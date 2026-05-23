#%%
import pandas as pd
import numpy as np
import timeit
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import parsers.parser_greece as greece
import parsers.parser_turkey as turkey
import parsers.parser_belgium as belgium
import parsers.parser_france as france
import parsers.parser_uk as uk
import parsers.parser_italy as italy
import parsers.parser_netherlands as netherlands
import parsers.parser_usa as usa
import parsers.parser_spain as spain
import parsers.parser_bali as bali

# NOT WORKING YET

# import parsers.parser_portugal as portugal

#%%

def upload_to_google_sheets(sheetname:str, df:pd.DataFrame):

    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets', \
            "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("sailing-analytics-425909-708f3b5e87ff.json",scope)
    client = gspread.authorize(creds)

    sheet = client.open(sheetname).sheet1
    data = sheet.get_all_records()
    existing_data_google_sheets = pd.DataFrame(data)

    columns_to_compare = ['url']

    new_rows = df[~df[columns_to_compare].apply(tuple, axis=1) \
                        .isin(existing_data_google_sheets[columns_to_compare] \
                        .apply(tuple, axis=1))].reset_index(drop=True)

    new_rows["query_date"] = new_rows["query_date"].astype(str)
    sheet.append_rows(new_rows.replace(np.inf, np.nan).fillna("").values.tolist())
    print(f"For {sheetname}, {len(new_rows)} new rows added.")

#%%

start = timeit.default_timer()
# parsers = [spain]
parsers = [uk, netherlands, greece, belgium, france, spain, usa, bali]
dfList = []

for parser in parsers:
    print(f"Scraping {parser.__name__}")
    try:
        dfTemp = parser.parse()
        if dfTemp.empty:
            print(f"failed to get {parser.__name__}")
            continue
        dfTemp2 = parser.clean(dfTemp)
        dfList.append(dfTemp2)
        country = parser.__name__.split("_")[-1]
        upload_to_google_sheets(f"real_estate_table_{country}", dfTemp2)
    except Exception as e:
        print(f"Error processing {parser.__name__}: {e}")
        continue
    stop = timeit.default_timer()
    print('Time ' + parser.__name__ + ": ", int(stop - start))

# %%

start = timeit.default_timer()
parsers = [turkey]
dfList_2 = []

for parser in parsers:
    print(f"Scraping {parser.__name__}")

    dfTemp = parser.parse("satilik", "daire", "istanbul-kadikoy")
    dfTemp2 = parser.clean(dfTemp)
    dfList_2.append(dfTemp2)

    dfTemp = parser.parse("satilik", "arsa", "canakkale-gokceada")
    dfTemp2 = parser.clean(dfTemp)
    dfList_2.append(dfTemp2)

    df_final = pd.concat(dfList_2, ignore_index=True)

    country = parser.__name__.split("_")[-1]
    upload_to_google_sheets(f"real_estate_table_{country}", df_final)
    stop = timeit.default_timer()
    print('Time ' + parser.__name__ + ": ", int(stop - start))

# %%