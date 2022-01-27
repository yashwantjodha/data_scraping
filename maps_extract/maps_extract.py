# This file would have function which takes a tag name
# and output file, saves all the stores info in output file
# it returns how many stores were found and written

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from helpers import *

import pandas as pd

import time


def find_stores(keyword, output_file=None):
    """
    Takes keyword and output_file.
    Searches keyword on google maps and saves the output of all stores in output_file.

    Returns number of stores found and written to the file.

    todo:
        1. check if the file contains any duplicate rows and remove them

    - done: all the hardcoded waiting time seems to arbitary, they might not be able to scale to 7000 excel sheets
    - need to write file logic such that if the programs stops due to some reason most of the extracted data should remain
    - there could be scenario where the search results might not belong to the city in keyword
    - there are combinations of keyword with cities and business types
    - instead of writing code for clicking back (driver.navigate().back())
    """

    
    serial_num = 1
    output_df = pd.read_excel('files/templates/Output_file.xlsx')
    # opening the template file
    # try:
    #     pass
    #     # output_df = pd.read_excel(f'files/extracted/{output_file}.xlsx')
    #     # try:
    #     #     # if there is data in file, find last row's index
    #     #     serial_num = output_df.iloc[-1, 0] + 1
    #     # except:
    #     #     pass
    # except:
    #     output_df = pd.read_excel('files/templates/Output_file.xlsx')

    # serial number
    # try:
    #     # if there is data in file, find last row's index
    #     serial_num = output_df.iloc[-1, 0] + 1
    # except:
    #     serial_num = 1

    # 1. open and search keyword on maps
    driver = selenium.webdriver.Chrome()
    maps_url = f'https://www.google.com/maps/search/{keyword}'
    driver.get(maps_url)

    # 2. find all the store from results and click one by one
    # finding total number of results

    # range(1, 41, 2)
    stores_xpaths_num = list(range(3, 41, 2))
    store_count = 0

    while store_count < len(stores_xpaths_num):

        store_xpath = \
            f'/html[1]/body[1]/div[3]/div[9]/div[8]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[{stores_xpaths_num[store_count]}]'

        # scroll to bottom if the store not found
        # trying only 2 times
        scroll_tries = 4
        for scroll_try in range(scroll_tries):
            try:
                store = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, store_xpath)))
                break
            except:
                # scroll to bottom if the store isn't found
                scrollable_div = driver.find_element(By.XPATH, \
                    r'/html[1]/body[1]/div[3]/div[9]/div[8]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]')
                driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)

        if scroll_try == scroll_tries - 1:
            print("----No more store to click----")
            break
        
        # click on the store found
        store.click()
        
        # waiting for store data to load
        try:
            location_xpath = r'/html[1]/body[1]/div[3]/div[9]/div[8]/div[1]/div[1]/div[1]/div[1]/div[7]/div[1]/button[1]/div[1]/div[2]/div[1]'
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, location_xpath)))
        except:
            try:
                directions_xpath = r'/html[1]/body[1]/div[3]/div[9]/div[8]/div[1]/div[1]/div[1]/div[1]/div[4]/div[1]/button[1]'
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, directions_xpath)))
            except:
                try:
                    cancel_xpath = r'/html[1]/body[1]/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[2]/a[1]'
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, directions_xpath)))
                except:
                    pass

        ################################
        # Extracting Data of the store #
        ################################
        
        # could do two things, either open the file once and add the data at one time
        # or write data in every loop to avoid loosing data, but ...
        # if program have to restart, previous data could be duplicated

        # from all the buttons on store page

        store_data = {}

        store_data['S. No.'] = serial_num
        store_data['Search Keyword'] = keyword
        store_data['Storefront Link'] = driver.current_url
        store_data['Company Name'] = driver.title.replace('- Google Maps', '').strip()
        
        
        rating_xpath = \
        r'/html[1]/body[1]/div[3]/div[9]/div[8]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/span[1]/span[1]/span[1]'
        
        try:
            rating = driver.find_element(By.XPATH, rating_xpath).text
        except:
            rating = None

        store_data['Rating'] = rating

        store_buttons = driver.find_elements(By.TAG_NAME, 'button')
        i = 0
        while i < len(store_buttons):
            try:
                store_button = store_buttons[i]
                store_button_aria_label = store_button.get_attribute("aria-label")
            except:
                print('----Stale element----')
                # driver.refresh()
                time.sleep(10)
                store_buttons = driver.find_elements(By.TAG_NAME, 'button')
                i = 0
                continue
            i = i + 1

            # if there is no aria-label
            if store_button_aria_label == None:
                continue

            # store phone number
            if store_button_aria_label.startswith('Phone'):
                store_data['Phone'] = store_button_aria_label.replace('Phone:', '').strip()

            # store address
            if store_button_aria_label.startswith('Address'):
                store_data['Address'] = store_button_aria_label.replace('Address:', '').strip()
                store_data['State'], store_data['City'], store_data['Pincode'] = find_address_details(store_data['Address'])
                
            # website for email adress
            if store_button_aria_label.startswith('Website:'):
                store_website = 'http://' + store_button_aria_label.replace('Website:', '').strip()
                store_data['Website'] = store_website
                # store_data['Email Id'], products =  website_details(store_website)

                # for product_count in range(len(products)):
                #     store_data[f'Product{product_count + 1}'] = products[product_count]

                #     # max 30 products
                #     if product_count >= 30:
                #         break


        output_df = output_df.append(store_data, ignore_index=True)

        serial_num += 1 # incrementing serial number
        #################################

        # 4. click on back
        # todo: confirm if the back button is back button only
        back_button_xpath = r'/html[1]/body[1]/div[3]/div[9]/div[3]/div[1]/div[1]/div[1]/div[1]/button[1]'
        back = driver.find_element(By.XPATH, back_button_xpath)
        
        back.click()

        # watiing for results to load on clicking back
        update_when_map_moves_xpath = r'/html[1]/body[1]/div[3]/div[9]/div[8]/div[1]/div[1]/div[1]/div[1]/div[2]/div[3]/button[1]'
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, update_when_map_moves_xpath)))

        # writing to excel
        # print(output_df)
        # output_df.to_excel(f'files/extracted/{output_file}.xlsx', index=False)
        output_df.to_excel(f'files/extracted/{keyword}.xlsx', index=False)
        

        # to next store
        # if the store is 20th then find if there is next buttom,
        # if there is a next button, press it
        if stores_xpaths_num[store_count] == 39:
            try:
                next_button_xpath = \
                    r'/html[1]/body[1]/div[3]/div[9]/div[8]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/button[2]'
                next_button = driver.find_element(By.XPATH, next_button_xpath)
                next_button.click()
                time.sleep(5) # waiting 5 seconds to load next page results
                store_count = 0
                continue
            except:
                # if the next button is not clickable
                print('----next button is not clickable----')
                break
        else:
            store_count += 1

    # append_df_to_excel(f'{output_file}.xlsx', output_df, header=None, index=False)
    # writing the extracted data to the file
    # output_df.to_excel(output_file + 'Final' + '.xlsx', index=False)
    driver.quit()