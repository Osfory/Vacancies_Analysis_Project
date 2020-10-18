import sys
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from functional import seq
from chromium import *
import pandas as pd
import csv
import json


@dataclass
class ScrapperConfig:
    path_to_driver: str
    path_to_output: str
    num_of_pages: int
    num_of_vacancies: int
    command: str
    port: int


# Usage: path_to_driver path_to_output num_of_pages num_of_vacancies command (open|connect port)
def parseCliArguments():
    argv = len(sys.argv)
    if (argv < 6 or 7 < argv):
        raise ValueError("Usage: path_to_driver path_to_output num_of_pages num_of_vacancies command (open|connect port)")
    args = sys.argv
    num_of_pages = -1 if args[3] == "all" else int(args[3])
    num_of_vacancies = -1 if args[4] == "all" else int(args[4])
    port = int(args[6]) if 7 == argv else -1
    command = "open" if "connect" != args[5] else "connect"
    return ScrapperConfig(args[1], args[2], num_of_pages, num_of_vacancies, command, port)


def page_scrapper(presence, page_catcher, required_elements, number_of_vacancies):
    """
    Function for scrapping pages. Extends DataFrame with vacancies.

    Parameters
    ----------
    presence: str
        CSS element used to locate presence of list of vacancies
    page_catcher: str
        CSS element used to getting vacancy page.
    required_elements: list
        List of CSS elements used to collect the required elements of a web page.
    number_of_vacancies: int
        Number of vacancies to be collected.
    Returns
    -------
        Gives no return.

    For more information see source code.
    """

    global vacancies_df
    # Waiting for presence of list of vacancies
    main_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, presence)))
    # Take a list of vacancies
    vacancies = driver.find_elements_by_css_selector(presence)
    # Iterating over list of vacancies
    for link in vacancies[:number_of_vacancies]:
        vacancy_content = []
        try:
            # Waiting for the presence of vacancies
            main_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, page_catcher)))
            link.find_element_by_css_selector(page_catcher).click()
            driver.switch_to.window(driver.window_handles[1])

            # Waiting for required information
            main_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-qa=\"vacancy-description\"]")))
            # Gather required information
            vacancy_content.extend(seq(required_elements).map(lambda elem: driver.find_element_by_css_selector(elem).text))
            # Appending collected data from page to DataSet
            vacancies_df = pd.concat([vacancies_df, pd.Series(vacancy_content)], axis=1)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except (NoSuchElementException, StaleElementReferenceException):
            vacancy_content.append(None) # append() OR extend()?
            vacancies_df = pd.concat([vacancies_df, pd.Series(vacancy_content)], axis=1)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])


# ----------------------------------
scrapperConfig = parseCliArguments()
print(scrapperConfig)
# ----------------------------------
driver = open_chrome_browser(scrapperConfig.path_to_driver) if "open" == scrapperConfig.command else connect_to_opened_chrome(scrapperConfig.path_to_driver, scrapperConfig.port)
# ----------------------------------
# Set up waiting
main_wait = WebDriverWait(driver, 5, poll_frequency=1, ignored_exceptions=[NoSuchElementException])
# ----------------------------------
# Get Vacancies from HeadHunter
driver.get("https://hh.ru/vacancies/data-scientist")
main_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.vacancy-serp-item")))
# ----------------------------------
# HH by default determines geolocation and changes vacancies to local ones.
# We do not need this, therefore, we find the switch responsible for this and turn it off. Then rebooting the page.
main_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.bloko-icon_cancel"))).click()
driver.refresh()
# ----------------------------------
# Creating pandas DataFrame for storing collected data
vacancies_df = pd.DataFrame()
# Some additional variable for navigation
num_pages = len(driver.find_elements_by_css_selector("span a.bloko-button"))
# ----------------------------------
# Navigation stuff
css_list_of_vacancies = "div.vacancy-serp-item"
css_link_to_vacancy = "a.HH-LinkModifier"
css_next_page_button = "a.HH-Pager-Controls-Next"
# Elements we interested in
css_elements = ["h1.bloko-header-1", "a[data-qa=\"vacancy-company-name\"]", "p[data-qa=\"vacancy-view-location\"]",
                "span[data-qa=\"vacancy-experience\"]", "p[data-qa=\"vacancy-view-employment-mode\"]", "p.vacancy-salary",
                "p.vacancy-creation-time", "div[data-qa=\"vacancy-description\"]", "div.bloko-tag-list"]
# ----------------------------------
# Iterating over pages with vacancies
for i in range(0, range(0, num_pages+1)[scrapperConfig.num_of_pages]): # damn, that's horrible
    print("Performing scrapping on page {}.".format(str(i + 1)))
    page_scrapper(css_list_of_vacancies, css_link_to_vacancy, css_elements, scrapperConfig.num_of_vacancies)
    # Go to next page with vacancies
    main_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_next_page_button))).click()
    print("Went on page {}.".format(str(i + 2)))

print("Performing scrapping on page {}.".format(str(scrapperConfig.num_of_pages + 1)))
page_scrapper(css_list_of_vacancies, css_link_to_vacancy, css_elements, scrapperConfig.num_of_vacancies)
print("Scrapping is over. Congratulations!")
# ----------------------------------
# To CSV file
vacancies_df.to_csv(scrapperConfig.path_to_output + '/vacancies_data_test.csv')
# ----------------------------------
driver.quit()
