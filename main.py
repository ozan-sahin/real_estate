#%%
import pandas as pd
import numpy as np
import timeit
from sqlalchemy import create_engine, MetaData, inspect
import parser_immowelt as immowelt

start = timeit.default_timer()
states = [ f"AD04DE{str(i)}" for i in range(1,17)]
# states = ["AD04DE5"]
dfList = []

for state in states:
    dfTemp = immowelt.parse(state)
    dfList.append(dfTemp)

df = pd.concat(dfList)
stop = timeit.default_timer()
print('Time ' + immowelt.__name__ + ": ", int(stop - start))

#%%
# Create a SQLite database engine
engine = create_engine('sqlite:///germany_real_estate_database.db', echo=True)  # echo=True will log SQL queries

# Define metadata
metadata = MetaData()
# Create an Inspector
inspector = inspect(engine)

existing_data = pd.read_sql('SELECT * FROM main_table', engine)
columns_to_compare = ['url','makler','address','title','city']

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

sheet = client.open("real_estate_table").sheet1
data = sheet.get_all_records()
existing_data_google_sheets = pd.DataFrame(data)

columns_to_compare = ['url','makler','address','title','city']

new_rows = df[~df[columns_to_compare].apply(tuple, axis=1) \
                    .isin(existing_data_google_sheets[columns_to_compare] \
                    .apply(tuple, axis=1))].drop_duplicates().reset_index(drop=True)

new_rows["query_date"] = new_rows["query_date"].astype(str)
sheet.append_rows(new_rows.replace(np.inf, np.nan).fillna("").values.tolist())

# %%
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets', \
         "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("sailing-analytics-425909-708f3b5e87ff.json",scope)
client = gspread.authorize(creds)

sheet = client.open("real_estate_table").sheet1
data = sheet.get_all_records()
existing_data_google_sheets = pd.DataFrame(data)

# Get today's date
today_date = datetime.datetime.today().strftime('%Y-%m-%d')

existing_tuples = set(existing_data_google_sheets[columns_to_compare].apply(tuple, axis=1))
df_tuples = set(df[columns_to_compare].apply(tuple, axis=1))

# Identify the deleted ads
deleted_tuples = existing_tuples - df_tuples
deleted_ads = existing_data_google_sheets[existing_data_google_sheets[columns_to_compare].apply(tuple, axis=1).isin(deleted_tuples)].drop_duplicates()

# Update status of deleted ads to 'inactive' if there are any
if not deleted_ads.empty:

    # Find the indices of rows to update
    indices_to_update = existing_data_google_sheets.index[existing_data_google_sheets[columns_to_compare].apply(tuple, axis=1).isin(deleted_tuples)].tolist()

    # Update the DataFrame
    existing_data_google_sheets.loc[indices_to_update, 'status'] = 'inactive'
    existing_data_google_sheets.loc[indices_to_update, 'deletion_date'] = today_date

    # Prepare the cell updates
    cell_updates = []
    for index in indices_to_update:
        # Correctly format the range string for Google Sheets
        status_col = existing_data_google_sheets.columns.get_loc('status') + 1
        deletion_date_col = existing_data_google_sheets.columns.get_loc('deletion_date') + 1

        status_cell_range = f"{chr(64 + status_col)}{index + 2}"
        deletion_date_cell_range = f"{chr(64 + deletion_date_col)}{index + 2}"

        cell_updates.append({
            'range': status_cell_range,
            'values': [['inactive']]
        })
        cell_updates.append({
            'range': deletion_date_cell_range,
            'values': [[today_date]]
        })

    # Perform batch update
    sheet.batch_update(cell_updates)

# %%
