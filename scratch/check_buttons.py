import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://www.jio.com/selfcare/recharge/mobility/?entrysource=search')
        await page.wait_for_timeout(3000)
        els = await page.locator('button.j-button.primary').evaluate_all('els => els.map(e => e.outerHTML)')
        for i, el in enumerate(els):
            print(f"Button {i}: {el[:100]}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
