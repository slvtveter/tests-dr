import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

try:
    # 1. Go to homepage and search
    driver.get("https://www.dr.com.tr/")
    time.sleep(3)
    
    # Handle popups
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

    # Search
    search_box = driver.find_element(By.CSS_SELECTOR, "input.search-input")
    search_box.clear()
    search_box.send_keys("Harry Potter")
    
    search_button = driver.find_element(By.ID, "searchIcon")
    driver.execute_script("arguments[0].click();", search_button)
    
    # Wait for results page
    wait.until(lambda d: "q=Harry" in d.current_url)
    time.sleep(2)
    
    # Find the first add to cart button in the results
    add_buttons = driver.find_elements(By.CSS_SELECTOR, "button.js-add-basket")
    if add_buttons:
        print(f"Found {len(add_buttons)} add to cart buttons.")
        driver.execute_script("arguments[0].click();", add_buttons[0])
        print("Clicked the first Add to Cart button.")
        time.sleep(3)
    else:
        print("Could not find any add to cart buttons on search results.")
    
    # Navigate to Cart
    driver.get("https://www.dr.com.tr/sepetim")
    time.sleep(5)
    
    # Dump Cart page HTML
    with open("cart_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved cart_page.html")
    
finally:
    driver.quit()
