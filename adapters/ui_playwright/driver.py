# adapters/ui_playwright/driver.py
from playwright.sync_api import sync_playwright
from core.config import settings

class UiSession:
    def __init__(self):
        self._pw = sync_playwright().start()
        browser = getattr(self._pw, settings.browser)
        self.browser = browser.launch(headless=settings.headless)
        self.ctx = self.browser.new_context(base_url=str(settings.base_url))
        self.page = self.ctx.new_page()

    def close(self):
        self.ctx.close()
        self.browser.close()
        self._pw.stop()
