from playwright.async_api import Page, TimeoutError

async def detect_topup(page: Page):
    """
    Detect Top-up Voucher using multiple fallback methods based on priority.
    Includes container and button scrolling to ensure all items are loaded and visible.
    """
    desktop_categories = []
    mobile_categories = []
    categories = []
    method = ""
    confidence = 0
    found = False

    print("\n========== TOP-UP DETECTOR ==========\n")

    # 1. Desktop Category Extraction & Scrolling
    try:
        desktop_container = page.locator('[data-testid="desktopChangeCategory"]')
        if await desktop_container.count() > 0:
            print("Scrolling Desktop Category Container...")
            # Scroll container to trigger lazy loading of tab items
            container_handle = await desktop_container.element_handle()
            if container_handle:
                # Scroll right/down to the end
                await page.evaluate('(elem) => { elem.scrollLeft = elem.scrollWidth; elem.scrollTop = elem.scrollHeight; }', container_handle)
                await page.wait_for_timeout(300)
                # Scroll back to start
                await page.evaluate('(elem) => { elem.scrollLeft = 0; elem.scrollTop = 0; }', container_handle)
                await page.wait_for_timeout(300)
            
            desktop_buttons = desktop_container.locator('button')
            count = await desktop_buttons.count()
            for i in range(count):
                btn = desktop_buttons.nth(i)
                try:
                    # Scroll individual button into view
                    await btn.scroll_into_view_if_needed()
                except Exception:
                    pass
                label = await btn.get_attribute("aria-label")
                text = await btn.inner_text()
                cat_name = (label or text or "").strip()
                if cat_name and cat_name not in desktop_categories:
                    desktop_categories.append(cat_name)
            print(f"Extracted Desktop Categories: {desktop_categories}")
    except Exception as e:
        print(f"Error extracting desktop categories: {e}")

    # 2. Mobile Category Extraction & Scrolling
    try:
        mobile_container = page.locator('[data-testid="mobileChangeCategory"]')
        if await mobile_container.count() > 0:
            print("Scrolling Mobile Category Container...")
            container_handle = await mobile_container.element_handle()
            if container_handle:
                # Scroll right/down to the end
                await page.evaluate('(elem) => { elem.scrollLeft = elem.scrollWidth; elem.scrollTop = elem.scrollHeight; }', container_handle)
                await page.wait_for_timeout(300)
                # Scroll back to start
                await page.evaluate('(elem) => { elem.scrollLeft = 0; elem.scrollTop = 0; }', container_handle)
                await page.wait_for_timeout(300)

            mobile_buttons = mobile_container.locator('button')
            count = await mobile_buttons.count()
            for i in range(count):
                btn = mobile_buttons.nth(i)
                try:
                    # Scroll individual button into view
                    await btn.scroll_into_view_if_needed()
                except Exception:
                    pass
                label = await btn.get_attribute("aria-label")
                text = await btn.inner_text()
                cat_name = (label or text or "").strip()
                if cat_name and cat_name not in mobile_categories:
                    mobile_categories.append(cat_name)
            print(f"Extracted Mobile Categories: {mobile_categories}")
    except Exception as e:
        print(f"Error extracting mobile categories: {e}")

    # Combine categories list (retains order, removes duplicates)
    categories = list(dict.fromkeys(desktop_categories + mobile_categories))

    # 3. Priority-based Detection logic

    # Priority 1: Desktop Category Buttons
    if not found:
        print("Checking Priority 1: Desktop Category Buttons...")
        if "Top-up Voucher" in desktop_categories:
            found = True
            method = "Desktop Category Buttons"
            confidence = 100
            print("Priority 1 Match Found!")

    # Priority 2: Mobile Category
    if not found:
        print("Checking Priority 2: Mobile Category...")
        if "Top-up Voucher" in mobile_categories:
            found = True
            method = "Mobile Category"
            confidence = 90
            print("Priority 2 Match Found!")

    # Priority 3: Playwright get_by_text
    if not found:
        try:
            print("Checking Priority 3: Playwright get_by_text...")
            locator = page.get_by_text("Top-up Voucher")
            count = await locator.count()
            if count > 0:
                visible = False
                for i in range(count):
                    # Attempt to scroll it into view to verify visibility
                    btn = locator.nth(i)
                    try:
                        await btn.scroll_into_view_if_needed()
                    except Exception:
                        pass
                    if await btn.is_visible():
                        visible = True
                        break
                if visible:
                    found = True
                    method = "Playwright get_by_text"
                    confidence = 80
                    print("Priority 3 Match Found!")
        except Exception as e:
            print(f"Priority 3 Detection Error: {e}")

    # Priority 4: Body Text Search
    if not found:
        try:
            print("Checking Priority 4: Body Text Search...")
            body_locator = page.locator("body")
            if await body_locator.count() > 0:
                body_text = await body_locator.inner_text()
                if "Top-up Voucher" in body_text:
                    found = True
                    method = "Body Text Search"
                    confidence = 60
                    print("Priority 4 Match Found!")
        except Exception as e:
            print(f"Priority 4 Detection Error: {e}")

    # Priority 5: HTML Search
    if not found:
        try:
            print("Checking Priority 5: HTML Search...")
            html_content = await page.content()
            if 'aria-label="Top-up Voucher"' in html_content or "Top-up Voucher" in html_content:
                found = True
                method = "HTML Search"
                confidence = 40
                print("Priority 5 Match Found!")
        except Exception as e:
            print(f"Priority 5 Detection Error: {e}")

    print("\n========== RESULT ==========")
    print("Found      :", found)
    print("Method     :", method)
    print("Confidence :", confidence)
    print("Categories :", categories)
    print("============================\n")

    return {
        "found": found,
        "method": method,
        "confidence": confidence,
        "categories": categories
    }