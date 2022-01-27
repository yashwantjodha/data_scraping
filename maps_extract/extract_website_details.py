import pandas as pd
from helpers import *
from concurrent import futures

# Code to extrat details from the website...

file_df = pd.read_excel('anurag/Pneumatic Stapler Merged.xlsx') # file with websites row
websites = []

for idx, row in file_df.iterrows():
    if type(row['Website']) == str:
         websites.append(row['Website'])


uniq_websites = list(set(websites))

print(len(uniq_websites))

# max_worker here defines number of parrallel operations you want to do
with futures.ThreadPoolExecutor(max_workers=5) as executor: # default/optimized number of threads
    titles = list(executor.map(website_details, uniq_websites))




