# tests/ui_bdd/features/environment.py  (your version + small hardening)
import os, datetime, configparser
import allure
from behave.runner import Context
from behavex_images import image_attachments
from behavex_images.image_attachments import AttachmentsCondition
from playwright.sync_api import Page
from utils.browser_utils import prepare_browser, test_tracing
from helpers.constants.framework_constants import FrameworkConstants as Fc
from utils.elk import add_in_elk
from utils.helper_utils import read_file
from utils.reporting.logger import get_logs
from utils.reporting.screenshots import attach_screenshot_in_report
from contextlib import suppress

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]   # ...\ml-api-test-framework
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def before_all(context: Context):
    current_time = datetime.datetime.now()
    file_name = current_time.strftime("%d_%m_%y-%H_%M_%S_%f")[:-3]
    context.base_url = os.getenv("APP_BASE_URL", "http://zero.webappsecurity.com/")
    context.username = os.getenv("APP_USERNAME", "username")
    context.password = os.getenv("APP_PASSWORD", "password")
    global logger
    # Ensure dirs exist
    os.makedirs(Fc.logs_dir, exist_ok=True)
    os.makedirs(Fc.screenshots_dir, exist_ok=True)
    logger = get_logs(f"{Fc.logs_dir}/{file_name}.txt")

    image_attachments.set_attachments_condition(context, AttachmentsCondition.ALWAYS)
    context.details = configparser.ConfigParser()
    context.details.read(Fc.details_file)
    context.base_url = context.base_url if hasattr(context, "base_url") else "http://zero.webappsecurity.com/"


def before_feature(context: Context, feature):
    logger.info(f"Feature file: {feature.filename}")
    logger.info(f"Number of Scenarios: {len(feature.scenarios)}")
    formatted_tags = " ".join([f"@{tag}" for tag in feature.tags])
    if formatted_tags:
        logger.info(f"{formatted_tags}")
    logger.info(f"Feature: {feature.name}")

def before_scenario(context, scenario):
    formatted_tags = " ".join([f"@{tag}" for tag in scenario.tags])
    if formatted_tags:
        logger.info(f"{formatted_tags}")
    logger.info(f"Scenario: {scenario.name}")

    if scenario.feature.background:
        for step in scenario.feature.background.steps:
            logger.info(f"{step.keyword} {step.name}")

    for step in scenario.steps:
        logger.info(f"{step.keyword} {step.name}")

    prepare_browser(context)          # <-- creates context.playwright/browser/browser_context/page
    test_tracing(context, True)
    context.pages = {} # optional: start tracing

def after_step(context: Context, step):
    # If you prefer only-on-failure, check: if step.status == "failed":
    current_time = datetime.datetime.now()
    file_name = current_time.strftime("%d_%m_%y-%H_%M_%S_%f")[:-3]
    page: Page = context.page
    page.wait_for_load_state()
    png_path = f"{Fc.screenshots_dir}/{file_name}.png"
    page.screenshot(path=png_path)
    attach_screenshot_in_report(png_path)
    image_attachments.attach_image_file(context, png_path)

def _elk_enabled(ctx) -> bool:
    try:
        return (
            getattr(ctx, "details", None)
            and ctx.details.has_section("elk")
            and ctx.details.getboolean("elk", "enabled", fallback=False)
        )
    except Exception:
        return False
def after_scenario(context, scenario):
    # ---- summary fields up front (usable even if something fails later)
    test_id = " ".join([tag for tag in scenario.tags])
    summary = str(scenario.name).split("--")[0].strip()
    status = str(scenario.status).split(".")[-1].capitalize()
    author = "user_1"

    # ---- logging
    with suppress(Exception):
        logger.info(f"Scenario status: {scenario.status}")

    # ---- stop tracing (if you started it in before_scenario)
    with suppress(Exception):
        test_tracing(context, False)

    # ---- optional ELK (guarded; called ONCE)
    if _elk_enabled(context):
        with suppress(Exception) as _:
            add_in_elk(context, logger, test_id, summary, status, author)
    else:
        with suppress(Exception):
            logger.info("ELK disabled or no [elk] section; skipping push.")

    # ---- optional Allure dynamics (guarded)
    with suppress(Exception):
        import allure
        allure.dynamic.title(scenario.name)
        allure.dynamic.link("https://www.link.com", test_id)
        allure.dynamic.issue(f"https://www.issue.com/{test_id}", test_id)
        allure.dynamic.testcase(f"https://www.testcase.com/{test_id}", test_id)

    # ---- ALWAYS cleanup (in order)
    with suppress(Exception):
        if getattr(context, "page", None):
            context.page.close()
    with suppress(Exception):
        if getattr(context, "browser_context", None):
            context.browser_context.close()
    with suppress(Exception):
        if getattr(context, "browser", None):
            context.browser.close()
    with suppress(Exception):
        if getattr(context, "playwright", None):
            context.playwright.stop()
def after_feature(context, feature):
    logger.info(f"Feature Status: {feature.status}")
