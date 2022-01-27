# data_scraping


- Files
  - maps_extract.py : searches the keyword and clicks on stores and saves the data (you have to merge the files into one excel file)
  - extract_website_details.py : finds the email and products of websites from the merged file created above and stores website details in separte excel files, again you have to merge the websites and create a website lookup file (as many stores are repeated)
  - helpers.py : helper functions, extracts website function and saves the file (used by above file)
  - merge_all_details : looks for website in the lookup file created above and merges it, creates a final file
  
(Note: You need to merge 3 times, first all the keyword files, second all the website files and lastly need to merge website with stores)
