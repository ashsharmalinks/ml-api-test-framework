# Make sure pytest imports your step module so the decorators register
pytest_plugins = ['tests.ui_bdd.steps.login_steps']

from pytest_bdd import scenarios
scenarios("features/login.feature")  # path is relative to this file
