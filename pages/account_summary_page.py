import re
from .base_page import BasePage

SAVINGS = re.compile(r"\bsavings?\b", re.I)
BROKERAGE = re.compile(r"\bbrokerage\b", re.I)

class AccountSummaryPage(BasePage):
    TITLE = "Account Summary"

    def visible(self): self.heading_visible(self.TITLE)

    def cash_savings_count_is(self, expected: int):
        container = self.first_following_container_of_heading("Cash Accounts")
        assert container.count() > 0, "Cash Accounts section not found"
        actual = self.count_items_with_text(container, SAVINGS)
        assert actual == expected, f"Expected {expected} savings accounts, found {actual}"

    def investment_brokerage_count_is(self, expected: int):
        container = self.first_following_container_of_heading("Investment Accounts")
        assert container.count() > 0, "Investment Accounts section not found"
        actual = self.count_items_with_text(container, BROKERAGE)
        assert actual == expected, f"Expected {expected} brokerage accounts, found {actual}"

    def navigation_links_work(self):
        self.assert_nav_links_work()
