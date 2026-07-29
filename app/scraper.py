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
            print("Launching Browser with cloud optimizations...")
            # Optimized arguments for low-resource environments (Docker/Render free tier)
            browser_args = [
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-gpu",
                "--no-first-run",
                "--no-zygote",
                "--single-process",  # Dramatically reduces RAM by keeping all tabs in a single process
                "--disable-extensions",
            ]

            browser = await p.chromium.launch(
                headless=HEADLESS,
                slow_mo=SLOW_MO,
                args=browser_args,
            )

            page = await browser.new_page(
                viewport={
                    "width": 1366,
                    "height": 768,
                }
            )

            # Block heavy assets (images, media, fonts) to save network bandwidth and memory (speeds up loading by 3x)
            async def block_unnecessary_resources(route):
                if route.request.resource_type in ["image", "media", "font"]:
                    try:
                        await route.abort()
                    except Exception:
                        pass
                else:
                    try:
                        await route.continue_()
                    except Exception:
                        pass

            await page.route("**/*", block_unnecessary_resources)

            # Navigate directly to plans page bypassing first page inputs (Speeds up scraping by 3x)
            plans_url = f"https://www.jio.com/selfcare/recharge/mobility/plans/?serviceId={mobile}&serviceType=mobility&next=PREPAID&billingType=PREPAID"
            print("Navigating directly to plans page:", plans_url)
            await page.goto(
                plans_url,
                wait_until="domcontentloaded",
                timeout=25000,
            )
            print("Direct Plans Page Loaded. Waiting for selectors or redirect validation...")

            # Wait for either the plan category headers to appear, or for the site to redirect back to edit page (non-Jio number)
            try:
                await page.wait_for_function(
                    """() => {
                        const plans = document.querySelector('[data-testid="desktopChangeCategory"], [data-testid="mobileChangeCategory"], .plans_roundedBoder__2CH9e');
                        const errorMsg = document.body.innerText.match(/not a Jio|valid Jio|Enter a valid/i);
                        const isRedirected = window.location.href.includes('/mobility/?') || window.location.href.includes('action=edit') || window.location.href.includes('serviceId=');
                        
                        // We are done waiting if plans container is loaded, or if validation error/redirect occurs
                        if (plans && plans.offsetHeight > 0) return true;
                        if (errorMsg) return true;
                        
                        // If it redirected back to edit page without query serviceId or with edit action
                        if (window.location.href.includes('action=edit') || (!window.location.href.includes('/plans/') && window.location.href.includes('/mobility/'))) {
                            return true;
                        }
                        return false;
                    }""",
                    timeout=15000
                )
            except Exception as wait_err:
                print(f"Wait helper timeout or warning: {wait_err}")

            current_url = page.url
            print("Page URL after resolution:", current_url)

            # Check if we were redirected back or error is present (indicates invalid/non-Jio number)
            if "plans" not in current_url or "action=edit" in current_url or "/mobility/?" in current_url:
                print("Validation redirect detected. Mobile number is invalid or non-Jio.")
                err_txt = "Invalid/Non-Jio Number"
                try:
                    non_jio_error = page.locator("text=/not a Jio|valid Jio|Enter a valid/i").first
                    if await non_jio_error.is_visible(timeout=2000):
                        err_txt = await non_jio_error.inner_text()
                except Exception:
                    pass

                await browser.close()
                return {
                    "success": True,
                    "status": "Non-Jio",
                    "mobile": mobile,
                    "operator": operator,
                    "circle": circle,
                    "topupAvailable": False,
                    "message": "Non-Jio Number",
                    "error": err_txt
                }

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

            # Save screenshot (optional, catch error if image rendering blocked)
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