import pandas as pd

# URL DATA from data.gov.my
PHARM_URL_DATA = 'https://storage.data.gov.my/healthcare/pharmaceutical_products.parquet'
COSMETIC_URL_DATA = 'https://storage.data.gov.my/healthcare/cosmetic_notifications.parquet'
CANCELLED_URL_DATA = 'https://storage.data.gov.my/healthcare/pharmaceutical_products_cancelled.parquet'

# Read the data from the URL
pharm_df = pd.read_parquet(PHARM_URL_DATA)
if 'date' in pharm_df.columns: pharm_df['date'] = pd.to_datetime(pharm_df['date'])
pharm_df = pharm_df.iloc[2:]

cosmetic_df = pd.read_parquet(COSMETIC_URL_DATA)
if 'date' in cosmetic_df.columns: cosmetic_df['date'] = pd.to_datetime(cosmetic_df['date'])

cancelled_df = pd.read_parquet(CANCELLED_URL_DATA)
if 'date' in cancelled_df.columns: cancelled_df['date'] = pd.to_datetime(cancelled_df['date'])

# what unique value are in description column in pharm_df and its count
print(pharm_df['description'].value_counts())

# Return pharm_df with description column 'PRESCRIPTION','NON PRESCRIPTION' only
rx_pharm = pharm_df[pharm_df['description'].isin(['PRESCRIPTION','NON PRESCRIPTION'])]

# length of rx_pharm
len(rx_pharm)

# take first 30 rows of rx_pharm
rx_test = rx_pharm.head(30)



