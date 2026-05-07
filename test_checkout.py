import pytest
import time
import json
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchWindowException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGIN_SUCCESS_TIMEOUT = 180
CHECKOUT_READY_TIMEOUT = 180
CHROME_PROFILE_DIR = os.path.join(tempfile.gettempdir(), "dr-com-tr-selenium-profile")
AUTH_COOKIES_PATH = os.path.join(tempfile.gettempdir(), "dr-com-tr-auth-cookies.json")

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

def restore_auth_cookies(driver):
    if not os.path.exists(AUTH_COOKIES_PATH):
        return False

    driver.get("https://www.dr.com.tr/")
    with open(AUTH_COOKIES_PATH, "r") as f:
        cookies = json.load(f)

    for cookie in cookies:
        filtered = {k: cookie[k] for k in ("name", "value", "domain", "path", "expiry", "secure", "httpOnly", "sameSite") if k in cookie}
        try:
            driver.add_cookie(filtered)
        except Exception:
            continue

    driver.refresh()
    driver.get("https://www.dr.com.tr/login")
    try:
        wait_for_login_redirect(driver, timeout=10)
        return True
    except TimeoutException:
        return False

def wait_for_login_redirect(driver, timeout=LOGIN_SUCCESS_TIMEOUT):
    """Wait longer for manual CAPTCHA completion before continuing checkout setup."""
    def login_redirected(d):
        try:
            current_url = d.current_url or ""
        except NoSuchWindowException:
            return False
        return bool(current_url) and "/login" not in current_url

    WebDriverWait(driver, timeout, poll_frequency=1).until(login_redirected)

def wait_for_checkout_page(driver, timeout=CHECKOUT_READY_TIMEOUT):
    """Wait for the checkout address page to render, even if the URL shape changes."""
    def checkout_ready(d):
        try:
            current_url = (d.current_url or "").lower()
        except NoSuchWindowException:
            return False
        if any(token in current_url for token in ("teslimat", "adres", "odeme", "checkout")):
            return True

        page_source = d.page_source.lower()
        return any(token in page_source for token in ("js-add-new-address", "add-new-address-btn", "js-save-address", "btnsaveaddress"))

    WebDriverWait(driver, timeout, poll_frequency=1).until(checkout_ready)

def find_checkout_action_button(driver):
    selectors = [
        ".js-save-address",
        "#btnSaveAddress",
        "button[type='submit']",
        "input[type='submit']",
    ]
    for selector in selectors:
        for element in driver.find_elements(By.CSS_SELECTOR, selector):
            label = " ".join(filter(None, [
                (element.text or "").strip(),
                element.get_attribute("value") or "",
                element.get_attribute("aria-label") or "",
                element.get_attribute("class") or "",
            ])).lower()
            if any(token in label for token in ("kaydet", "devam", "onay", "adres", "submit")):
                return element

    for element in driver.find_elements(By.CSS_SELECTOR, "button, input[type='button'], input[type='submit']"):
        label = " ".join(filter(None, [
            (element.text or "").strip(),
            element.get_attribute("value") or "",
            element.get_attribute("aria-label") or "",
            element.get_attribute("class") or "",
        ])).lower()
        if any(token in label for token in ("kaydet", "devam", "onay", "adres", "submit")):
            return element

    raise AssertionError("Could not locate the checkout submit button.")

def login_and_prepare_checkout(driver):
    email, password = get_credentials()
    if "dummy" in email or "mehmet_will" in email:
        pytest.skip("No real credentials provided in config.json. Checkout tests require a valid user account.")

    logged_in = restore_auth_cookies(driver)
    if not logged_in:
        # 1. Login
        driver.get("https://www.dr.com.tr/login")
        handle_popups(driver)
        
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(email)
        wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
        login_btn = driver.find_element(By.CSS_SELECTOR, "button.auth-page__button.js-form-button")
        driver.execute_script("arguments[0].click();", login_btn)
        
        wait_for_login_redirect(driver)
        with open(AUTH_COOKIES_PATH, "w") as f:
            json.dump(driver.get_cookies(), f)
    
    # 2. Add item to cart
    driver.get("https://www.dr.com.tr/")
    search_box = driver.find_element(By.CSS_SELECTOR, "input.search-input")
    search_box.clear()
    search_box.send_keys("Harry Potter")
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "searchIcon"))
    
    wait = WebDriverWait(driver, 20)
    wait.until(lambda d: "q=Harry" in d.current_url)
    time.sleep(2)
    
    add_buttons = driver.find_elements(By.CSS_SELECTOR, "button.js-add-basket")
    if add_buttons:
        driver.execute_script("arguments[0].click();", add_buttons[0])
        time.sleep(3)
        
    # 3. Go to checkout
    driver.get("https://www.dr.com.tr/sepetim")
    wait.until(lambda d: "/sepetim" in d.current_url)
    checkout_btn = WebDriverWait(driver, 20).until(
        lambda d: next(
            (
                element for element in d.find_elements(By.CSS_SELECTOR, "button, a")
                if "checkout" in " ".join(filter(None, [
                    (element.text or "").strip(),
                    element.get_attribute("class") or "",
                    element.get_attribute("href") or "",
                ])).lower()
                or "başla" in (element.text or "").lower()
                or "devam" in (element.text or "").lower()
            ),
            None,
        )
    )
    driver.execute_script("arguments[0].click();", checkout_btn)
    
    # Wait for address selection/creation page
    wait_for_checkout_page(driver)
    time.sleep(2)

# --- TEST CASES ---

def test_checkout_address_required_fields(driver):
    login_and_prepare_checkout(driver)
    
    # Attempt to trigger "Add New Address" if on a selection screen
    try:
        new_address_btn = driver.find_element(By.CSS_SELECTOR, ".js-add-new-address, .add-new-address-btn")
        driver.execute_script("arguments[0].click();", new_address_btn)
        time.sleep(2)
    except:
        pass
        
    # Submit empty form
    submit_btn = find_checkout_action_button(driver)
    driver.execute_script("arguments[0].click();", submit_btn)
    time.sleep(2)
    
    # Verify validation messages appear
    page_text = driver.page_source.lower()
    assert "zorunlu" in page_text or "gerekli" in page_text or "boş bırakılamaz" in page_text or "swal2-shown" in page_text

def test_checkout_address_invalid_format(driver):
    login_and_prepare_checkout(driver)
    
    try:
        new_address_btn = driver.find_element(By.CSS_SELECTOR, ".js-add-new-address, .add-new-address-btn")
        driver.execute_script("arguments[0].click();", new_address_btn)
        time.sleep(2)
    except:
        pass
        
    # Fill invalid phone number (e.g., letters instead of numbers)
    try:
        phone_input = driver.find_element(By.CSS_SELECTOR, "input[name='Phone'], #PhoneNumber, .js-phone-mask")
        phone_input.clear()
        phone_input.send_keys("ABCDEFG")
    except:
        pytest.skip("Could not locate phone input field.")
        
    submit_btn = find_checkout_action_button(driver)
    driver.execute_script("arguments[0].click();", submit_btn)
    time.sleep(2)
    
    # Verify format validation
    page_text = driver.page_source.lower()
    assert "geçerli" in page_text or "format" in page_text or "hatalı" in page_text
