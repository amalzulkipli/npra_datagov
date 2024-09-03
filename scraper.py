from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random


def scrape_mims_malaysia():
    url = "https://www.mims.com/malaysia/drug/search?q=Antacids%2C%20Antireflux%20Agents%20%26%20Antiulcerants&mtype=brand"
    
    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Load the search page
        driver.get(url)
        
        # Wait for the content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "drug-search-result"))
        )
        
        # Get the page source after JavaScript has rendered the content
        page_source = driver.page_source
        
        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find all drug items
        drug_items = soup.find_all('div', class_='search-border-style')
        
        # Extract information from each drug item
        drugs = []
        for item in drug_items:
            name = item.find('h1').text.strip()
            mims_class_element = item.find('span', class_='class-header', string='MIMS Class : ')
            if mims_class_element:
                mims_class = mims_class_element.find_next('span').text.strip()
            else:
                mims_class = "N/A"
            
            # Get the link to the drug's page
            drug_link = item.find('a')['href']
            drug_url = f"https://www.mims.com{drug_link}"
            
            # Navigate to the drug's page
            driver.get(drug_url)
            
            # Wait for the new page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get the HTML of the new page
            new_page_source = driver.page_source
            
            # Print the HTML of the new page for debugging
            print(f"HTML for {name}:\n{new_page_source}\n{'-'*80}\n")
            
            # Parse the new page with BeautifulSoup
            new_soup = BeautifulSoup(new_page_source, 'html.parser')
            
            # Extract the "Contents" and "ATC Classification"
            contents = new_soup.find('div', class_='monograph-section-header', string='Contents')
            if contents:
                contents_value = contents.find_next('div', class_='monograph-section-content').text.strip()
            else:
                contents_value = "N/A"
            
            atc_classification = new_soup.find('div', class_='monograph-section-header', string='ATC Classification')
            if atc_classification:
                atc_classification_value = atc_classification.find_next('div', class_='monograph-section-content').text.strip()
            else:
                atc_classification_value = "N/A"
            
            # Append the extracted information to the drugs list
            drugs.append({
                'name': name,
                'mims_class': mims_class,
                'contents': contents_value,
                'atc_classification': atc_classification_value
            })
            
            # Add a random delay between 1 to 20 seconds
            time.sleep(random.randint(1, 20))
        
        return drugs
    
    finally:
        # Close the browser
        driver.quit()

# Run the scraper
drug_list = scrape_mims_malaysia()

# Print the results
for drug in drug_list:
    print(f"Name: {drug['name']}")
    print(f"MIMS Class: {drug['mims_class']}")
    print(f"Contents: {drug['contents']}")
    print(f"ATC Classification: {drug['atc_classification']}")
    print("---")
    
print(f"Total drugs scraped: {len(drug_list)}")


brand_url_var1 = "https://www.mims.com/malaysia/drug/info/Resicalm"
brand_url_var2 = "https://www.mims.com/malaysia/drug/info/BETANOR"
generic_url = "https://www.mims.com/malaysia/drug/info/chlorphenamine?mtype=generic"

# Set up Chrome options for headless browsing
chrome_options = Options()
chrome_options.add_argument("--headless")

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

# return the html of the brand_url page    
driver.get(brand_url_var2)
html = driver.page_source

# save html page to file name brand_url.html
with open('brand_url_var2.html', 'w') as f:
    f.write(html)



# return the html of the generic_url page
driver.get(generic_url)
html = driver.page_source
        
# save html page to file name generic_url.html
with open('generic_url.html', 'w') as f:
    f.write(html)

driver.quit()
