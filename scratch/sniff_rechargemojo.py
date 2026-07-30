"""
Test script to find rechargemojo.com's internal API endpoints
by intercepting all XHR/fetch requests made during number entry.
"""
import asyncio
import json
from playwright.async_api import async_playwright

MOBILE = "7869632727"

captured = []

async def on_response(response):
    url = response.url
    # Only capture JSON API calls (skip images, fonts, JS bundles, analytics)
    skip_domains = ["google", "facebook", "firebase", "doubleclick", "googleapis", "analytics", "gtm"]
    if any(d in url for d in skip_domains):
        return
    
    content_type = response.headers.get("content-type", "")
    if "json" in content_type or "application/json" in content_type:
        try:
            body = await response.json()
            entry = {
                "url": url,
                "status": response.status,
                "method": response.request.method,
                "body_snippet": json.dumps(body)[:500]
            }
            captured.append(entry)
            print(f"\n🎯 JSON API FOUND!")
            print(f"   URL: {url}")
            print(f"   Status: {response.status}")
            print(f"   Body: {json.dumps(body)[:400]}")
        except Exception:
            pass

async def run():
    print(f"Sniffing rechargemojo.com for JSON API calls...")
    
    iphone_12 = {
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "viewport": {"width": 390, "height": 844},
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**iphone_12)
        page = await context.new_page()
        
        page.on("response", on_response)
        
        url = "https://rechargemojo.com/mobile-recharge/landing1?utm_source=google&utm_medium=cpc&utm_campaign=mobile"
        print(f"Loading: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=40000)
        await page.wait_for_timeout(4000)
        
        print(f"\nEntering mobile number {MOBILE}...")
        try:
            tel_input = page.locator("input[type='tel']").first
            await tel_input.wait_for(timeout=8000)
            await tel_input.fill(MOBILE)
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"Input error: {e}")
        
        print(f"\n--- Total JSON APIs captured: {len(captured)} ---")
        for item in captured:
            print(f"\n  URL: {item['url']}")
            print(f"  Body: {item['body_snippet']}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
