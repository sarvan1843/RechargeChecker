import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.jio.com/selfcare/recharge/mobility/?entrysource=search')
        await page.wait_for_timeout(2000)
        
        await page.fill('input[type="tel"]', '7746815442')
        await page.wait_for_timeout(1000)
        
        # Click the correct button based on recent fix
        submit_btn = page.locator("button.j-button.primary").first
        await submit_btn.click()
        
        # Wait super long
        print("Waiting 15 seconds for plans to load...")
        await page.wait_for_timeout(15000)
        
        # Save screenshot
        await page.screenshot(path="jio_plans_7746815442_long_wait.png")
        
        # Check text
        body_text = await page.evaluate("document.body.innerText")
        print("Top-Up found:", "top-up" in body_text.lower() or "top up" in body_text.lower())
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
