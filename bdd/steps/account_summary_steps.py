from pytest_bdd import given, when, then

# NOTE: Your feature has a typo "naviagtion".
# We bind both spellings to the same function for now.

@given("I open the login page")
def open_login(login_page):
    login_page.open()

@given("I have clicked the sign-in button")
def click_sign_in(login_page):
    login_page.click_sign_in_button()

@when("I enter valid credentials")
def enter_valid_creds(login_page, creds):
    login_page.fill_credentials_and_submit(creds["username"], creds["password"])

@then("I should be redirected to the account summary page")
def on_summary(account_summary_page):
    account_summary_page.visible()

@then("the account summary should have Cash Accounts with two savings accounts")
def cash_two(account_summary_page):
    account_summary_page.cash_savings_count_is(2)

@then("all naviagtion links should be working on account summary page")
@then("all navigation links should be working on account summary page")
def nav_links(account_summary_page):
    account_summary_page.navigation_links_work()

@then("the account summary should have Investment Accounts with one brokerage account")
def brokerage_one(account_summary_page):
    account_summary_page.investment_brokerage_count_is(1)
