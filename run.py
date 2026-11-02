"""
SHEVAULT AI - Main Application Runner
Starts the Uvicorn ASGI server hosting the SHEVAULT AI platform.
"""
import os
import sys
import uvicorn

def main():
    print("=" * 60)
    print(" [SHEVAULT AI] - Digital Trust & Identity Protection")
    print("=" * 60)
    print(" Platform: SHEVAULT AI")
    print(" Core Promise: 'Verify first. Protect your identity. Participate safely.'")
    print(" Access URL: http://127.0.0.1:8000")
    print("=" * 60)
    
    uvicorn.run(
        "backend.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
