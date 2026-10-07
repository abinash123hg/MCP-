from pathlib import Path
from typing import Any
from playwright.async_api import async_playwright, BrowserContext, Page

class BrowserService:
    def __init__(self, headless: bool = True, timeout_ms: int = 15000):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self._pw = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def start(self) -> None:
        if self._context:
            return
        self._pw = await async_playwright().start()
        profile = Path("data/browser-profile")
        profile.mkdir(parents=True, exist_ok=True)
        self._context = await self._pw.chromium.launch_persistent_context(
            str(profile), headless=self.headless, viewport={"width": 1440, "height": 900}
        )
        self._context.set_default_timeout(self.timeout_ms)
        self._page = self._context.pages[0] if self._context.pages else await self._context.new_page()

    async def stop(self) -> None:
        if self._context:
            await self._context.close()
        if self._pw:
            await self._pw.stop()
        self._pw = self._context = self._page = None

    async def page(self) -> Page:
        await self.start()
        assert self._page is not None
        return self._page

    async def open(self, url: str) -> dict[str, Any]:
        page = await self.page()
        await page.goto(url, wait_until="domcontentloaded")
        return await self.snapshot()

    async def snapshot(self) -> dict[str, Any]:
        page = await self.page()
        title = await page.title()
        text = (await page.locator("body").inner_text())[:12000]
        return {"url": page.url, "title": title, "text": text}

    async def click(self, selector: str) -> dict[str, Any]:
        page = await self.page()
        await page.locator(selector).first.click()
        return await self.snapshot()

    async def fill(self, selector: str, value: str) -> dict[str, Any]:
        page = await self.page()
        await page.locator(selector).first.fill(value)
        return await self.snapshot()

    async def close(self) -> None:
        await self.stop()
