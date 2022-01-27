from maps_extract import find_stores
import pandas as pd
from concurrent import futures
from os import listdir
from os.path import isfile, join

local_keywords_df = pd.read_excel('files/templates/LOCAL GOOGLE KEYWORD.xlsx')
business_type_df = pd.read_excel('files/templates/Business Type.xlsx')
Top_Cities_df = pd.read_excel('files/templates/Top Cities_list.xlsx')

google_keyword = local_keywords_df.at[0, 'mcat_keywords']

### Below is a list of done keywords, business types and cities
todo_business = ['Manufacturer', 'Exporter', 'Wholesaler']

done_cities = ['Agra', 'Ahmedabad', 'Belgaum']

last_city = ''
last_city_gone = True
####

keywords = []
for index, business_type in business_type_df.iterrows():
    if not(business_type['Business Type'] in todo_business):
        continue

    for index2, city in Top_Cities_df.iterrows():
        # if city['Gl_City_Name'] == last_city:
        #     last_city_gone = True
        #     continue # skip the last city

        # if not(last_city_gone):
        #     continue

        keyword = google_keyword + ' ' + business_type['Business Type'] + ' in ' + city['Gl_City_Name']
        keywords.append(keyword)

### continuing from next files
mypath = 'files/extracted/'
done_files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
keywords = [k for k in keywords if not(f'{k}.xlsx' in done_files)]
# keywords.remove('Pneumatic Stapler Distributor in Manglore')
# keywords = ['Pneumatic Stapler Supplier in Coimbatore']

print(len(keywords))


## max_worker refer to how many instances you want to execute
## concurrently. Set it to 1 if it lags on higher value

########### PARRALLEL EXECUTION ###########
with futures.ThreadPoolExecutor(max_workers=3) as executor: # default/optimized number of threads
    titles = list(executor.map(find_stores, keywords))
    # find_stores(keyword, google_keyword)