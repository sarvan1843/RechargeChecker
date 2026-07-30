import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to Jio...")
        await page.goto("https://www.jio.com/selfcare/recharge/mobility/?entrysource=search")
        
        print("Entering mobile number...")
        await page.fill('input[type="tel"]', "7869632727")
        
        print("Clicking submit...")
        submit_btn = page.locator('button.j-button.j-button-size__medium.primary').first
        await submit_btn.click()
        
        print("Waiting 10 seconds for plans to load...")
        await page.wait_for_timeout(10000)
        
        print("Taking screenshot...")
        await page.screenshot(path="jio_plans_7869632727.png", full_page=True)
        
        html = await page.content()
        with open("jio_plans_7869632727.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        print("Done. Screenshot saved as jio_plans_7869632727.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
