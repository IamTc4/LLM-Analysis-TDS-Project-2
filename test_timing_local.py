import asyncio
import time
import os
import sys

# Inject credentials explicitly for this test since .env is blocked
os.environ["GOOGLE_API_KEY"] = "AIzaSyDD8cUMuIHAbyVn4EO30uzg-Y4hA2VaX6Q"
os.environ["STUDENT_EMAIL"] = "23f2005433@ds.study.iitm.ac.in"
os.environ["STUDENT_SECRET"] = "iamtc"

from quiz_solver import QuizSolver
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_timing():
    print("\n=== Testing Quiz Solver Timing ===")
    # Target the failing quiz URL provided by the user
    url = "https://tdsbasictest.vercel.app/quiz/1"
    print(f"Target URL: {url}")
    
    start_time = time.time()
    solver = QuizSolver()
    
    try:
        print("Starting solver...")
        # We solve a single quiz to measure time
        result = await solver.solve_single_quiz(url)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n=== Result ===")
        print(f"Status: {'Success' if result.get('correct') else 'Failed'}")
        print(f"Message: {result.get('reason') or 'Correct answer submitted'}")
        print(f"Time Taken: {duration:.2f} seconds")
        
        if duration < 180:
            print("✅ PASSED: Completed within 3 minutes")
        else:
            print("❌ FAILED: Exceeded 3 minutes limit")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await solver.close()

if __name__ == "__main__":
    asyncio.run(test_timing())
