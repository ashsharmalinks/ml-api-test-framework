from behave import given, when, then
import re
from pages.login_page import LoginPage
from pages.account_summary_page import AccountSummaryPage

@given("I open the login page")
def open_login(context):
    context.pages["login"] = LoginPage(context.page, context.base_url)
    context.pages["login"].open()

@given("I have clicked the sign-in button")
def click_sign_in(context):
    context.pages["login"].click_sign_in_button(timeout=5000)

@when("I enter valid credentials")
def enter_valid_creds(context):
    context.pages["login"].enter_credentials(context.username, context.password)
    context.pages["login"].submit()

@then("I should be redirected to the account summary page")
def on_summary(context):
    context.pages["summary"] = AccountSummaryPage(context.page, context.base_url)
    context.pages["summary"].visible()

@then("the account summary should have Cash Accounts with two savings accounts")
def cash_two(context):
    context.pages["summary"].cash_savings_count_is(2)

@then("all naviagtion links should be working on account summary page")
@then("all navigation links should be working on account summary page")
def nav_links(context):
    context.pages["summary"].navigation_links_work()

@then("the account summary should have Investment Accounts with one brokerage account")
def brokerage_one(context):
    context.pages["summary"].investment_brokerage_count_is(1)
