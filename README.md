# Title:
Classifying medication into its class group

# Objective:
1. Classify medication into its class group based on its product name or active ingredients
2. To ease business treemap generation
3. To ease sales analytics and forecasting

# Data source:
1. MIMS Malaysia
2. NPRA data.gov.my

# Flow Draft:
1. Collect data from data.gov.my
- Get all NPRA approved product name and its active ingredients
2. Check if the product name or active ingredients is in the MIMS Malaysia by scraping the MIMS Malaysia website
- If product name available, then classify the medication into its class group
- If it is not, use active ingredients, then classify the medication into its class group
3. Save data into csv file
