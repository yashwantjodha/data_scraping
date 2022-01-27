# Example 

import selenium
from selenium import webdriver
from concurrent import futures
import time

# **** OPTIONS for chrome Driver ****
# here headless means without opening the browser window
# everything is done in background
# use this when you are sure your extraction code is working as expected
# make the extraction process way faster
op = selenium.webdriver.ChromeOptions()
# op.add_argument('headless')

driver = selenium.webdriver.Chrome(options=op)
driver.get(r'https://google.com')

time.sleep(10)
driver.quit()