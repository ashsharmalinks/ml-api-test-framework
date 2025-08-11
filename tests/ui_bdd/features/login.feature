Feature: Login and Account Summary Verification
  As a user
  I want to verify the login functionality and account summary
  So that I can access my account and perform transactions

  @ui
  Scenario: Successful login and account summary verification
    Given I open the login page
    And I have clicked the sign-in button
    When I enter valid credentials
#    Then I should be redirected to the account summary page
#    Then the account summary should have Cash Accounts with two savings accounts
#    Then all naviagtion links should be working on account summary page
