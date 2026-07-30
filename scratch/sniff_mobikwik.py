import asyncio
from playwright.async_api import async_playwright

async def print_request(request):
    resource_type = request.resource_type
    if resource_type in ["fetch", "xhr"]:
        print(f"\n[REQUEST] {request.method} -> {request.url}")
        if request.post_data:
            print(f"Post Data: {request.post_data}")

async def print_response(response):
    resource_type = response.request.resource_type
    if resource_type in ["fetch", "xhr"]:
        print(f"\n[RESPONSE] Status: {response.status} -> {response.url}")
        try:
            body = await response.text()
            print(f"Content (snippet): {body[:600]}")
        except Exception as e:
            pass

async def run():
    print("Starting improved network sniffer...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        page.on("request", lambda req: asyncio.create_task(print_request(req)))
        page.on("response", lambda res: asyncio.create_task(print_response(res)))

        target_url = "https://www.mobikwik.com/mobile-recharge"
        print(f"Navigating to {target_url}...")
        await page.goto(target_url, wait_until="domcontentloaded", timeout=40000)
        await page.wait_for_timeout(4000)
        
        print("Typing mobile number 7869632727...")
        # Target the input field
        inputs = await page.locator("input").all()
        for inp in inputs:
            placeholder = await inp.get_attribute("placeholder") or ""
            inp_type = await inp.get_attribute("type") or ""
            if "mobile" in placeholder.lower() or "number" in placeholder.lower() or inp_type in ["tel", "text"]:
                await inp.click()
                await inp.fill("")
                await inp.type("7869632727", delay=100)
                print(f"Typed in: placeholder='{placeholder}', type='{inp_type}'")
                break
                
        # Wait 10 seconds for dynamic API fetches to resolve
        await page.wait_for_timeout(10000)
        await browser.close()
        print("Sniffer finished.")

if __name__ == "__main__":
    asyncio.run(run())
