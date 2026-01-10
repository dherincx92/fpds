"""Scrapes fields from FPDS ezSearch page.

author: derek663@gmail.com
last_updated: 2026-01-10
"""

import json
import re
from pathlib import Path

from packaging.version import Version
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tabulate import tabulate

from fpds.config import (
    FPDS_EZSEARCH_URL,
    FPDS_FIELDS_CONFIG,
    FPDS_FIELDS_FILE_PATH,
    FPDS_WORKSITE_URL,
)
from fpds.utilities import set_github_output

SPEC_PATTERN = "V(.*?) Specifications"


def configure_driver(url: str) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url=url)
    return driver


def update_fields_json(dropdown_fields: list[str]) -> None:
    config = FPDS_FIELDS_CONFIG
    current_field_options = [field["name"] for field in config]
    new_options = [
        field for field in dropdown_fields if field["name"] not in current_field_options
    ]
    config.extend(new_options)
    sorted_config = sorted(config, key=lambda field: field["name"])

    with Path(str(FPDS_FIELDS_FILE_PATH)).open(mode="w", encoding="utf-8") as file:
        json.dump(sorted_config, file, indent=4)
        file.write("\n")


def scrape_latest_data_dictionary() -> str:
    """Scrapes FPDS Worksite page for the latest data dictionary document."""
    driver = configure_driver(url=FPDS_WORKSITE_URL)
    div = driver.find_elements(
        By.XPATH, "//div[h3[contains(normalize-space(.), 'Specifications')]]"
    )

    h3_tags = []
    for child in div:
        h3 = child.find_element(By.TAG_NAME, "h3")
        h3_tags.append(h3.text)

    prog = re.compile(SPEC_PATTERN)
    versions = [prog.search(tag).group(1) for tag in h3_tags if prog.search(tag)]
    highest = max(versions, key=lambda v: Version(v.strip()))
    idx = h3_tags.index(f"V{highest} Specifications")

    tag = div[idx].find_element(
        By.XPATH,
        ".//a[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
        "'data dictionary')]",
    )
    data_dict_url = tag.get_attribute("href")

    set_github_output(data_dict_url=data_dict_url, feed_version=highest)
    return data_dict_url


def scrape_ezsearch() -> list[str]:
    """Scrapes FPDS ezSearch field for Advanced Search Criteria dropdown values.

    These values represent valid parameter values for an instance of
    `:class:`fpdsRequest.
    """
    driver = configure_driver(url=FPDS_EZSEARCH_URL)

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

    def _get_visible_div(driver):
        divs = driver.find_elements(By.XPATH, "//div[starts-with(@id,'my0DivBox')]")
        for div in divs:
            if div.is_displayed():
                return div
        return False

    dropdowns = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "#advancedSearchdiv select")
        )
    )

    dropdown_fields = []
    failures = []
    for dropdown in dropdowns:
        elements = dropdown.find_elements(By.TAG_NAME, "option")
        for element in elements[1:]:  # first element is a label
            try:
                element.click()
                div = WebDriverWait(driver, 10).until(_get_visible_div)
                inputs = div.find_elements(By.XPATH, ".//input")

                dropdown_fields.append(
                    {
                        "name": element.get_attribute("value"),
                        "description": element.text,
                        "quotes": False if len(inputs) == 2 else True,
                        "regex": "<TODO: Add regex pattern>",
                    }
                )

            except:
                print(f"Failed on element {element.text}")
                match = next(
                    (f for f in FPDS_FIELDS_CONFIG if f["name"] == element.text), None
                )
                status = "✅" if match else "❌"
                failures.append([element.get_attribute("value"), element.text, status])

    grid = tabulate(
        tabular_data=failures,
        headers=["Name", "Description", "Exists"],
        tablefmt="github",
    )
    set_github_output(grid=grid)

    return dropdown_fields


if __name__ == "__main__":
    scrape_latest_data_dictionary()
    dropdown_fields = scrape_ezsearch()
    update_fields_json(dropdown_fields=dropdown_fields)
