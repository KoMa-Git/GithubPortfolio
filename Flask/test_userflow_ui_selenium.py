import pytest
import allure
from allure_commons.types import Severity
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

@pytest.fixture(scope="function")
def driver(request):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    
    # Ensure screenshots folder exists
    os.makedirs("screenshots", exist_ok=True)
    
    yield driver

    driver.quit()


BASE_URL = "http://127.0.0.1:5000"
TEST_EMAIL = "test@example.com"
TEST_NAME = "Test User"
TEST_PASSWORD = "password123"

def wait_for(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def wait_and_click(driver, by, value, timeout=10):
    elem = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
    elem.click()

@allure.severity(Severity.CRITICAL)
@allure.title("Register New User")
def test_register(driver):
    with allure.step("Open Register Page"):
        driver.get(f"{BASE_URL}/register")

    with allure.step("Fill and Submit Registration Form"):
        wait_for(driver, By.NAME, "email").send_keys(TEST_EMAIL)
        wait_for(driver, By.NAME, "nm").send_keys(TEST_NAME)
        wait_for(driver, By.NAME, "pwd").send_keys(TEST_PASSWORD)
        wait_and_click(driver, By.NAME, "submit")

    with allure.step("Check if redirected to Login"):
        time.sleep(1)
        assert "login" in driver.current_url

@allure.severity(Severity.CRITICAL)
@allure.title("Login with Valid Credentials")
def test_login(driver):
    with allure.step("Open Login Page"):
        driver.get(f"{BASE_URL}/login")

    with allure.step("Enter Credentials and Submit"):
        wait_for(driver, By.NAME, "email").send_keys(TEST_EMAIL)
        wait_for(driver, By.NAME, "pwd").send_keys(TEST_PASSWORD)
        wait_and_click(driver, By.NAME, "submit")

    with allure.step("Check if redirected to User Page"):
        time.sleep(1)
        assert "/user" in driver.current_url

@allure.severity(Severity.NORMAL)
@allure.title("Change User Name")
def test_change_name(driver):
    test_login(driver)

    with allure.step("Change Name on User Page"):
        wait_and_click(driver, By.NAME, "chng_nm_btn")
        wait_for(driver, By.NAME, "nm").clear()
        wait_for(driver, By.NAME, "nm").send_keys("New Name")
        wait_and_click(driver, By.NAME, "chng_nm_btn")

    with allure.step("Verify Name Changed"):
        time.sleep(1)
        body_text = driver.page_source
        assert "New name was saved" in body_text

@allure.severity(Severity.NORMAL)
@allure.title("Change Password and Reset It Back")
def test_change_password(driver):
    test_login(driver)

    with allure.step("Change Password"):
        wait_and_click(driver, By.NAME, "change_pass_btn")
        wait_for(driver, By.NAME, "old_pass").send_keys(TEST_PASSWORD)
        wait_for(driver, By.NAME, "new_pass").send_keys("newpass123")
        wait_and_click(driver, By.NAME, "change_pass_btn")
    
    with allure.step("Verify Password Changed"):
        time.sleep(1)
        body_text = driver.page_source
        assert "Password has changed" in body_text

    with allure.step("Log Out"):
        driver.get(f"{BASE_URL}/logout")

    with allure.step("Login with New Password"):
        driver.get(f"{BASE_URL}/login")
        wait_for(driver, By.NAME, "email").send_keys(TEST_EMAIL)
        wait_for(driver, By.NAME, "pwd").send_keys("newpass123")
        wait_and_click(driver, By.NAME, "submit")
        time.sleep(1)
        assert "/user" in driver.current_url

    with allure.step("Reset Password Back"):
        wait_and_click(driver, By.NAME, "change_pass_btn")
        wait_for(driver, By.NAME, "old_pass").send_keys("newpass123")
        wait_for(driver, By.NAME, "new_pass").send_keys(TEST_PASSWORD)
        wait_and_click(driver, By.NAME, "change_pass_btn")

@allure.severity(Severity.CRITICAL)
@allure.title("Delete User Account")
def test_delete_account(driver):
    test_login(driver)

    with allure.step("Delete Account with 'DELETE' confirmation"):
        wait_and_click(driver, By.NAME, "delete_acc_btn")
        wait_for(driver, By.NAME, "del").send_keys("DELETE")
        wait_and_click(driver, By.NAME, "delete_acc_btn")

    with allure.step("Verify Account Deleted"):
        time.sleep(1)
        body_text = driver.page_source
        assert "Account deleted" in body_text

    with allure.step("Verify Redirect to Home"):
        time.sleep(1)
        assert driver.current_url == f"{BASE_URL}/"
