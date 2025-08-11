# ui/pages/base_page.py
from __future__ import annotations
import re, time
from pathlib import Path
from typing import Optional, Union
from contextlib import suppress
from playwright.sync_api import Page, Locator, expect, TimeoutError as PWTimeoutError

Selector = Union[str, Locator]

class BasePage:
    """Reusable base for all Page Objects."""

    def __init__(self, page: Page, base_url: str, default_timeout: int = 5000):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.default_timeout = default_timeout
        self.page.set_default_timeout(default_timeout)

    # ---------- navigation ----------
    def goto(self, path: str, wait_until: str = "domcontentloaded") -> None:
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        self.page.goto(url, wait_until=wait_until)

    def wait_for_url_contains(self, fragment: str, timeout: Optional[int] = None) -> None:
        expect(self.page).to_have_url(re.compile(re.escape(fragment)), timeout=timeout or self.default_timeout)

    def wait_for_idle(self, state: str = "networkidle", timeout: Optional[int] = None) -> None:
        self.page.wait_for_load_state(state, timeout=timeout or self.default_timeout)

    # ---------- locator helpers ----------
    def by_test_id(self, test_id: str) -> Locator:
        return self.page.get_by_test_id(test_id)

    def by_role(self, role: str, name: Optional[Union[str, re.Pattern]] = None) -> Locator:
        if isinstance(name, str):
            name = re.compile(rf"^{re.escape(name)}$", re.I)
        return self.page.get_by_role(role, **({"name": name} if name is not None else {}))

    def by_label(self, label: Union[str, re.Pattern]) -> Locator:
        if isinstance(label, str):
            label = re.compile(rf"^{re.escape(label)}$", re.I)
        return self.page.get_by_label(label)

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def _as_locator(self, target: Selector) -> Locator:
        return target if isinstance(target, Locator) else self.page.locator(target)

    # ---------- safe actions ----------
    def click(self, target: Selector, timeout: Optional[int] = None, retries: int = 1) -> None:
        timeout = timeout or self.default_timeout
        loc = self._as_locator(target).first
        try:
            expect(loc).to_be_visible(timeout=timeout)
            expect(loc).to_be_enabled(timeout=timeout)
            loc.click()
        except Exception as e:
            if retries > 0:
                with suppress(Exception):
                    loc.scroll_into_view_if_needed()
                time.sleep(0.2)
                return self.click(loc, timeout=timeout, retries=retries - 1)
            raise e

    def fill(self, target: Selector, value: str, timeout: Optional[int] = None) -> None:
        timeout = timeout or self.default_timeout
        loc = self._as_locator(target).first
        try:
            expect(loc).to_be_visible(timeout=timeout)
        except PWTimeoutError:
            with suppress(Exception):
                loc.scroll_into_view_if_needed()
            expect(loc).to_be_visible(timeout=timeout)
        loc.fill(value)

    def type(self, target: Selector, value: str, delay_ms: int = 0, timeout: Optional[int] = None) -> None:
        timeout = timeout or self.default_timeout
        loc = self._as_locator(target).first
        expect(loc).to_be_visible(timeout=timeout)
        loc.type(value, delay=delay_ms)

    # ---------- assertions / content ----------
    def heading_visible(self, text_or_regex: Union[str, re.Pattern], timeout: Optional[int] = None) -> None:
        timeout = timeout or self.default_timeout
        regex = text_or_regex if isinstance(text_or_regex, re.Pattern) else re.compile(rf"^{re.escape(text_or_regex)}$", re.I)
        self.page.get_by_role("heading", name=regex).wait_for(timeout=timeout)

    def expect_visible(self, target: Selector, timeout: Optional[int] = None) -> None:
        expect(self._as_locator(target).first).to_be_visible(timeout=timeout or self.default_timeout)

    def text_of(self, target: Selector) -> str:
        return self._as_locator(target).first.inner_text().strip()

    def count(self, target: Selector) -> int:
        return self._as_locator(target).count()

    # ---------- section utilities (great for summaries) ----------
    def first_following_container_of_heading(self, exact_text: str) -> Locator:
        h = self.page.get_by_role("heading", name=re.compile(rf"^{re.escape(exact_text)}$", re.I))
        return h.locator("xpath=following-sibling::*[1]")

    def count_items_with_text(self, container: Locator, pattern: re.Pattern) -> int:
        items = container.locator("li")
        if items.count() > 0:
            return items.filter(has_text=pattern).count()
        rows = container.locator("tbody tr")
        if rows.count() > 0:
            return rows.filter(has_text=pattern).count()
        return container.locator("*").filter(has_text=pattern).count()

    # ---------- diagnostics ----------
    def screenshot(self, name: str = "page", full_page: bool = True, into: str = "artifacts/screenshots") -> Path:
        Path(into).mkdir(parents=True, exist_ok=True)
        path = Path(into) / f"{name}.png"
        self.page.screenshot(path=str(path), full_page=full_page)
        return path

    def assert_nav_links_work(self, nav_role: str = "navigation") -> None:
        nav = self.page.get_by_role(nav_role)
        links = nav.locator('a[href]:not([href^="#"])')
        total = links.count()
        assert total > 0, "No navigation links found"
        for i in range(total):
            href = links.nth(i).get_attribute("href")
            assert href and href.strip(), "Empty href in navigation link"
            url = href if re.match(r"^https?://", href, re.I) else f"{self.base_url}/{href.lstrip('/')}"
            resp = self.page.request.get(url)
            assert resp.ok, f"Broken nav link: {href} -> HTTP {resp.status}"
