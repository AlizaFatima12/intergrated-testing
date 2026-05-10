from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import sys
import time

def run_tests(base_url):
    options = Options()
    options.add_argument("--headless")

    # Selenium Manager will automatically download and use geckodriver
    driver = webdriver.Firefox(options=options)

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