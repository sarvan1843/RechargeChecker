import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 375, 'height': 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()
        await page.goto("https://www.jio.com/selfcare/recharge/mobility/?entrysource=search")
        await page.wait_for_timeout(3000)
        
        body_text = await page.evaluate("document.body.innerText")
        print("top-up" in body_text.lower() or "top up" in body_text.lower())
        
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
