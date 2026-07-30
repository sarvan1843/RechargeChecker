"""
Test the full rechargemojo.com API flow:
1. Get guest token
2. Detect operator/circle from mobile number
3. Fetch plans
4. Check if Top Up category exists
"""
import asyncio
import json
from playwright.async_api import async_playwright

MOBILE = "7869632727"

async def on_response(response):
    url = response.url
    skip = ["google", "facebook", "firebase", "doubleclick", "analytics", "gtm", "clarity", "hotjar"]
    if any(d in url for d in skip):
        return
    content_type = response.headers.get("content-type", "")
    if "json" in content_type:
        try:
            body = await response.json()
            print(f"\n🎯 JSON: {url}")
            print(f"   Body: {json.dumps(body)[:600]}")
        except Exception:
            pass

async def run():
    print("=== Phase 1: Full Flow Sniff ===")
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
        await page.goto(url, wait_until="domcontentloaded", timeout=40000)
        await page.wait_for_timeout(3000)
        
        # Enter number
        print(f"\nEntering {MOBILE}...")
        tel = page.locator("input[type='tel']").first
        await tel.wait_for(timeout=8000)
        await tel.fill("")
        await tel.type(MOBILE, delay=100)
        await page.wait_for_timeout(3000)
        
        # Click Prepaid
        print("\nSelecting Prepaid...")
        prepaid = page.locator("input[value='prepaid']").first
        if await prepaid.count() > 0:
            await prepaid.click()
        await page.wait_for_timeout(1000)
        
        # Select Jio
        print("\nSelecting Jio...")
        sel = page.locator("select").first
        if await sel.count() > 0:
            await sel.select_option(label="Jio")
        await page.wait_for_timeout(1000)
        
        # Click View Plans
        print("\nClicking View Plans...")
        btn = page.locator("text=/View Plans/i").first
        if await btn.count() > 0:
            await btn.click()
        await page.wait_for_timeout(8000)
        
        await browser.close()
        print("\n=== Sniff Complete ===")

if __name__ == "__main__":
    asyncio.run(run())
