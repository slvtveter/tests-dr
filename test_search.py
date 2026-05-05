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

def perform_search(driver, query):
    """Helper function to find the search box, enter a query, and click search."""
    handle_popups(driver)
    search_box = driver.find_element(By.CSS_SELECTOR, "input.search-input")
    search_box.clear()
    search_box.send_keys(query)
    
    # Use JavaScript click to bypass any lingering invisible popup overlays
    search_button = driver.find_element(By.ID, "searchIcon")
    driver.execute_script("arguments[0].click();", search_button)

# --- TEST CASES ---

def test_search_valid_book(driver):
    driver.get("https://www.dr.com.tr/")
    perform_search(driver, "Harry Potter")
    
    # Wait for results to load by checking the URL
    WebDriverWait(driver, 15).until(lambda d: "q=Harry" in d.current_url)
    assert "Harry Potter" in driver.page_source

def test_search_empty_query(driver):
    driver.get("https://www.dr.com.tr/")
    perform_search(driver, "")
    
    # An empty search usually shouldn't navigate away to a query page
    time.sleep(2) # Brief wait to ensure page settled
    assert "q=" not in driver.current_url

def test_search_only_spaces(driver):
    driver.get("https://www.dr.com.tr/")
    perform_search(driver, "     ")
    
    # Searching for spaces usually behaves like an empty search
    time.sleep(2)
    assert "q=" not in driver.current_url

def test_search_special_characters(driver):
    driver.get("https://www.dr.com.tr/")
    perform_search(driver, "!@#$%^&*()")
    
    # Wait for the page to load after search
    WebDriverWait(driver, 10).until(EC.url_contains("q="))
    
    # Verify that a "Not Found" message appears (in Turkish: "Bulunamadı" or "0 Sonuç")
    # Alternatively, ensure no product elements are found
    page_text = driver.page_source.lower()
    assert "bulunamadı" in page_text or "0 sonuç" in page_text or "bulunamamaktadır" in page_text
