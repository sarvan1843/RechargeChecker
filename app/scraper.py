from playwright.async_api import async_playwright
import traceback

from app.logger import logger
from app.config import HEADLESS, SLOW_MO
from app.detector import detect_topup

print("########## NEW SCRAPER LOADED ##########")

async def open_jio_website(
    mobile=None,
    operator=None,
    circle=None,
):
    browser = None
    if mobile is None:
        mobile = "7869632727"

    print("=" * 60)
    print("STEP 1 : SCRAPER STARTED")
    print("=" * 60)
    print("Mobile   :", mobile)
    print("Operator :", operator)
    print("Circle   :", circle)

    logger.info("SCRAPER STARTED")

    try:
        async with async_playwright() as p:
            print("Launching Browser...")
            browser = await p.chromium.launch(
                headless=HEADLESS,
                slow_mo=SLOW_MO,
            )

            page = await browser.new_page(
                viewport={
                    "width": 1366,
                    "height": 768,
                }
            )

            print("Opening Jio Website...")
            await page.goto(
                "https://www.jio.com/selfcare/recharge/mobility/",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            print("Jio Page Opened")

            input_box = page.locator("#submitNumber")
            await input_box.wait_for(timeout=15000)
            print("Input Box Found")

            await input_box.fill("")
            await input_box.type(mobile, delay=100)
            print("Number Entered:", mobile)

            # Locate the Continue button
            continue_btn = page.locator('button[aria-label="Continue"]').first
            if await continue_btn.count() == 0:
                continue_btn = page.get_by_role("button", name="Continue")

            await continue_btn.wait_for(timeout=15000)
            print("Continue Button Found")

            await continue_btn.click()
            print("Continue Clicked. Waiting for recharge page...")

            # Wait for any of the category/plans selectors to appear (increased timeout to 60s)
            try:
                recharge_indicator = page.locator(
                    '[data-testid="desktopChangeCategory"], [data-testid="mobileChangeCategory"], .plans_roundedBoder__2CH9e'
                ).first
                await recharge_indicator.wait_for(timeout=60000)
                print("Recharge page detected successfully.")
            except Exception as e:
                print(f"Warning: Recharge page load indicator not found (Timeout). Continuing anyway... Error: {e}")

            print("Current URL:", page.url)
            print("Page Title:", await page.title())

            # Detect Top-up Voucher
            result = await detect_topup(page)

            topup_available = result["found"]
            detection_method = result["method"]
            confidence = result["confidence"]
            categories = result["categories"]

            print("\nDetector Result")
            print("----------------------")
            print("Topup      :", topup_available)
            print("Method     :", detection_method)
            print("Confidence :", confidence)
            print("Categories :", len(categories))

            # Save screenshot
            try:
                await page.screenshot(
                    path="screenshots/after_continue.png",
                    full_page=True,
                )
                print("Screenshot Saved to screenshots/after_continue.png")
            except Exception as e:
                print(f"Error saving screenshot: {e}")

            print("Closing Browser...")
            await browser.close()
            browser = None

            # Map the status to "Active" if topup is available, else "Expired" for Flutter compatibility
            status_value = "Active" if topup_available else "Expired"

            return {
                "success": True,
                "status": status_value,
                "mobile": mobile,
                "operator": operator,
                "circle": circle,
                "topupAvailable": topup_available,
                "detectionMethod": detection_method,
                "confidence": confidence,
                "categories": categories,
                "plan": "",
                "validity": "",
                "expiryDate": "",
                "message": f"Top-Up Check Completed (Status: {status_value})",
                "error": None,
            }

    except Exception as e:
        print("\n" + "=" * 80)
        print("SCRAPER ERROR:")
        traceback.print_exc()
        print("=" * 80)

        logger.exception("SCRAPER ERROR")

        if browser:
            try:
                await browser.close()
            except Exception:
                pass

        return {
            "success": False,
            "status": "Failed",
            "mobile": mobile,
            "operator": operator,
            "circle": circle,
            "topupAvailable": False,
            "detectionMethod": "",
            "confidence": 0,
            "categories": [],
            "plan": "",
            "validity": "",
            "expiryDate": "",
            "message": "Scraper Failed",
            "error": str(e),
        }