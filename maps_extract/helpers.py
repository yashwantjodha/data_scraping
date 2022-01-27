# Helper module
# it contains functions which supplement the data extraction
# so, the funtionality of both the functions could remain separate

import re
import requests
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import pandas as pd
import random
import string

def find_address_details(address):
    """
    takes adress
    returns a tuple (State, City, Pincode)
    A -24 SHIV INDUSTRIAL PARK, AMBICA MILL COMPOUND, NR. OVERBRIDGE VATVA, Vatva, Ahmedabad, Gujarat 382440

    """
    try:
        pincode = re.search(r'(\d\d\d\d\d\d)\Z', address).group(0)
        state = address.split(',')[-1].replace(pincode, '').strip()
        city = address.split(',')[-2].strip()
    except:
        pincode = None
        state = None
        city = None
        
    return (state, city, pincode)

def find_email(link):
    """
    Takes website as input link and finds email address using regex,
    """
    try:
        resp = requests.get(link, headers = {
            # using different use agent because default is being blocked by the hosting server
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
        }, verify=False)
        
        if resp.status_code != 200:
            print('Error in get request')
            return None

        # html output
        html_doc = resp.content

    
        soup = BeautifulSoup(html_doc, 'html.parser')
        text = soup.find("body").get_text()

        email = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    
        email = email.group(0)
    except:
        email = None
    
    return email

def website_details(website):
    """
    takes website and find any email address and products

    returns (email, [products])
    """
    # need to use selenium

    print(f'{website}')
    website_df = pd.read_excel('anurag/websites_lookup.xlsx')

    # **** OPTIONS for chrome Driver ****
    # here headless means without opening the browser window
    # everything is done in background
    # use this when you are sure your extraction code is working as expected
    # make the extraction process way faster
    op = selenium.webdriver.ChromeOptions()
    op.add_argument('headless')

    store_driver = selenium.webdriver.Chrome(options=op)
    try:
        store_driver.get(website)
    except:
        print('--------Driver Error---------')
        return

    try:
        # 1. find email
        email = find_email(website) # on homepage
        # no email then go to any contact page
        if email == None:
            # find contact pages
            page_links = store_driver.find_elements(By.TAG_NAME, 'a')
            for link in page_links:
                link_text = link.text.lower()

                if 'contact' in link_text:
                    email = find_email(link.get_attribute('href')) # on contact page
    except:
        print('--------Email Error---------')
        email = None

    # 2. find products

    page_links = store_driver.find_elements(By.TAG_NAME, 'a')
    products = []
    try:
        for link in page_links:
            link_text = link.text.lower()

            if 'product' in link_text:
                # if there is product link on the page and if have childrens
                # then we find the children below it
                # clicking on products and finding products is not possible due to diversity in websites

                parent_element = link.find_element(By.XPATH, './..')
                products_li = parent_element.find_elements(By.XPATH, './/li')
                
                for product in products_li:
                    products.append(" ".join(BeautifulSoup(product.get_attribute('innerHTML'), 'html.parser').text.split()))
    except:
        print('--------Driver Error---------')
        products = []

    try:
        store_driver.quit()
    except:
        print('--------Driver Error closing---------')
        return

    temp = {}
    temp['Email Id'] = email
    temp['Website'] = website

    for product_count in range(len(products)):
        temp[f'Product{product_count + 1}'] = products[product_count]

        # max 30 products
        if product_count >= 30:
            break

    rand_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    website_df = website_df.append(temp, ignore_index=True)
    website_df.to_excel(f'anurag/websites/{rand_name}.xlsx', index=False)

    print(f'{website} done')
