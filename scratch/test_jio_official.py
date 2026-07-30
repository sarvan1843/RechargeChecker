import asyncio
from playwright.async_api import async_playwright

async def test_jio_number(mobile: str):
    print(f"\n=========================================")
    print(f"Testing Mobile Number: {mobile}")
    print(f"=========================================")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**p.devices['iPhone 12'])
        page = await context.new_page()
        
        try:
            print("1. Opening Jio Selfcare URL...")
            await page.goto("https://www.jio.com/selfcare/recharge/mobility/?entrysource=search", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            print("2. Looking for mobile number input field...")
            input_locator = page.locator("input[type='tel']").first
            if await input_locator.count() == 0:
                input_locator = page.locator("input[name='jioNumber']").first
                
            if await input_locator.count() > 0:
                await input_locator.click()
                await input_locator.fill(mobile)
            else:
                print("Could not find input field!")
                return

            print("3. Clicking Submit...")
            submit_btn = page.locator("button:has-text('Continue')").first
            if await submit_btn.count() == 0:
                 submit_btn = page.locator("button:has-text('Submit')").first
                 
            if await submit_btn.count() > 0:
                await submit_btn.click()
            
            print("4. Waiting for loader to disappear and plans to load...")
            # Wait a bit longer to ensure it goes past the spinner
            await page.wait_for_timeout(10000)
            
            # Check if error exists
            body_text = await page.locator("body").inner_text()
            
            if "not a Jio number" in body_text.lower() or "invalid" in body_text.lower():
                print("=> RESULT: Error detected on page!")
            else:
                print("=> RESULT: No error. Plans loaded.")
            
            # Save screenshot
            screenshot_path = f"scratch/jio_test_{mobile}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"Saved screenshot to {screenshot_path}")
            
        except Exception as e:
            print(f"Exception during test: {e}")
            
        finally:
            await browser.close()

async def main():
    await test_jio_number("7869632727") # Jio
    await test_jio_number("8103557998") # Non-Jio

if __name__ == "__main__":
    asyncio.run(main())
