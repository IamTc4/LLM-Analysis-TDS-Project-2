# ⏱️ Verifying Quiz Solving Time (3-Minute Limit)

Since the local test failed (likely due to an invalid local OpenAI API key), we must verify the timing on Render, where the service is working correctly.

## How to Check Timing on Render

1. **Go to Render Dashboard**: [https://dashboard.render.com](https://dashboard.render.com)
2. **Select your service**: `llm-analysis-tds-project-2-2`
3. **Click "Logs"**
4. **Trigger a Quiz**:
   Run this command in your terminal:
   ```powershell
   powershell -ExecutionPolicy Bypass -File test_all_quizzes.ps1
   ```
5. **Watch the Logs**:
   Look for these two messages and note the timestamps:

   **Start Time:**
   ```
   [INFO] Starting quiz chain from https://...
   ```

   **End Time:**
   ```
   [INFO] Quiz chain completed successfully
   ```
   *(Or "Quiz chain stopped: timeout exceeded" if it failed)*

## Calculation

**Duration = End Time - Start Time**

- ✅ **Pass**: Duration < 3 minutes (180 seconds)
- ❌ **Fail**: Duration > 3 minutes

## Example Log

```
Nov 29 02:30:00 PM  [INFO] Starting quiz chain from https://tds-llm-analysis.s-anand.net/demo
... (logs of solving) ...
Nov 29 02:31:15 PM  [INFO] Quiz chain completed successfully
```

**Result**: 1 minute 15 seconds. **PASSED** ✅

---

## Why Local Test Failed?

The local script `test_timing_local.py` failed with `401 Unauthorized` from OpenAI. This means the `OPENAI_API_KEY` in your local `.env` file is likely invalid, expired, or different from the one on Render.

Since Render is working (status 200 OK), the key on Render is valid. Trust the Render logs for the final verification.
