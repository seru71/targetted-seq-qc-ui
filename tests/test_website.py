from selenium import webdriver
from selenium.webdriver.common.keys import Keys

WEBSITE = 'http://127.0.0.1:5000/'

driver = webdriver.Chrome(executable_path='C:\chrome_driver\chromedriver.exe')

driver.get(WEBSITE)
driver.maximize_window()

runs_tab = driver.find_element_by_id('runs')
runs_tab.click()

samples_tab = driver.find_element_by_id('samples')
samples_tab.click()

driver.close()
