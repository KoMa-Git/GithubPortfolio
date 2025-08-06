import pytest
import allure

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to take a screenshot when a test fails.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver", None)
        if driver:
            screenshot_path = f"screenshots/{item.name}.png"
            driver.save_screenshot(screenshot_path)
            allure.attach.file(screenshot_path, name="Screenshot", attachment_type=allure.attachment_type.PNG)
