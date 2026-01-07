"""Scrapes fields from FPDS ezSearch page.

author: derek663@gmail.com
last_updated: 2026-01-06
"""

import json
from pathlib import Path
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from fpds.config import FPDS_EZSEARCH_URL, FPDS_FIELDS_FILE_PATH


def update_fields_json(dropdown_fields: List[str]) -> None:
    with Path(str(FPDS_FIELDS_FILE_PATH)).open(encoding="utf-8") as file:
        config = json.load(file)

    current_field_options = [field["name"] for field in config]

    # as of right now, we have no way to validate the pattern unless we go to the data dict
    new_options = [
        {
            "description": "<TODO: Add description>",
            "name": field,
            "quotes": False,
            "regex": "<TODO: Add regex pattern>",
        }
        for field in dropdown_fields
        if field not in current_field_options
    ]
    config.extend(new_options)
    sorted_config = sorted(config, key=lambda field: field["name"])

    with Path(str(FPDS_FIELDS_FILE_PATH)).open(mode="w", encoding="utf-8") as file:
        json.dump(sorted_config, file, indent=4)
        file.write("\n")


def scrape_ezsearch() -> List[str]:
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
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "#advancedSearchdiv select")
        )
    )

    dropdown_fields = []
    for dropdown in dropdowns:
        element = dropdown.find_elements(By.TAG_NAME, "option")
        for opt in element[1:]:  # skip the first element since its the dropdown label
            value = opt.get_attribute("value")
            if value:
                dropdown_fields.append(value)

    return dropdown_fields


if __name__ == "__main__":
    dropdown_fields = scrape_ezsearch()
    update_fields_json(dropdown_fields=dropdown_fields)
