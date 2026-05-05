import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()

try:
    driver.get("https://www.dr.com.tr/")
    time.sleep(2)
    # Search & Add
    driver.find_element(By.CSS_SELECTOR, "input.search-input").send_keys("Harry Potter")
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "searchIcon"))
    time.sleep(3)
    add_btn = driver.find_elements(By.CSS_SELECTOR, "button.js-add-basket")[0]
    driver.execute_script("arguments[0].click();", add_btn)
    time.sleep(2)
    
    # Go to cart
    driver.get("https://www.dr.com.tr/sepetim")
    time.sleep(3)
    
    # Click Delete
    del_btn = driver.find_element(By.CLASS_NAME, "js-basket-item-delete")
    driver.execute_script("arguments[0].click();", del_btn)
    time.sleep(2)
    
    with open("cart_after_delete.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
        
    print("Delete clicked. Check cart_after_delete.html")
    
finally:
    driver.quit()
