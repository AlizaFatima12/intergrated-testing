from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

def run_tests(base_url):
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 10)
    failures = []

    try:
        driver.get(base_url)

        # Wait until task list is loaded by JavaScript
        wait.until(
            EC.presence_of_element_located((By.ID, "task-list"))
        )

        # Verify page title
        if driver.title != "Taskboard":
            failures.append(f"FAIL: Unexpected page title '{driver.title}'")
        else:
            print("PASS: Page title is correct")

        # Verify logo text
        logo = driver.find_element(By.CLASS_NAME, "logo")
        if "taskboard_" not in logo.text:
            failures.append("FAIL: Logo text not found")
        else:
            print("PASS: Logo text found")

        # Verify input field exists
        driver.find_element(By.ID, "new-title")
        print("PASS: New task input field found")

        # Verify Add button exists
        add_button = driver.find_element(By.CLASS_NAME, "btn-add")
        if "+ add" not in add_button.text.lower():
            failures.append("FAIL: Add button text incorrect")
        else:
            print("PASS: Add button found")

        # Wait until sample task appears
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Write unit tests')]")
            )
        )
        print("PASS: Sample task 'Write unit tests' found")

        # Verify stats counters exist
        driver.find_element(By.ID, "s-total")
        driver.find_element(By.ID, "s-done")
        driver.find_element(By.ID, "s-pending")
        print("PASS: Stats counters found")

        # Verify progress bar exists
        driver.find_element(By.ID, "prog-fill")
        print("PASS: Progress bar found")

    except Exception as e:
        failures.append(f"FAIL: {str(e)}")

    finally:
        driver.quit()

    if failures:
        print("\n".join(failures))
        sys.exit(1)

    print("All Selenium tests passed.")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    run_tests(url)