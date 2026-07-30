import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def check_number(mobile, operator):
    print(f"Testing number: {mobile} with operator {operator}...")
    screenshots_dir = Path(__file__).resolve().parent.parent / "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    async with async_playwright() as p:
        iphone = p.devices['iPhone 12']
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**iphone)
        page = await context.new_page()
        
        await page.goto("https://rechargemojo.com/mobile-recharge/landing1", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)
        
        # 1. Fill mobile
        mobile_input = page.locator("input[type='tel']").first
        await mobile_input.fill("")
        await mobile_input.type(mobile, delay=50)
        
        # 2. Select Operator
        select_el = page.locator("select").first
        await select_el.select_option(label=operator)
        
        await page.wait_for_timeout(2000)
        
        # Check if error message is visible on the landing page
        error_msg = ""
        try:
            # Let's see if there is any visible error text (like "Please enter a valid...")
            body_text = await page.locator("body").inner_text()
            print("Landing page body text status:")
            if "Please enter a valid" in body_text:
                print("Validation error text found in body!")
        except Exception:
            pass
            
        # 3. Click View Plans
        try:
            view_plans_btn = page.locator("text=/View Plans/i").first
            await view_plans_btn.click()
            await page.wait_for_timeout(5000)
            
            # Save screenshot
            filename = f"step3_plans_{mobile}.png"
            await page.screenshot(path=str(screenshots_dir / filename))
            print(f"Plans page screenshot saved to {filename}")
            
            body_text = await page.locator("body").inner_text()
            print(f"[{mobile}] Is 'Top Up' in plans page? {'Top Up' in body_text}")
            print(f"[{mobile}] Is 'Voice Only Plan' in plans page? {'Voice Only Plan' in body_text}")
            print(f"[{mobile}] Current Page URL: {page.url}")
            
        except Exception as e:
            print(f"Failed to load plans page for {mobile}: {e}")
            
        await browser.close()

async def main():
    # Test 1: Invalid number
    await check_number("1111111111", "Jio")
    print("-" * 50)
    # Test 2: Non-Jio (Airtel) number
    await check_number("9826012345", "Jio")

if __name__ == "__main__":
    asyncio.run(main())
