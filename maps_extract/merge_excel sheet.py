# ## Clean the data
# ## 1. add stores from one store lists
# ## 2. remove the duplicate rows
# ## 3. find email and products from website


# from os import listdir
# from os.path import isfile, join
# import pandas as pd

# mypath = 'anurag/extracted/extracted'
# onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

# serial_num = 1
# output_df = pd.read_excel('files/templates/Output_file.xlsx')

# files = [onlyfiles[-1]] + onlyfiles[:-1]

# print(files)
# for f in files:
#     temp_df = pd.read_excel(f'anurag/extracted/extracted/{f}')
#     for idx, row in temp_df.iterrows():
#         row['S. No.'] = serial_num
#         serial_num += 1
#         output_df = output_df.append(row, ignore_index=True)

# output_df.to_excel('anurag/Pneumatic Stapler Merged.xlsx', index=False)


# Helper module
# it contains functions which supplement the data extraction
# so, the funtionality of both the functions could remain separate

import re
import requests
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

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
    store_driver = selenium.webdriver.Chrome()
    store_driver.get(website)

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

    # 2. find products

    page_links = store_driver.find_elements(By.TAG_NAME, 'a')
    products = []
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

    store_driver.quit()
    return (email, products)


