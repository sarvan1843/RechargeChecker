import asyncio
from playwright.async_api import async_playwright, Page, BrowserContext, Browser

class SessionPool:
    def __init__(self):
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.pool: list[Page] = []
        self.lock = asyncio.Lock()
        self.p = None
        self.target_url = "https://rechargemojo.com/mobile-recharge/landing1?utm_source=google&utm_medium=cpc&utm_campaign=mobile&gad_source=1&gad_campaignid=19173133406&gbraid=0AAAAADDStxPCKz3b_qUlEy22ZYVaVEx3z&gclid=CjwKCAjwyabTBhBFEiwAM3mNUHdsi9q8f40wFFEDshgiQPxrvAZoxcta4ec26FszQA7vbc5IHaEN1BoCssEQAvD_BwE#currentSection="
        self.is_initializing = False

    async def start(self):
        async with self.lock:
            if self.browser:
                return
            self.is_initializing = True
            print("Initializing session pool browser...")
            self.p = await async_playwright().start()
            
            # Headless must always be True to avoid popping up 10 browser tabs on user screen
            self.browser = await self.p.chromium.launch(
                headless=True,
                args=[
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-gpu",
                ]
            )
            
            # Setup mobile emulation context (iPhone 12 Profile)
            iphone = self.p.devices['iPhone 12']
            self.context = await self.browser.new_context(
                **iphone,
                locale="en-US",
                geolocation={"longitude": 77.2090, "latitude": 28.6139},
                permissions=["geolocation"]
            )
            self.is_initializing = False
            print("Session pool context created successfully.")
            
        # Trigger background replenishment to fill up the pool
        asyncio.create_task(self.replenish())

    async def replenish(self):
        """
        Maintains exactly 10 pages in the background pool.
        """
        while True:
            await asyncio.sleep(0.5)
            if not self.browser or self.is_initializing:
                continue
                
            async with self.lock:
                pool_size = len(self.pool)
            
            if pool_size >= 10:
                continue
                
            print(f"Pool size: {pool_size}/10. Warming up new page session...")
            try:
                page = await self.context.new_page()
                # Block ads and telemetry trackers to save memory and network speed
                await page.route("**/*", self._block_unnecessary_resources)
                
                await page.goto(self.target_url, wait_until="domcontentloaded", timeout=45000)
                # Wait 2 seconds for client-side React bundles to parse
                await page.wait_for_timeout(2000)
                
                async with self.lock:
                    self.pool.append(page)
                print(f"Session warmed up and added to pool. New pool size: {len(self.pool)}")
            except Exception as e:
                print(f"Error warming up page in pool: {e}")

    async def get_page(self) -> Page:
        """
        Pops a pre-warmed page from the pool, or creates one on-the-fly if pool is empty.
        """
        # Make sure browser is started
        if not self.browser:
            await self.start()
            
        # Wait up to 10 seconds for a page from pool, else create one on the fly
        for _ in range(20):
            async with self.lock:
                if len(self.pool) > 0:
                    page = self.pool.pop(0)
                    print(f"Checked out page from pool. Remaining in pool: {len(self.pool)}")
                    # Trigger background replenishment
                    asyncio.create_task(self.replenish())
                    return page
            await asyncio.sleep(0.5)
            
        print("Pool empty. Creating a new page on-the-fly...")
        page = await self.context.new_page()
        await page.route("**/*", self._block_unnecessary_resources)
        await page.goto(self.target_url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(2000)
        return page

    async def _block_unnecessary_resources(self, route):
        url = route.request.url.lower()
        resource_type = route.request.resource_type
        
        is_tracking = any(pattern in url for pattern in [
            "google-analytics", "googletagmanager", "facebook", "hotjar",
            "doubleclick", "analytics", "telemetry", "tracking", "omni",
            "adservice", "partner"
        ])
        
        if resource_type in ["image", "media", "font"] or is_tracking:
            try:
                await route.abort()
            except Exception:
                pass
        else:
            try:
                await route.continue_()
            except Exception:
                pass

    async def close_all(self):
        """
        Safely closes all pages and browsers to prevent memory leaks.
        """
        async with self.lock:
            for page in self.pool:
                try:
                    await page.close()
                except Exception:
                    pass
            self.pool.clear()
            if self.context:
                try:
                    await self.context.close()
                except Exception:
                    pass
            if self.browser:
                try:
                    await self.browser.close()
                except Exception:
                    pass
            if self.p:
                try:
                    await self.p.stop()
                except Exception:
                    pass
            self.browser = None
            self.context = None
            self.p = None

# Global Singleton instance of SessionPool
session_pool = SessionPool()
