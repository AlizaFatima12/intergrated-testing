from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import sys, time

def run_tests(base_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    svc = Service("C:/tools/chromedriver/chromedriver.exe")
    driver = webdriver.Chrome(service=svc, options=options)
    failures = []
    try:
        driver.get(base_url)
        time.sleep(1)
        if "Task Manager" not in driver.title and "Task Manager" not in driver.page_source:
            failures.append("FAIL: Homepage did not load correctly")
        else:
            print("PASS: Homepage loaded")
        el = driver.find_element(By.ID, "status")
        if el.text != "Running":
            failures.append(f"FAIL: Status element text was '{el.text}'")
        else:
            print("PASS: Status element OK")
    finally:
        driver.quit()
    if failures:
        print("\n".join(failures))
        sys.exit(1)
    print("All Selenium tests passed.")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    run_tests(url)