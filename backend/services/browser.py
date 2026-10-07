import base64
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

    async def _describe_elements(self, page: Page) -> list[dict[str, str]]:
        return await page.locator("button, a, input, textarea, select").evaluate_all(
            """els => els.slice(0, 80).map(e => ({
                tag: e.tagName.toLowerCase(),
                text: (e.innerText || e.getAttribute('aria-label') || e.getAttribute('placeholder') || e.value || '').trim().slice(0,160),
                selector: e.id ? '#' + CSS.escape(e.id) :
                    e.getAttribute('name') ? e.tagName.toLowerCase() + '[name="' + CSS.escape(e.getAttribute('name')) + '"]' :
                    e.tagName.toLowerCase() + ':nth-of-type(' + (Array.from(e.parentElement.children).indexOf(e)+1) + ')'
            }))"""
        )

    async def snapshot(self, include_screenshot: bool = False) -> dict[str, Any]:
        page = await self.page()
        result: dict[str, Any] = {
            "url": page.url,
            "title": await page.title(),
            "text": (await page.locator("body").inner_text())[:12000],
            "elements": await self._describe_elements(page),
        }
        if include_screenshot:
            result["screenshot_base64"] = await self.screenshot_base64()
        return result

    async def screenshot_base64(self) -> str:
        page = await self.page()
        data = await page.screenshot(type="jpeg", quality=55)
        return base64.b64encode(data).decode("ascii")

    def _locator(self, page: Page, selector: str):
        if selector.startswith("text="):
            return page.get_by_text(selector[5:], exact=False).first
        if selector.startswith("role="):
            role, _, name = selector[5:].partition("|")
            return page.get_by_role(role, name=name or None).first
        if selector.startswith("placeholder="):
            return page.get_by_placeholder(selector[12:], exact=False).first
        if selector.startswith("label="):
            return page.get_by_label(selector[6:], exact=False).first
        return page.locator(selector).first

    async def click(self, selector: str) -> dict[str, Any]:
        page = await self.page()
        await self._locator(page, selector).click()
        return await self.snapshot()

    async def fill(self, selector: str, value: str) -> dict[str, Any]:
        page = await self.page()
        await self._locator(page, selector).fill(value)
        return await self.snapshot()

    async def close(self) -> None:
        await self.stop()
