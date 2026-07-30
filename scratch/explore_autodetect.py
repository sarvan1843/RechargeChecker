import asyncio
from playwright.async_api import async_playwright

async def check_autodetect(mobile):
    print(f"Testing auto-detection for mobile: {mobile}...")
    async with async_playwright() as p:
        iphone = p.devices['iPhone 12']
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**iphone)
        page = await context.new_page()
        
        await page.goto("https://rechargemojo.com/mobile-recharge/landing1", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # Fill mobile
        mobile_input = page.locator("input[type='tel']").first
        await mobile_input.fill("")
        await mobile_input.type(mobile, delay=50)
        
        # Wait 3 seconds for dynamic auto-detection API requests to resolve
        await page.wait_for_timeout(3000)
        
        # Read the value of select element
        select_el = page.locator("select").first
        selected_value = await select_el.evaluate("el => el.value")
        # Try to find selected option text
        selected_text = await select_el.evaluate("""el => {
            const opt = el.options[el.selectedIndex];
            return opt ? opt.text : '';
        }""")
        
        print(f"[{mobile}] Detected Operator Value: {selected_value}, Text: {selected_text}")
        await browser.close()

async def main():
    # Test 1: Jio prepaid number
    await check_autodetect("7869632727")
    print("-" * 50)
    # Test 2: Airtel number
    await check_autodetect("9826012345")
    print("-" * 50)
    # Test 3: Invalid number
    await check_autodetect("1111111111")

if __name__ == "__main__":
    asyncio.run(main())
