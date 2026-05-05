import pytest
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def login_and_prepare_checkout(driver):
    email, password = get_credentials()
    if email == "dummy@example.com":
        pytest.skip("No real credentials provided in config.json. Checkout tests require a valid user account.")
        
    # 1. Login
    driver.get("https://www.dr.com.tr/login")
    handle_popups(driver)
    
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    login_btn = driver.find_element(By.CSS_SELECTOR, "button.auth-page__button.js-form-button")
    driver.execute_script("arguments[0].click();", login_btn)
    
    WebDriverWait(driver, 10).until(lambda d: "/login" not in d.current_url)
    
    # 2. Add item to cart
    driver.get("https://www.dr.com.tr/")
    search_box = driver.find_element(By.CSS_SELECTOR, "input.search-input")
    search_box.clear()
    search_box.send_keys("Harry Potter")
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "searchIcon"))
    
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: "q=Harry" in d.current_url)
    time.sleep(2)
    
    add_buttons = driver.find_elements(By.CSS_SELECTOR, "button.js-add-basket")
    if add_buttons:
        driver.execute_script("arguments[0].click();", add_buttons[0])
        time.sleep(3)
        
    # 3. Go to checkout
    driver.get("https://www.dr.com.tr/sepetim")
    wait.until(lambda d: "/sepetim" in d.current_url)
    checkout_btn = driver.find_element(By.CLASS_NAME, "js-begin-checkout")
    driver.execute_script("arguments[0].click();", checkout_btn)
    
    # Wait for address selection/creation page
    wait.until(lambda d: "teslimat" in d.current_url.lower() or "adres" in d.current_url.lower())
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
    submit_btn = driver.find_element(By.CSS_SELECTOR, ".js-save-address, #btnSaveAddress")
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
        
    submit_btn = driver.find_element(By.CSS_SELECTOR, ".js-save-address, #btnSaveAddress")
    driver.execute_script("arguments[0].click();", submit_btn)
    time.sleep(2)
    
    # Verify format validation
    page_text = driver.page_source.lower()
    assert "geçerli" in page_text or "format" in page_text or "hatalı" in page_text
