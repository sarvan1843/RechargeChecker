import asyncio
from app.scraper import open_jio_website

async def test():
    print("Running scraper test locally...")
    result = await open_jio_website(
        mobile="7869632727",
        operator="Jio",
        circle="Madhya Pradesh"
    )
    print("Scraper Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(test())
