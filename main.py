import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import logging

# Set up logging
logging.basicConfig(filename='drug_classification_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# URL DATA from data.gov.my
PHARM_URL_DATA = 'https://storage.data.gov.my/healthcare/pharmaceutical_products.parquet'

# Function to read and process dataframe
def read_and_process_df(url):
    df = pd.read_parquet(url)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

# Read and process dataframes
pharm_df = read_and_process_df(PHARM_URL_DATA).iloc[2:]

# Return pharm_df with description column 'PRESCRIPTION','NON PRESCRIPTION' only
rx_pharm = pharm_df[pharm_df['description'].isin(['PRESCRIPTION','NON PRESCRIPTION'])]

# take first 30 rows of rx_pharm
rx_test = rx_pharm.head(5)

# Function to get the first word of a string
def get_first_word(text):
    return text.split()[0] if isinstance(text, str) else ""

# Function to get MIMS class for a given drug
def get_mims_class(drug_name, is_brand=True):
    if is_brand:
        url = f"https://www.mims.com/malaysia/drug/info/{drug_name}"
    else:
        url = f"https://www.mims.com/malaysia/drug/info/{drug_name}?mtype=generic"
    
    logging.info(f"Requesting URL: {url}")
    
    try:
        response = requests.get(url)
        logging.info(f"Response status code: {response.status_code}")
        logging.info(f"Response URL: {response.url}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the MIMS Class section
        mims_class_header = soup.find('div', class_='monograph-section-header', string='MIMS Class')
        if mims_class_header:
            mims_class_content = mims_class_header.find_next_sibling('div', class_='monograph-section-content')
            if mims_class_content:
                mims_class_link = mims_class_content.find('a', class_='color-red')
                if mims_class_link:
                    mims_class = mims_class_link.text.strip()
                    logging.info(f"MIMS class found: {mims_class}")
                    return mims_class
        
        logging.info("MIMS class not found in the page")
        logging.info("HTML content around MIMS Class section:")
        logging.info(soup.prettify())
        
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
    
    return "Not found"

# Add a new column for MIMS class
def get_drug_mims_class(row):
    logging.info(f"Processing row: {row['product']}")
    
    # Check product column (brand name)
    if pd.notna(row['product']):
        brand_name = row['product'].split(',')[0].strip()  # Take everything before the first comma
        logging.info(f"Trying brand name: {brand_name}")
        mims_class = get_mims_class(brand_name, is_brand=True)
        if mims_class != "Not found":
            return mims_class
    
    # If brand not found, check active_ingredient column (generic name)
    if pd.notna(row['active_ingredient']):
        generic_name = row['active_ingredient'].split('[')[0].strip()  # Take everything before the first '['
        logging.info(f"Trying generic name: {generic_name}")
        mims_class = get_mims_class(generic_name, is_brand=False)
        if mims_class != "Not found":
            return mims_class
    
    # Add intentional pause to avoid being blocked
    pause_time = random.uniform(1, 3)
    logging.info(f"Pausing for {pause_time:.2f} seconds")
    time.sleep(pause_time)
    
    return "Not found"

rx_test['mims_class'] = rx_test.apply(get_drug_mims_class, axis=1)

# Display the result
print(rx_test[['product', 'active_ingredient', 'mims_class']])

# Save the updated dataframe
rx_test.to_csv('rx_test_with_mims_class.csv', index=False)

logging.info("Process completed")

