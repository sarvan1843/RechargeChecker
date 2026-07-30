import asyncio
import json
from playwright.async_api import async_playwright

captured_apis = []

async def on_response(response):
    url = response.url
    if "api" in url.lower() and "jio" in url.lower():
        try:
            body = await response.text()
            if "top" in body.lower() or "plan" in body.lower() or "service" in body.lower():
                print(f"\n[API FOUND] {response.request.method} {url}")
                print(f"Snippet: {body[:500]}")
        except:
            pass

async def test_jio_api_sniff(mobile: str):
    print(f"\n=========================================")
    print(f"Sniffing Plans API for Mobile: {mobile}")
    print(f"=========================================")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**p.devices['iPhone 12'])
        page = await context.new_page()
        page.on("response", on_response)
        
        try:
            print("1. Opening Jio Selfcare URL...")
            await page.goto("https://www.jio.com/selfcare/recharge/mobility/?entrysource=search", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            print("2. Entering mobile number...")
            input_locator = page.locator("input[type='tel']").first
            if await input_locator.count() == 0:
                input_locator = page.locator("input[name='jioNumber']").first
                
            if await input_locator.count() > 0:
                await input_locator.click()
                await input_locator.fill(mobile)
            else:
                return

            print("3. Clicking Submit...")
            submit_btn = page.locator("button:has-text('Continue')").first
            if await submit_btn.count() == 0:
                 submit_btn = page.locator("button:has-text('Submit')").first
                 
            if await submit_btn.count() > 0:
                await submit_btn.click()
            
            print("4. Waiting for APIs to fire (15 seconds)...")
            await page.wait_for_timeout(15000)
            
        except Exception as e:
            pass
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_jio_api_sniff("7869632727"))
