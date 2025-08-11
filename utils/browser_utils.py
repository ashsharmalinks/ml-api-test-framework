# utils/browser_utils.py
import os
from playwright.sync_api import sync_playwright

def prepare_browser(context):
    # Config via env (override with your config layer if you like)
    base_url = os.getenv("APP_BASE_URL", "http://zero.webappsecurity.com/")
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    browser_name = os.getenv("BROWSER", "chromium")  # chromium|firefox|webkit

    # Start Playwright once per run (if not already started)
    if not hasattr(context, "playwright") or context.playwright is None:
        context.playwright = sync_playwright().start()

    browser_factory = getattr(context.playwright, browser_name)
    context.browser = browser_factory.launch(headless=headless)

    # New isolated context + page per scenario
    context.browser_context = context.browser.new_context(base_url=base_url)
    context.page = context.browser_context.new_page()

def test_tracing(context, start: bool = True):
    """
    Start/stop Playwright tracing on the per-scenario browser context.
    Call test_tracing(context, True) in before_scenario if you want traces.
    """
    if start:
        if hasattr(context, "browser_context"):
            context.browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)
    else:
        try:
            if hasattr(context, "browser_context"):
                os.makedirs("artifacts/traces", exist_ok=True)
                context.browser_context.tracing.stop(path="artifacts/traces/trace.zip")
        except Exception:
            pass
