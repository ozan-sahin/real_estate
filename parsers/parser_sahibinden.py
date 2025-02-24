#%%
import datetime
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

def parse() -> pd.DataFrame:
    with open("sahibinden_istanbul.txt", "r" , encoding="utf8") as file:
        source = file.read()

    soup = BeautifulSoup(source, "lxml")

    final_list = []
    tables = soup.findAll("table", {"id" : "searchResultsTable"})

    for table in tables:
        for item in table.findAll("tr")[1:]:
            img = item.find("img")
            if img:
                if ".jpg" in img["src"] or "iconHasMegaPhotoLarge" in img["src"]:
                    image = img["src"]
                title = item.find("a", {"class" : "classifiedTitle"}).text.strip()
                URL = item.find("a", {"class" : "classifiedTitle"})["href"]
                alan = item.findAll("td", {"class" : "searchResultsAttributeValue"})[0].text.strip()
                #length = item.findAll("td", {"class" : "searchResultsAttributeValue"})[2].text.strip()
                price = item.find("div", {"class" : "classified-price-container"}).text.strip()
                publish_date = item.find("td", {"class" : "searchResultsDateValue"}).text.replace("\n"," ").strip()
                location_raw = item.find("td", {"class" : "searchResultsLocationValue"}).text.replace("\n"," ").strip()
                final_list.append({"Title" : title,
                                "URL" : "https://www.sahibinden.com" + URL,
                                "Image" : image,
                                "Alan" : alan,
                                "Price" : price,
                                "Publish_Date" : publish_date,
                                "Location_Raw" : location_raw})
            else:
                continue
    df = pd.DataFrame(final_list)
    df = clean(df)
    return df

def clean(df2):
    df = df2.copy()
    def get_exchange_ratio(date, source_currency: str, target_currency: str) -> dict:
        url = f"https://api.frankfurter.dev/v1/{date}?base={source_currency}&symbols={target_currency}"
        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.json()["rates"][target_currency]
    cur = get_exchange_ratio(pd.to_datetime("today").strftime("%Y-%m-%d"), "TRY", "EUR")
    #cur = 0.026234934 # Hardcoded currency conversion rate on 22.02.2025
    df.Price = df.Price.apply(lambda x: float(x.replace("TL", "").replace("den itibaren", "").replace(".", "")) )
    df["Price_EUR"] = df.Price * cur
    df["Price_EUR"]  = df["Price_EUR"].round()
    df[["City", "County"]] = df["Location_Raw"].apply(lambda row: split_locations(row)).tolist()
    df["Location"] = "Turkey"
    df["Alan"] = df["Alan"].str.replace(".", "").astype(float)
    df["Price_per_m2"] = round(df["Price"] / df["Alan"],0)
    df["Price_EUR_per_m2"] = round(df["Price_EUR"] / df["Alan"],2)
    df["Currency_Conversion"] = cur
    months_dict = {"Ocak": "January","Şubat": "February","Mart": "March","Nisan": "April",
        "Mayıs": "May","Haziran": "June","Temmuz": "July","Ağustos": "August",
        "Eylül": "September","Ekim": "October","Kasım": "November","Aralık": "December"
    }
    for turkish, english in months_dict.items():
        df['Publish_Date'] = df['Publish_Date'].str.replace(turkish, english)
    ref_price_per_m2 = df.groupby("City")["Price_per_m2"].mean().round().sort_values(ascending=False).to_dict()
    df["Ref_price_per_m2"] = df["City"].map(ref_price_per_m2)
    df['Sale_ratio'] = df.apply(lambda row: get_sale_ratio(row, ref_price_per_m2), axis=1)
    df["Source"] = "sahibinden"
    df['Publish_Date'] = pd.to_datetime(df['Publish_Date'], format='%d %B %Y')
    df["Query_Date"] = datetime.date.today()
    df = df.drop(columns=["Location_Raw"])
    df = df = df.drop_duplicates().reset_index(drop=True)
    return df

def split_locations(row):
    ls =  re.findall(r'[A-ZÇĞİÖŞÜ][^A-ZÇĞİÖŞÜ]*', row)
    if len(ls) == 1:
        ls.append(None)
    if len(ls) == 3:
        ls = ls[:-1]
    if len(ls) == 4:
        ls = ls[:-2]
    return ls


def get_sale_ratio(row:pd.DataFrame, mapping) -> pd.DataFrame:
    ref = mapping[row["City"]]
    return round((row["Price_per_m2"] - ref) / ref * -100, 2)

#%%