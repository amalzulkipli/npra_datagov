import pandas as pd

# URL DATA from data.gov.my
PHARM_URL_DATA = 'https://storage.data.gov.my/healthcare/pharmaceutical_products.parquet'
COSMETIC_URL_DATA = 'https://storage.data.gov.my/healthcare/cosmetic_notifications.parquet'
CANCELLED_URL_DATA = 'https://storage.data.gov.my/healthcare/pharmaceutical_products_cancelled.parquet'

# Function to read and process dataframe
def read_and_process_df(url):
    df = pd.read_parquet(url)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

# Read and process dataframes
pharm_df = read_and_process_df(PHARM_URL_DATA).iloc[2:]
cosmetic_df = read_and_process_df(COSMETIC_URL_DATA)
cancelled_df = read_and_process_df(CANCELLED_URL_DATA)

# Return pharm_df with description column 'PRESCRIPTION','NON PRESCRIPTION' only
rx_pharm = pharm_df[pharm_df['description'].isin(['PRESCRIPTION','NON PRESCRIPTION'])]


