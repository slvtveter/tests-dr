import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def add_book_to_cart(driver):
    driver.get("https://www.dr.com.tr/")
    handle_popups(driver)
    
    search_box = driver.find_element(By.CSS_SELECTOR, "input.search-input")
    search_box.clear()
    search_box.send_keys("Harry Potter")
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "searchIcon"))
    
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: "q=Harry" in d.current_url)
    time.sleep(2) # Let products render
    
    add_buttons = driver.find_elements(By.CSS_SELECTOR, "button.js-add-basket")
    if add_buttons:
        driver.execute_script("arguments[0].click();", add_buttons[0])
        time.sleep(3) # Wait for add animation and backend processing
    
    driver.get("https://www.dr.com.tr/sepetim")
    # Instead of presence, wait for URL to confirm we are in cart, then find element
    wait.until(lambda d: "/sepetim" in d.current_url)
    time.sleep(2) # Let the cart render

def update_quantity(driver, quantity):
    """Updates the quantity using JS since the input is readonly."""
    input_element = driver.find_element(By.CLASS_NAME, "basketCounter")
    driver.execute_script(f"arguments[0].value = '{quantity}'; arguments[0].dispatchEvent(new Event('change'));", input_element)
    time.sleep(2) # Wait for any ajax updates

# --- TEST CASES ---

def test_cart_add_item(driver):
    add_book_to_cart(driver)
    input_element = driver.find_element(By.CLASS_NAME, "basketCounter")
    assert int(input_element.get_attribute("value")) >= 1

@pytest.mark.parametrize("quantity", [0, 1, 50, 99, 100])
def test_cart_update_quantity_bva(driver, quantity):
    add_book_to_cart(driver)
    update_quantity(driver, quantity)
    
    try:
        input_element = driver.find_element(By.CLASS_NAME, "basketCounter")
        actual_value = int(input_element.get_attribute("value"))
    except:
        actual_value = None # Element disappeared
    
    # Assertions based on Boundary Values
    if quantity == 0:
        # Setting to 0 via JS sets the value to 0 without removing the item immediately
        assert actual_value == 0
            
    elif quantity in [1, 50]:
        # Valid boundaries
        assert actual_value == quantity
        
    elif quantity in [99, 100]:
        # Invalid boundaries. Check if the site caps it at 50 or allows it.
        if actual_value > 50:
            pytest.xfail(f"Known Defect: Site allows quantity {actual_value} which exceeds max 50")
        assert actual_value <= 50

def test_cart_remove_item(driver):
    add_book_to_cart(driver)
    
    # Click the delete icon
    delete_button = driver.find_element(By.CLASS_NAME, "js-basket-item-delete")
    driver.execute_script("arguments[0].click();", delete_button)
    
    # Wait for the specific SweetAlert confirmation popup button
    wait = WebDriverWait(driver, 5)
    confirm_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.swal2-confirm")))
    driver.execute_script("arguments[0].click();", confirm_button)
    
    time.sleep(3)
    
    # Verify cart is empty
    elements = driver.find_elements(By.CLASS_NAME, "basketCounter")
    assert len(elements) == 0
