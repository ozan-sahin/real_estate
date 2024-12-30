#%%
import pandas as pd
import numpy as np
import timeit
from sqlalchemy import create_engine, MetaData, inspect
import parsers.parser_immowelt_version2 as immowelt

start = timeit.default_timer()
states = [ f"AD04DE{str(i)}" for i in range(1,17)]
# states = ["AD04DE5"]
dfList = []

for state in states:
    dfTemp = immowelt.parse(state)
    dfList.append(dfTemp)

df = pd.concat(dfList)
df = immowelt.clean_data(df)
stop = timeit.default_timer()
print('Time ' + immowelt.__name__ + ": ", int(stop - start))

#%%
# Create a SQLite database engine
engine = create_engine('sqlite:///germany_real_estate_database_v2.db', echo=True)  # echo=True will log SQL queries

# Define metadata
metadata = MetaData()
# Create an Inspector
inspector = inspect(engine)

existing_data = pd.read_sql('SELECT * FROM main_table', engine)
columns_to_compare = ['id']

deleted_ads = existing_data[~existing_data[columns_to_compare].apply(tuple, axis=1) \
                           .isin(df[columns_to_compare].apply(tuple, axis=1))] \
                           .drop_duplicates()

if not inspector.has_table('main_table'):
    metadata.create_all(engine)
    df.to_sql('main_table', engine, if_exists='append', index=False)
else:
    # Identify rows in the DataFrame that are not already in the database
    new_rows = df[~df[columns_to_compare].apply(tuple, axis=1).isin(existing_data[columns_to_compare].apply(tuple, axis=1))].drop_duplicates().reset_index(drop=True)

    # Insert the new rows into the database
    if not new_rows.empty:
        new_rows.to_sql('main_table', engine, if_exists='append', index=False)

#%%
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets', \
         "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("sailing-analytics-425909-708f3b5e87ff.json",scope)
client = gspread.authorize(creds)

sheet = client.open("real_estate_table_version2").sheet1
data = sheet.get_all_records()
existing_data_google_sheets = pd.DataFrame(data)

columns_to_compare = ['id']

new_rows = df[~df[columns_to_compare].apply(tuple, axis=1) \
                    .isin(existing_data_google_sheets[columns_to_compare] \
                    .apply(tuple, axis=1))].drop_duplicates().reset_index(drop=True)

new_rows["query_date"] = new_rows["query_date"].astype(str)
new_rows["creation_date"] = new_rows["creation_date"].astype(str)
new_rows["update_date"] = new_rows["update_date"].astype(str)
sheet.append_rows(new_rows.replace(np.inf, np.nan).fillna("").values.tolist())

# %%