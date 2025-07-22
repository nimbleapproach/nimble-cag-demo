#!/usr/bin/env python3
"""
Simple test runner for the CAG API
Usage: python run_tests.py [--api-url http://localhost:8000] [--timeout 300]
"""

import sys
import os
import argparse
from test_api import test_api_integration


def main():
    parser = argparse.ArgumentParser(description="Run CAG API tests")
    parser.add_argument("--api-url", default="http://localhost:8000", 
                       help="API URL to test (default: http://localhost:8000)")
    parser.add_argument("--timeout", type=int, default=300,
                       help="Timeout in seconds (default: 300)")
    
    args = parser.parse_args()
    
    # Set environment variables for tests
    os.environ["TEST_API_URL"] = args.api_url
    os.environ["TEST_TIMEOUT"] = str(args.timeout)
    
    print(f"🧪 Testing CAG API at {args.api_url}")
    print(f"⏱️  Timeout: {args.timeout} seconds")
    print("=" * 50)
    
    try:
        test_api_integration()
        print("\n✅ All tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 