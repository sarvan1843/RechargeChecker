import asyncio
from playwright.async_api import async_playwright
import json

async def run():
    print("Sniffing Mobikwik ROffer / Plans API...")
    async with async_playwright() as p:
        # Use iPhone to avoid desktop complex UI
        iphone_12 = p.devices['iPhone 12']
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**iphone_12)
        page = await context.new_page()
        
        captured = []
        
        def on_response(response):
            if "mobikwik" in response.url and ("plan" in response.url or "offer" in response.url or "operator" in response.url):
                asyncio.create_task(save_response(response))
                
        async def save_response(response):
            try:
                body = await response.text()
                if "{" in body:
                    captured.append({
                        "url": response.url,
                        "body": body[:500]
                    })
            except:
                pass
                
        page.on("response", on_response)
        
        print("Opening Mobikwik recharge page...")
        await page.goto("https://www.mobikwik.com/mobile-recharge", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        print("Finding input field...")
        # Since it's mobile view, input might be standard
        inputs = await page.locator("input").all()
        for i, inp in enumerate(inputs):
            ph = await inp.get_attribute("placeholder")
            print(f"Input {i}: placeholder={ph}")
            if ph and ("number" in ph.lower() or "mobile" in ph.lower()):
                await inp.fill("7869632727")
                print("Filled mobile number.")
                break
                
        await page.wait_for_timeout(5000)
        
        print(f"Captured {len(captured)} potential API responses:")
        for c in captured:
            print(f"URL: {c['url']}")
            print(f"Body: {c['body']}\n")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
