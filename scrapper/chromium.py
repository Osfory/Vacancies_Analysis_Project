from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def open_chrome_browser(path_to_chrome_driver):
    return webdriver.Chrome(path_to_chrome_driver)

def connect_to_opened_chrome(path_to_chrome_driver, port):
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:" + str(port))
    chrome_driver = path_to_chrome_driver
    return webdriver.Chrome(chrome_driver, options=chrome_options)