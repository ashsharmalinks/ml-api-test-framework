import logging, re
from .base_page import BasePage

log = logging.getLogger(__name__)

class LoginPage(BasePage):
    PATH = ""
    BTN_NAME = re.compile(r"(sign[- ]?in|log[- ]?in|submit)", re.I)

    def open(self): self.goto(self.PATH)

    def click_sign_in_button(self, timeout: int = 5000):
        btn = self.page.locator("#signin_button")
        try:
            btn.wait_for(state="visible", timeout=timeout)
        except Exception:
            btn = self.by_role("button", name=self.BTN_NAME).first
            if btn.count() == 0 or not btn.is_visible():
                btn = self.by_role("link", name=self.BTN_NAME).first
            btn.wait_for(state="visible", timeout=timeout)
        btn.click()
        log.info("✅ Clicked sign-in button.")

    def enter_credentials(self, username: str, password: str, timeout: int = 5000):
        self.fill("#user_login, [name='username'], [name='email']", username, timeout=timeout)
        self.fill("#user_password, [name='password']", password, timeout=timeout)
        log.info(f"🔐 Entered credentials for user: {username}")

    def submit(self):
        self.click(self.by_role("button", name=self.BTN_NAME).first)
