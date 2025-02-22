#%%
import pandas as pd
import numpy as np
import timeit
from sqlalchemy import create_engine, MetaData, inspect
import parser_france

start = timeit.default_timer()
parsers = [parser_france]
dfList = []

for parser in parsers:
    dfTemp = parser.parse()
    dfTemp = parser.clean(dfTemp)
    dfList.append(dfTemp)

df = pd.concat(dfList)
stop = timeit.default_timer()
print('Time ' + parser_france.__name__ + ": ", int(stop - start))

#%%
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets', \
         "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("sailing-analytics-425909-708f3b5e87ff.json",scope)
client = gspread.authorize(creds)

sheet = client.open("real_estate_table_france").sheet1
data = sheet.get_all_records()
existing_data_google_sheets = pd.DataFrame(data)

columns_to_compare = ['url']

new_rows = df[~df[columns_to_compare].apply(tuple, axis=1) \
                    .isin(existing_data_google_sheets[columns_to_compare] \
                    .apply(tuple, axis=1))].drop_duplicates().reset_index(drop=True)

new_rows["query_date"] = new_rows["query_date"].astype(str)
sheet.append_rows(new_rows.replace(np.inf, np.nan).fillna("").values.tolist())

#%%
