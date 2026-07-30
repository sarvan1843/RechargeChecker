import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def run():
    print("Starting fill exploration on rechargemojo...")
    screenshots_dir = Path(__file__).resolve().parent.parent / "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    async with async_playwright() as p:
        iphone = p.devices['iPhone 12']
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            **iphone,
            locale="en-US",
            geolocation={"longitude": 77.2090, "latitude": 28.6139},
            permissions=["geolocation"]
        )
        
        page = await context.new_page()
        # Enable console log forwarding
        page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
        
        target_url = "https://rechargemojo.com/mobile-recharge/landing1"
        print(f"Navigating to {target_url}...")
        await page.goto(target_url, wait_until="domcontentloaded", timeout=40000)
        await page.wait_for_timeout(3000)
        
        # Step 1: Fill Mobile Number
        print("Locating mobile input field...")
        mobile_input = page.locator("input[type='tel']").first
        await mobile_input.wait_for(timeout=10000)
        await mobile_input.click()
        await mobile_input.fill("")
        await mobile_input.type("7869632727", delay=100)
        print("Mobile number filled.")
        
        # Take a screenshot after entering number
        await page.screenshot(path=str(screenshots_dir / "step1_entered_number.png"))
        
        # Step 2: Open Operator Dropdown and select Jio
        print("Locating operator select/dropdown...")
        # Let's inspect options inside select first
        select_locator = page.locator("select")
        select_count = await select_locator.count()
        print(f"Number of select elements found: {select_count}")
        
        if select_count > 0:
            select_el = select_locator.first
            try:
                # Click select element to trigger any custom overlays or let standard select work
                print("Clicking select dropdown...")
                await select_el.click()
                await page.wait_for_timeout(1000)
                await page.screenshot(path=str(screenshots_dir / "step2_dropdown_clicked.png"))
                
                # Check for custom mobile overlay options (like Jio in a modal)
                # In custom select popups, let's see if we can find text containing "Jio"
                jio_option = page.locator("text=/^Jio$/i").first
                if await jio_option.count() > 0 and await jio_option.is_visible():
                    print("Found custom overlay option for Jio! Clicking it...")
                    await jio_option.click()
                else:
                    print("Custom overlay option not visible. Attempting direct select_option...")
                    # Fallback to standard option selection
                    await select_el.select_option(label="Jio")
                    
                print("Operator selected.")
            except Exception as e:
                print(f"Select interaction warning: {e}")
        
        await page.wait_for_timeout(2000)
        await page.screenshot(path=str(screenshots_dir / "step2_operator_selected.png"))
        
        # Step 3: Click View Plans button
        print("Searching for View Plans button...")
        try:
            view_plans_btn = page.locator("text=/View Plans/i").first
            await view_plans_btn.wait_for(timeout=10000)
            print("View Plans button found! Clicking...")
            await view_plans_btn.click()
            
            # Wait for plans page to render
            print("Waiting for plans page content to load...")
            await page.wait_for_timeout(6000)
            await page.screenshot(path=str(screenshots_dir / "step3_plans_page.png"))
            
            # Explore plans page categories
            print("Exploring plans page text elements...")
            body_text = await page.locator("body").inner_text()
            print(f"Is 'Top Up' in plans page body? {'Top Up' in body_text}")
            print(f"Is 'Popular' in plans page body? {'Popular' in body_text}")
            print(f"Is 'Smart Phone' in plans page body? {'Smart Phone' in body_text}")
            
            # Print unique elements on the plans page
            headers = await page.locator("h1, h2, h3").all_texts()
            print("Page Headers found:", headers)
            
        except Exception as e:
            print(f"Failed to load plans page: {e}")
            
        await browser.close()
        print("Exploration completed.")

if __name__ == "__main__":
    asyncio.run(run())
