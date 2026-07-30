import asyncio
from app.logger import logger
from app.pool import session_pool

print("########## NEW SCRAPER ENGINE LOADED ##########")

async def open_jio_website(
    mobile=None,
    operator=None,
    circle=None,
):
    if mobile is None:
        mobile = "7869632727"

    print("=" * 60)
    print("NEW SCRAPER ENGINE INITIATED")
    print(f"Mobile   : {mobile}")
    print(f"Operator : {operator}")
    print(f"Circle   : {circle}")
    print("=" * 60)

    # Checked out pre-warmed page session from the background pool
    page = await session_pool.get_page()
    
    try:
        # Step 1: Fill Mobile Number
        print("Entering mobile number...")
        mobile_input = page.locator("input[type='tel']").first
        await mobile_input.wait_for(timeout=10000)
        await mobile_input.fill("")
        await mobile_input.type(mobile, delay=50)
        
        # Step 2: Select Prepaid
        print("Selecting Prepaid...")
        prepaid_radio = page.locator("input[value='prepaid']").first
        if await prepaid_radio.count() > 0:
            is_checked = await prepaid_radio.is_checked()
            if not is_checked:
                await prepaid_radio.click()
                
        # Step 3: Select operator Jio from select dropdown
        print("Selecting operator Jio...")
        select_el = page.locator("select").first
        if await select_el.count() > 0:
            await select_el.select_option(label="Jio")
            
        # Step 4: Click View Plans and wait for plans page
        print("Clicking View Plans...")
        view_plans_btn = page.locator("text=/View Plans/i").first
        await view_plans_btn.wait_for(timeout=10000)
        await view_plans_btn.click()
        
        # Wait for plans categories tab to appear in the DOM (timeout 20s)
        await page.wait_for_selector("text=/Popular/i", timeout=20000)
        print("Plans page loaded successfully.")
        
        # Step 5: Check if 'Top Up' is present in plans page body
        body_text = await page.locator("body").inner_text()
        topup_found = "Top Up" in body_text
        print(f"Top Up category found: {topup_found}")
        
        status = "Active" if topup_found else "Expired"
        message = "Recharge Active" if topup_found else "Recharge Expired"
        
        return {
            "success": True,
            "status": status,
            "mobile": mobile,
            "operator": operator,
            "circle": circle,
            "topupAvailable": topup_found,
            "message": message,
            "error": None
        }
        
    except Exception as e:
        print(f"Verification workflow failed: {e}")
        return {
            "success": False,
            "status": "error",
            "mobile": mobile,
            "operator": operator,
            "circle": circle,
            "topupAvailable": False,
            "message": str(e),
            "error": str(e)
        }
    finally:
        # Close page session to release memory and trigger pool replenishment
        try:
            await page.close()
        except Exception:
            pass
        # Replenish pool in the background
        asyncio.create_task(session_pool.replenish())