import asyncio
from playwright.async_api import async_playwright

async def run():
    print("Capturing mobikwik page screenshot...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Set a standard desktop viewport
        await page.set_viewport_size({"width": 1280, "height": 800})
        await page.goto("https://www.mobikwik.com/mobile-recharge", wait_until="networkidle", timeout=50000)
        await page.wait_for_timeout(5000)
        
        # Save screenshot
        screenshot_path = r"C:\Users\user\.gemini\antigravity\brain\0a83d257-ab78-4f4b-907f-a50aff0d0275\mobikwik_screenshot.png"
        await page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
        
        inputs = await page.locator("input").all()
        print(f"Found {len(inputs)} inputs:")
        for idx, inp in enumerate(inputs):
            visible = await inp.is_visible()
            placeholder = await inp.get_attribute("placeholder") or ""
            html = await inp.evaluate("el => el.outerHTML")
            print(f"[{idx}] Visible={visible}, Placeholder='{placeholder}' -> {html}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
