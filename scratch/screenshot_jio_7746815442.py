import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Using the exact same context settings as scraper.py
        context = await browser.new_context(
            viewport={'width': 375, 'height': 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()
        print("Navigating to Jio...")
        await page.goto("https://www.jio.com/selfcare/recharge/mobility/?entrysource=search")
        
        print("Entering mobile number 7746815442...")
        input_locator = page.locator("input[type='tel']").first
        if await input_locator.count() == 0:
            input_locator = page.locator("input[name='jioNumber']").first
            
        await input_locator.click()
        await input_locator.fill("7746815442")
        await page.wait_for_timeout(500)
        
        print("Clicking submit...")
        submit_btn = page.locator("button:has-text('Continue')").first
        if await submit_btn.count() == 0:
             submit_btn = page.locator("button:has-text('Submit')").first
        if await submit_btn.count() == 0:
             submit_btn = page.locator("button.j-button.primary").first
             
        await submit_btn.click()
        
        print("Waiting 10 seconds for plans to load...")
        await page.wait_for_timeout(10000)
        
        print("Taking screenshot...")
        await page.screenshot(path="jio_plans_7746815442.png", full_page=True)
        
        html = await page.content()
        with open("jio_plans_7746815442.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        # extract body text the same way scraper.py does
        body_text = await page.evaluate("document.body.innerText")
        body_text_lower = body_text.lower()
        
        topup_found = "top-up" in body_text_lower or "top up" in body_text_lower
        print(f"Top-Up found in body text: {topup_found}")
        
        print("Done.")
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
