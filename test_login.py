import pytest
import time
import json
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchWindowException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGIN_SUCCESS_TIMEOUT = 180
CHROME_PROFILE_DIR = os.path.join(tempfile.gettempdir(), "dr-com-tr-selenium-profile")
AUTH_COOKIES_PATH = os.path.join(tempfile.gettempdir(), "dr-com-tr-auth-cookies.json")

# Helper to load credentials from a config file (outside version control)
def get_credentials():
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            data = json.load(f)
            return data.get("email", "dummy@example.com"), data.get("password", "DummyPass123!")
    return "dummy@example.com", "DummyPass123!"

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument(f"--user-data-dir={CHROME_PROFILE_DIR}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

def handle_popups(driver):
    """Helper function to close any blocking popups before interacting with the page."""
    wait = WebDriverWait(driver, 3)
    popups = [
        (By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"),
        (By.ID, "dengage_push-refuse-button"),
        (By.CLASS_NAME, "sgf-ai-shop-modal__close-button")
    ]
    for by, value in popups:
        try:
            wait.until(EC.element_to_be_clickable((by, value))).click()
        except:
            pass

def save_auth_cookies(driver):
    with open(AUTH_COOKIES_PATH, "w") as f:
        json.dump(driver.get_cookies(), f)

def perform_login(driver, email, password):
    driver.get("https://www.dr.com.tr/login")
    handle_popups(driver)
    
    wait = WebDriverWait(driver, 20)
    email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
    password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
    
    email_field.clear()
    if email:
        email_field.send_keys(email)
        
    password_field.clear()
    if password:
        password_field.send_keys(password)
        
    # The login button has these specific classes based on our analysis
    login_button = driver.find_element(By.CSS_SELECTOR, "button.auth-page__button.js-form-button")
    driver.execute_script("arguments[0].click();", login_button)

def wait_for_login_redirect(driver, timeout=LOGIN_SUCCESS_TIMEOUT):
    """Wait longer for manual CAPTCHA completion before asserting login success."""
    def login_redirected(d):
        try:
            current_url = d.current_url or ""
        except NoSuchWindowException:
            return False
        return bool(current_url) and "/login" not in current_url

    WebDriverWait(driver, timeout, poll_frequency=1).until(login_redirected)

def assert_native_validation(driver, field):
    message = driver.execute_script("return arguments[0].validationMessage;", field)
    assert message
    assert driver.execute_script("return arguments[0].checkValidity();", field) is False

# --- TEST CASES ---

def test_login_valid_credentials(driver):
    email, password = get_credentials()
    if email == "dummy@example.com":
        pytest.skip("No real credentials in config.json. Skipping valid login test.")
        
    perform_login(driver, email, password)
    
    # Wait for navigation away from login page to confirm success
    wait_for_login_redirect(driver)
    save_auth_cookies(driver)
    assert "/login" not in driver.current_url

def test_login_wrong_password(driver):
    email, _ = get_credentials()
    perform_login(driver, email, "DefinitelyWrongPassword123!")
    
    # URL should stay on login page, and an error should appear
    time.sleep(2)
    assert "/login" in driver.current_url
    
    # Checking for general error presence or specific text
    page_text = driver.page_source.lower()
    # dr.com.tr uses SweetAlert (swal2) for error popups
    assert "swal2-shown" in page_text or "hatalı" in page_text or "yanlış" in page_text

def test_login_invalid_email_format(driver):
    perform_login(driver, "not-an-email", "SomePass123!")
    
    time.sleep(2)
    assert "/login" in driver.current_url
    assert_native_validation(driver, driver.find_element(By.ID, "email"))

def test_login_empty_fields(driver):
    perform_login(driver, "", "")
    
    time.sleep(2)
    assert "/login" in driver.current_url
    assert_native_validation(driver, driver.find_element(By.ID, "email"))
    assert_native_validation(driver, driver.find_element(By.ID, "password"))
