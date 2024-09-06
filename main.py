import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from requests.exceptions import RequestException
from urllib3.exceptions import HTTPError

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

# take first 5 rows of rx_pharm
rx_test = rx_pharm.head(5)

# Function to get the first word of a string
def get_first_word(text):
    return text.split()[0] if isinstance(text, str) else ""

# Function to get MIMS class for a given drug
def get_mims_class(drug_name, is_brand=True, max_retries=3):
    base_url = "https://www.mims.com/malaysia/drug/info/"
    url = f"{base_url}{drug_name}"
    if not is_brand:
        url += "?mtype=generic"
    
    logging.info(f"Requesting URL: {url}")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            logging.info(f"Response status code: {response.status_code}")
            logging.info(f"Response URL: {response.url}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple methods to find MIMS Class
            mims_class = None
            
            # Method 1: Look for specific div structure
            mims_class_header = soup.find('div', class_='monograph-section-header', string='MIMS Class')
            if mims_class_header:
                content = mims_class_header.find_next_sibling('div', class_='monograph-section-content')
                if content:
                    class_link = content.find('a', class_='color-red')
                    if class_link:
                        mims_class = class_link.text.strip()
            
            # Method 2: Search for any 'MIMS Class' text and nearby content
            if not mims_class:
                mims_class_text = soup.find(string='MIMS Class')
                if mims_class_text:
                    parent = mims_class_text.find_parent()
                    next_sibling = parent.find_next_sibling()
                    if next_sibling:
                        mims_class = next_sibling.text.strip()
            
            if mims_class:
                logging.info(f"MIMS class found: {mims_class}")
                return mims_class
            else:
                logging.info("MIMS class not found in the page")
                logging.debug("HTML content:")
                logging.debug(soup.prettify())
        
        except (RequestException, HTTPError) as e:
            logging.error(f"Error occurred on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                logging.error("Max retries reached. Unable to fetch data.")
                return "Not found"
            time.sleep(random.uniform(1, 3))  # Wait before retrying
    
    return "Not found"

# Function to get drug MIMS class
def get_drug_mims_class(row):
    logging.info(f"Processing row: {row['product']}")
    
    # Check product column (brand name)
    if pd.notna(row['product']):
        brand_name = row['product'].split()[0]  # Get first word
        logging.info(f"Trying brand name: {brand_name}")
        mims_class = get_mims_class(brand_name, is_brand=True)
        if mims_class != "Not found":
            return mims_class
    
    # If brand not found, check active_ingredient column (generic name)
    if pd.notna(row['active_ingredient']):
        generic_name = row['active_ingredient'].split()[0]  # Get first word
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