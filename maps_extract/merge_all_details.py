import pandas as pd
import tqdm



output_df = pd.read_excel(r'files/templates/Output_file.xlsx')
website_df = pd.read_excel(r'anurag/Website Merged.xlsx')
stores_df = pd.read_excel(r'anurag/Pneumatic Stapler Merged.xlsx')

for idx, row in stores_df.iterrows():
    store_website = row['Website']
    if type(store_website) == str:
        website_row = website_df.loc[website_df['Website'] == store_website]
        
        if website_row['Email Id'].values.size != 0:
            row['Email Id'] = website_row['Email Id'].values[0]

        for i in range(1, 31):
            try:
                row[f'Product{i}'] = website_row[f'Product{i}'].values[0]
            except:
                pass


    output_df = output_df.append(row, ignore_index=True)


output_df.to_excel('output_files/Pneumatic Stapler final.xlsx', index=False)