import asyncio
import json
import sys
import os

# Add parent directory to path so app module can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scraper import open_jio_website

async def main():
    # Using the default test number
    test_number = "7869632727"
    print(f"Running scraper test for mobile: {test_number}")
    res = await open_jio_website(mobile=test_number, operator="Jio", circle="Madhya Pradesh & Chhattisgarh")
    print("\nFinal API Response:")
    print(json.dumps(res, indent=4))

if __name__ == "__main__":
    asyncio.run(main())
