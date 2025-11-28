"""Quiz solver using Playwright and OpenAI."""
import asyncio
import json
import logging
import re
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError
import httpx
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

import config
from data_processor import DataProcessor
from prompts import (
    QUIZ_SOLVER_SYSTEM_PROMPT,
    CODE_GENERATION_PROMPT,
    ANSWER_EXTRACTION_PROMPT
)

logger = logging.getLogger(__name__)

class QuizError(Exception):
    """Base exception for quiz solving errors."""
    pass

class NetworkError(QuizError):
    """Network related errors."""
    pass

class ExtractionError(QuizError):
    """Data extraction errors."""
    pass

def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

class QuizSolver:
    """Solve quiz tasks using browser automation and LLM."""
    
    def __init__(self):
        genai.configure(api_key=config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        self.data_processor = DataProcessor()
        self.start_time: Optional[datetime] = None
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close async resources."""
        await self.http_client.aclose()
    
    def _is_timeout_exceeded(self) -> bool:
        """Check if 3-minute timeout has been exceeded."""
        if not self.start_time:
            return False
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed > config.QUIZ_TIMEOUT_SECONDS
    
    async def solve_quiz_chain(self, initial_url: str):
        """
        Solve a chain of quizzes starting from the initial URL.
        
        Args:
            initial_url: Starting quiz URL
        """
        self.start_time = datetime.now()
        current_url = initial_url
        attempt_count = 0
        
        logger.info(f"Starting quiz chain from {initial_url}")
        
        while current_url and not self._is_timeout_exceeded():
            try:
                logger.info(f"Solving quiz at {current_url}")
                result = await self.solve_single_quiz(current_url)
                
                if result.get("correct"):
                    logger.info(f"✓ Correct answer for {current_url}")
                    current_url = result.get("url")  # Get next quiz URL
                    attempt_count = 0  # Reset attempts for new quiz
                else:
                    logger.warning(f"✗ Wrong answer for {current_url}: {result.get('reason')}")
                    attempt_count += 1
                    
                    # Check if we should retry or move to next
                    next_url = result.get("url")
                    if next_url and next_url != current_url:
                        # New quiz provided, move to it
                        logger.info(f"Moving to next quiz: {next_url}")
                        current_url = next_url
                        attempt_count = 0
                    elif attempt_count >= config.MAX_RETRIES:
                        logger.error(f"Max retries exceeded for {current_url}")
                        break
                    # else: retry the same quiz
                
            except Exception as e:
                logger.error(f"Error solving quiz {current_url}: {e}", exc_info=True)
                break
        
        await self.close()
        
        if self._is_timeout_exceeded():
            logger.warning("Quiz chain stopped: timeout exceeded")
        else:
            logger.info("Quiz chain completed successfully")
    
    async def solve_single_quiz(self, quiz_url: str) -> Dict[str, Any]:
        """
        Solve a single quiz with Playwright and fallback to HTTPX.
        
        Args:
            quiz_url: URL of the quiz
            
        Returns:
            Response from submission endpoint
        """
        content = ""
        page = None
        playwright = None
        browser = None
        
        # Try Playwright first
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            
            logger.info(f"Loading quiz page with Playwright: {quiz_url}")
            await page.goto(quiz_url, timeout=config.BROWSER_TIMEOUT_MS)
            await page.wait_for_load_state("networkidle")
            
            # Get rendered HTML content
            content = await page.content()
            logger.info(f"Playwright loaded content, length: {len(content)}")
            
        except Exception as e:
            logger.error(f"Playwright failed: {e}. Falling back to HTTPX.")
            # Fallback to HTTPX
            try:
                response = await self.http_client.get(quiz_url)
                content = response.text
                logger.info(f"HTTPX loaded content, length: {len(content)}")
            except Exception as e2:
                logger.error(f"Fallback HTTPX failed: {e2}")
                if browser: await browser.close()
                if playwright: await playwright.stop()
                raise NetworkError(f"Failed to load quiz: {e} -> {e2}")

        try:
            # Extract quiz information using LLM (passing HTML content)
            quiz_info = self._extract_quiz_info(content)
            logger.info(f"Extracted quiz info: {quiz_info}")
            
            # Solve the quiz
            answer = await self._solve_quiz(quiz_info, page)
            logger.info(f"Generated answer: {answer}")
            
            # Submit the answer
            result = await self._submit_answer(
                quiz_info["submit_url"],
                quiz_url,
                answer
            )
            
            return result
            
        finally:
            if browser: await browser.close()
            if playwright: await playwright.stop()
                
    async def _navigate_to_quiz(self, page: Page, url: str) -> None:
        """Navigate to quiz page with retries."""
        for attempt in range(config.MAX_RETRIES):
            try:
                logger.info(f"Loading quiz page: {url} (Attempt {attempt + 1})")
                await page.goto(url, timeout=config.BROWSER_TIMEOUT_MS)
                await page.wait_for_load_state("networkidle")
                return
            except PlaywrightTimeoutError:
                logger.warning(f"Timeout loading {url}, retrying...")
                if attempt == config.MAX_RETRIES - 1:
                    raise NetworkError(f"Failed to load {url} after retries")
            except Exception as e:
                logger.error(f"Navigation error: {e}")
                raise NetworkError(f"Navigation failed: {e}")
    
    def _extract_quiz_info(self, content: str) -> Dict[str, Any]:
        """
        Extract quiz information from page content using LLM.
        
        Args:
            content: Page text content
            
        Returns:
            Dictionary with question, answer_type, data_sources, submit_url
        """
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You extract structured information from quiz questions. Return valid JSON only."},
                    {"role": "user", "content": ANSWER_EXTRACTION_PROMPT.format(content=content[:4000])}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"LLM extracted quiz info: {result}")
            
            # Validate extracted submit URL
            submit_url = result.get("submit_url", "")
            if submit_url and not validate_url(submit_url):
                logger.warning(f"Invalid submit URL extracted: {submit_url}")
                result["submit_url"] = ""
            
            return result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            raise ExtractionError("Invalid JSON from LLM")
        except Exception as e:
            logger.error(f"Error extracting quiz info: {e}")
            # Fallback: try to extract submit URL manually
            submit_url_match = re.search(r'https://[^\s<>"]+/submit', content)
            
            # Fallback: extract question from <div id="result"> or similar if LLM fails
            question_match = re.search(r'<div id="result">(.*?)</div>', content, re.DOTALL)
            question = question_match.group(1).strip() if question_match else content[:1000]
            
            submit_url = submit_url_match.group(0) if submit_url_match else ""
            if not submit_url or not validate_url(submit_url):
                logger.warning("Could not find valid submit URL in fallback mode")
                submit_url = ""
            
            return {
                "question": question,
                "answer_type": "string",
                "data_sources": [],
                "submit_url": submit_url
            }
    
    async def _solve_quiz(self, quiz_info: Dict[str, Any], page: Optional[Page] = None) -> Any:
        """
        Solve the quiz using LLM to generate and execute code.
        
        Args:
            quiz_info: Extracted quiz information
            page: Playwright page object
            
        Returns:
            The answer to submit
        """
        question = quiz_info["question"]
        answer_type = quiz_info.get("answer_type", "string")
        
        # Generate solution code using LLM
        code = self._generate_solution_code(question)
        
        # Execute the code safely
        answer = self._execute_solution_code(code, quiz_info)
        
        # Format answer based on type
        return self._format_answer(answer, answer_type)
    
    def _generate_solution_code(self, question: str) -> str:
        """
        Generate Python code to solve the quiz using LLM.
        
        Args:
            question: The quiz question
            
        Returns:
            Python code as string
        """
        try:
            # Call Gemini API
            response = self.model.generate_content(
                f"{QUIZ_SOLVER_SYSTEM_PROMPT}\n\n{CODE_GENERATION_PROMPT.format(question=question)}",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2
                )
            )
            
            code = response.text
            
            # Extract code from markdown if present
            if "```python" in code:
                code = re.search(r'```python\n(.*?)```', code, re.DOTALL).group(1)
            elif "```" in code:
                code = re.search(r'```\n(.*?)```', code, re.DOTALL).group(1)
            
            logger.info(f"Generated code:\n{code}")
            return code
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return "answer = None"
    
    def _execute_solution_code(self, code: str, quiz_info: Dict[str, Any]) -> Any:
        """
        Execute the generated solution code safely.
        
        Args:
            code: Python code to execute
            quiz_info: Quiz information
            
        Returns:
            The answer variable from executed code
        """
        # Create safe execution environment
        safe_globals = {
            "requests": requests,  # Keep requests for generated code compatibility if needed, or prefer httpx
            "httpx": httpx,
            "pd": __import__("pandas"),
            "np": __import__("numpy"),
            "BeautifulSoup": __import__("bs4").BeautifulSoup,
            "data_processor": self.data_processor,
            "json": json,
            "re": re,
            "base64": __import__("base64"),
        }
        
        safe_locals = {}
        
        try:
            exec(code, safe_globals, safe_locals)
            answer = safe_locals.get("answer")
            logger.info(f"Code executed successfully, answer: {answer}")
            return answer
        except Exception as e:
            logger.error(f"Error executing code: {e}", exc_info=True)
            # Fallback: try to answer with LLM directly
            return self._llm_direct_answer(quiz_info["question"])
    
    def _llm_direct_answer(self, question: str) -> str:
        """
        Get direct answer from LLM without code execution.
        
        Args:
            question: The quiz question
            
        Returns:
            Direct answer
        """
        try:
            response = self.model.generate_content(
                f"{QUIZ_SOLVER_SYSTEM_PROMPT}\n\nAnswer this question directly, return only the answer:\n{question}",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error getting direct answer: {e}")
            return ""
    
    def _format_answer(self, answer: Any, answer_type: str) -> Any:
        """
        Format answer based on expected type.
        
        Args:
            answer: Raw answer
            answer_type: Expected type (number, string, boolean, file, json)
            
        Returns:
            Formatted answer
        """
        if answer is None:
            return None
        
        if answer_type == "number":
            try:
                return float(answer) if '.' in str(answer) else int(answer)
            except:
                return answer
        elif answer_type == "boolean":
            if isinstance(answer, bool):
                return answer
            if isinstance(answer, str):
                return answer.lower().strip() in ['true', 'yes', '1']
            return bool(answer)
        elif answer_type == "json":
            if isinstance(answer, (dict, list)):
                return answer
            try:
                return json.loads(answer)
            except:
                return answer
        else:
            if isinstance(answer, str):
                return answer.strip()
            return answer
    
    async def _submit_answer(self, submit_url: str, quiz_url: str, answer: Any) -> Dict[str, Any]:
        """
        Submit answer to the endpoint asynchronously.
        
        Args:
            submit_url: Submission endpoint URL
            quiz_url: Original quiz URL
            answer: The answer to submit
            
        Returns:
            Response from server
        """
        payload = {
            "email": config.STUDENT_EMAIL,
            "secret": config.STUDENT_SECRET,
            "url": quiz_url,
            "answer": answer
        }
        
        # Validate payload size (1MB limit per problem statement)
        payload_json = json.dumps(payload)
        payload_size = len(payload_json.encode('utf-8'))
        if payload_size > 1_000_000:  # 1MB = 1,000,000 bytes
            logger.error(f"Payload too large: {payload_size:,} bytes (limit: 1,000,000)")
            return {
                "correct": False,
                "reason": f"Answer payload exceeds 1MB limit ({payload_size:,} bytes)"
            }
        
        logger.info(f"Submitting answer to {submit_url} (payload size: {payload_size:,} bytes)")

        
        for attempt in range(3):
            try:
                response = await self.http_client.post(
                    submit_url,
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                logger.info(f"Submission response: {result}")
                return result
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error submitting answer (Attempt {attempt+1}): {e.response.text}")
                if attempt == 2:
                    return {"correct": False, "reason": f"HTTP {e.response.status_code}"}
            except Exception as e:
                logger.error(f"Error submitting answer (Attempt {attempt+1}): {e}")
                if attempt == 2:
                    return {"correct": False, "reason": str(e)}
            
            # Wait before retry
            await asyncio.sleep(1)
            
        return {"correct": False, "reason": "Submission failed after retries"}
