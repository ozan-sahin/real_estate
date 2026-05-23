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
                final_list.append({"title" : title,
                                "url" : "https://www.sahibinden.com" + URL,
                                "image" : image,
                                "area" : alan,
                                "price" : price,
                                "publish_date" : publish_date,
                                "location_raw" : location_raw})
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
    df.price = df.price.apply(lambda x: float(x.replace("TL", "").replace("den itibaren", "").replace(".", "")) )
    df["price_EUR"] = df.price * cur
    df["price_EUR"]  = df["price_EUR"].round()
    df[["city", "mahalle"]] = df["location_raw"].apply(lambda row: split_locations(row)).tolist()
    df["location"] = "Turkey"
    df["area"] = df["area"].str.replace(".", "").astype(float)
    df["price_per_m2"] = round(df["price"] / df["area"],0)
    df["price_EUR_per_m2"] = round(df["price_EUR"] / df["area"],2)
    df["currency_conversion"] = cur
    months_dict = {"Ocak": "January","Şubat": "February","Mart": "March","Nisan": "April",
        "Mayıs": "May","Haziran": "June","Temmuz": "July","Ağustos": "August",
        "Eylül": "September","Ekim": "October","Kasım": "November","Aralık": "December"
    }
    for turkish, english in months_dict.items():
        df['publish_date'] = df['publish_date'].str.replace(turkish, english)
    ref_price_per_m2 = df.groupby("city")["price_per_m2"].mean().round().sort_values(ascending=False).to_dict()
    df["ref_price_per_m2"] = df["city"].map(ref_price_per_m2)
    df["ref_price_EUR_per_m2"] = (df["ref_price_per_m2"] * cur).round(0)
    df['sale_ratio'] = df.apply(lambda row: get_sale_ratio(row, ref_price_per_m2), axis=1)
    df["source"] = "sahibinden"
    df['publish_date'] = pd.to_datetime(df['publish_date'], format='%d %B %Y')
    df["query_date"] = datetime.date.today()
    df = df.drop(columns=["location_raw"])
    df = df.drop_duplicates().reset_index(drop=True)

    columns_list = ["title","ad_type","real_estate_type","city","badges","url","image",
                    "source","query_date","price","price_EUR","type","rooms","level",
                    "area","price_per_m2","price_EUR_per_m2","ilce","mahalle",
                    "ref_price_per_m2","sale_ratio"]

    for col in columns_list:
        if col not in df.columns:
            df[col] = None

    df = df[columns_list]
    
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
    ref = mapping[row["city"]]
    return round((row["price_per_m2"] - ref) / ref * -100, 2)

def save(df:pd.DataFrame):
    df.to_csv("delete.csv", index=False, encoding="utf-8-sig", sep=";")
#%%