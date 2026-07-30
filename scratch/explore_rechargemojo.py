import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def run():
    print("Starting rechargemojo mobile exploration...")
    screenshots_dir = Path(__file__).resolve().parent.parent / "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    async with async_playwright() as p:
        # Use iPhone 12 mobile profile
        iphone = p.devices['iPhone 12']
        browser = await p.chromium.launch(headless=True)
        
        print("Creating mobile context...")
        context = await browser.new_context(
            **iphone,
            locale="en-US",
            geolocation={"longitude": 77.2090, "latitude": 28.6139}, # New Delhi
            permissions=["geolocation"]
        )
        
        page = await context.new_page()
        target_url = "https://rechargemojo.com/mobile-recharge/landing1"
        print(f"Navigating to {target_url}...")
        
        await page.goto(target_url, wait_until="domcontentloaded", timeout=40000)
        await page.wait_for_timeout(3000) # Wait for client scripts
        
        screenshot_path = screenshots_dir / "rechargemojo_mobile.png"
        await page.screenshot(path=str(screenshot_path))
        print(f"Mobile screenshot saved to {screenshot_path}")
        
        print("\n--- INPUT FIELDS ---")
        inputs = await page.locator("input").all()
        for idx, inp in enumerate(inputs):
            inp_id = await inp.get_attribute("id")
            placeholder = await inp.get_attribute("placeholder")
            inp_type = await inp.get_attribute("type")
            name = await inp.get_attribute("name")
            value = await inp.get_attribute("value")
            print(f"Input {idx}: id={inp_id}, placeholder={placeholder}, type={inp_type}, name={name}, value={value}")
            
        print("\n--- SELECT FIELDS ---")
        selects = await page.locator("select").all()
        for idx, sel in enumerate(selects):
            sel_id = await sel.get_attribute("id")
            name = await sel.get_attribute("name")
            print(f"Select {idx}: id={sel_id}, name={name}")
            
        print("\n--- BUTTONS ---")
        buttons = await page.locator("button").all()
        for idx, btn in enumerate(buttons):
            text = await btn.inner_text()
            btn_id = await btn.get_attribute("id")
            btn_class = await btn.get_attribute("class")
            print(f"Button {idx}: text={text.strip()}, id={btn_id}, class={btn_class}")

        print("\n--- LINKS & SPANS (View Plans etc.) ---")
        anchors = await page.locator("a").all()
        for idx, a in enumerate(anchors):
            text = await a.inner_text()
            href = await a.get_attribute("href")
            print(f"Link {idx}: text={text.strip()}, href={href}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
