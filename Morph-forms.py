import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Define file paths for input and output CSV files
INPUT_CSV_PATH = "C:/Users/rupin/Desktop/roots.csv"  # Update with the actual path to roots.csv
OUTPUT_CSV_PATH = "C:/Users/rupin/Desktop/morph-forms_results.csv"  # Update with the actual path for output 

# Path to GeckoDriver (update this if not in PATH)
# GECKODRIVER_PATH = "C:/path/to/geckodriver.exe"  # Example for Windows

# Read the input CSV file
try:
    df = pd.read_csv(INPUT_CSV_PATH)
    print(f"Successfully read {INPUT_CSV_PATH}. Number of words: {len(df)}")
except FileNotFoundError:
    print(f"Error: {INPUT_CSV_PATH} not found. Please ensure the file exists.")
    exit(1)

# Assume the column with Punjabi words is named 'word' (adjust if different)
if 'word' not in df.columns:
    print(f"Error: 'word' column not found in {INPUT_CSV_PATH}.")
    exit(1)

# Initialize Selenium WebDriver for Firefox
firefox_options = Options()
# Set Firefox profile to handle SSL certificate errors
firefox_options.set_preference("security.enterprise_roots.enabled", True)
firefox_options.set_preference("webdriver_accept_untrusted_certs", True)
firefox_options.set_preference("webdriver_assume_untrusted_issuer", True)
# firefox_options.add_argument("--headless")  # Uncomment for headless mode

# Initialize WebDriver
# If GeckoDriver is not in PATH, uncomment and update the service line
# service = Service(GECKODRIVER_PATH, log_file="geckodriver.log")
# driver = webdriver.Firefox(service=service, options=firefox_options)
driver = webdriver.Firefox(options=firefox_options)  # Use this if GeckoDriver is in PATH

# Navigate to the morphological analysis webpage
url = "https://pgc.learnpunjabi.org/#Morph"
try:
    driver.get(url)
    print("Successfully loaded webpage.")
except WebDriverException as e:
    print(f"Error loading webpage: {str(e)}")
    driver.quit()
    exit(1)

# Wait for the page to load
time.sleep(2)

# Prepare a list to store results
results = []

try:
    # Click the hyperlink with id="linkbtnMorph" and href="#Morph"
    try:
        morph_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "linkbtnMorph"))
        )
        morph_link.click()
        print("Successfully clicked Morph hyperlink.")
        time.sleep(2)  # Increased pause to ensure page updates
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error clicking Morph hyperlink: {str(e)}")
        # Continue execution, as the page might already be in the correct state

    # Ensure the radio button is selected
    try:
        radio_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "radioMorphOption1"))
        )
        if not radio_button.is_selected():
            radio_button.click()
            print("Successfully selected radio button.")
        else:
            print("Radio button already selected.")
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error selecting radio button: {str(e)}")
        raise  # Stop execution if radio button fails, as it’s critical

    # Process each word in the CSV
    for index, row in df.iterrows():
        word = row['word']
        print(f"Processing word: {word}")

        try:
            # Find the input text area and enter the word
            input_area = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "txtMorphInput"))
            )
            input_area.clear()
            input_area.send_keys(word)
            print(f"Entered word '{word}' into input area.")

            # Click the process button
            process_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "btnMorphProcess"))
            )
            process_button.click()
            print("Clicked process button.")

            # Wait for results to appear (increased for reliability)
            time.sleep(5)

            # Retrieve the results from the output text area
            results_area = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "txtMorphResults"))
            )
            result_text = results_area.get_attribute('value').strip()
            print(f"Retrieved result for '{word}': {result_text}")

            # Store the word and its result
            results.append({'word': word, 'morph_result': result_text})

        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error processing word '{word}': {str(e)}")
            results.append({'word': word, 'morph_result': f'Error: {str(e)}'})

except Exception as e:
    print(f"Unexpected error during processing: {str(e)}")

finally:
    # Close the browser
    driver.quit()
    print("Browser closed.")

# Save results to a new CSV file
try:
    print(f"Results collected: {results}")
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')
    print(f"Results saved to {OUTPUT_CSV_PATH}. Number of rows: {len(results_df)}")
except Exception as e:
    print(f"Error saving results to {OUTPUT_CSV_PATH}: {str(e)}")