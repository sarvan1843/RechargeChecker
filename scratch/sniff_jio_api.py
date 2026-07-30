import asyncio
import json
from playwright.async_api import async_playwright

captured_apis = []

async def on_response(response):
    url = response.url
    # Filter out static assets and known third-party tracking
    if any(ext in url for ext in [".js", ".css", ".png", ".jpg", ".svg", ".woff"]):
        return
    if any(domain in url for domain in ["google", "facebook", "doubleclick", "analytics", "tagmanager", "wzrkt", "clevertap", "firebaselogging"]):
        return
        
    content_type = response.headers.get("content-type", "")
    if "json" in content_type:
        try:
            body = await response.text()
            captured_apis.append({
                "url": url,
                "status": response.status,
                "method": response.request.method,
                "body_snippet": body[:500]
            })
            print(f"\n[API FOUND] {response.request.method} {url}")
            print(f"Status: {response.status}")
            print(f"Snippet: {body[:300]}")
        except Exception as e:
            pass

async def test_jio_api_sniff(mobile: str):
    print(f"\n=========================================")
    print(f"Sniffing APIs for Mobile: {mobile}")
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
                await page.wait_for_timeout(1000)
            else:
                print("Could not find input field!")
                return

            print("3. Clicking Submit...")
            submit_btn = page.locator("button:has-text('Continue')").first
            if await submit_btn.count() == 0:
                 submit_btn = page.locator("button:has-text('Submit')").first
                 
            if await submit_btn.count() > 0:
                await submit_btn.click()
            
            print("4. Waiting for APIs to fire (8 seconds)...")
            await page.wait_for_timeout(8000)
            
        except Exception as e:
            print(f"Exception during test: {e}")
            
        finally:
            await browser.close()

async def main():
    await test_jio_api_sniff("6266258150") # Non-Jio
    await test_jio_api_sniff("7869632727") # Jio

if __name__ == "__main__":
    asyncio.run(main())
