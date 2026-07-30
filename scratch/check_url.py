import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Loading Jio recharge page...")
        await page.goto('https://www.jio.com/selfcare/recharge/mobility/?entrysource=search')
        await page.wait_for_timeout(3000)
        
        print("Filling mobile number...")
        await page.fill('input[type="tel"]', '7746815442')
        await page.wait_for_timeout(1000)
        
        print("Clicking submit...")
        await page.locator('button.j-button.primary').first.click()
        await page.wait_for_timeout(5000)
        
        print("URL after submit:", page.url)
        
        # also print visible text
        print("Visible text:")
        print(await page.locator('body').inner_text())
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
