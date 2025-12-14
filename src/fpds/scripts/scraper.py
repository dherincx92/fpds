"""Scrapes fields from FPDS ezSearch page.

author: derek663@gmail.com
last_updated: 2025-12-11
"""

from pathlib import Path
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from fpds.config import FPDS_EZSEARCH_URL, FPDS_FIELDS_FILE_PATH


def update_fields_json(dropdown_fields):
    with Path(FPDS_FIELDS_FILE_PATH).open(encoding="utf-8") as file:
        config = json.load(file)

    current_field_options = [field["name"] for field in config]

    # as of right now, we have no way to validate the pattern unless we go to the data dict
    new_options = [
        {
            "description": "",
            "name": field,
            "quotes": False,
            "regex": "",
        }
        for field in dropdown_fields if field not in current_field_options
    ]
    config.extend(new_options)
    sorted_config = sorted(config, key=lambda field: field["name"])

    print(new_options)
    # with Path(FPDS_FIELDS_FILE_PATH).open(mode="w", encoding="utf-8") as file:
    #     json.dump(sorted_config, file, indent=4)

def scrape_ezsearch():
    """Scrapes FPDS ezSearch field for Advanced Search Criteria dropdown values.

    These values represent valid parameter values for an instance of
    `:class:`fpdsRequest.
    """
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(FPDS_EZSEARCH_URL)

    search_criteria_button = driver.find_element(
        By.CSS_SELECTOR,
        "input[title='Advanced Search Criteria']",
    )
    search_criteria_button.click()

    advanced_search_div = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "advancedSearchdiv"))
    )

    add_button = advanced_search_div.find_element(By.CSS_SELECTOR, "input[title='Add']")
    add_button.click()

    dropdowns = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#advancedSearchdiv select"))
    )

    dropdown_fields = []
    for dropdown in dropdowns:
        options = dropdown.find_elements(By.TAG_NAME, "option")
        for opt in options:
            dropdown_fields.append(opt.get_attribute('value'))

    return dropdown_fields

if __name__ == "__main__":
    dropdown_fields = scrape_ezsearch()
    update_fields_json(dropdown_fields=dropdown_fields)
