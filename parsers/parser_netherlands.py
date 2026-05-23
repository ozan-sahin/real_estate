#%%
import bs4 as bs
import requests
import pandas as pd
import datetime
import numpy as np
from geopy.geocoders import Nominatim
import re

def parse() -> pd.DataFrame:

    headers = {
        "authority": "www.funda.nl",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,tr;q=0.6,hu;q=0.5",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=0, i",
        "referer": "https://www.funda.nl/en/",
        "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
    }

    dutch_provinces = [
    "provincie-drenthe", "provincie-flevoland", "provincie-friesland",
    "provincie-gelderland", "provincie-groningen", "provincie-limburg",
    "provincie-noord-brabant", "provincie-noord-holland", "provincie-overijssel",
    "provincie-zuid-holland", "provincie-utrecht", "provincie-zeeland"
    ]

    final_list = []

    for province in dutch_provinces:

        params = {"selected_area" : f'["{province}"]',
                "object_type" : '["house", "apartment"]',
                "floor_area" : '',
                "rooms" : '',
                "sort" : "date_down",
                "search_result" : "1"}

        #Find the last page's number
        url = f"https://www.funda.nl/en/zoeken/koop"

        for page in range(1,10,1): #666 is max page number

            # print(f"province: {province}, page number: {str(page)}")
            params["search_result"] = str(page)
            r = requests.get(url, params=params, headers=headers, timeout=10)

            if r.status_code == 200:
                soup = bs.BeautifulSoup(r.text, "lxml")
                divs = soup.findAll('div', class_='@container border-b pb-3')
                if not divs:
                    #print(soup)
                    print(f"unsuccessful to parse page: {str(page)}")
                    break

                for div in divs:
                    if len(div.contents) > 0:

                        link = div.find("a")["href"]
                        title = div.find("span", {"class" : "truncate"}).text.strip()
                        postal = div.find("div", {"class" : "truncate text-neutral-80"}).text.strip()
                        price = div.find("div", {"class" : "mt-2"}).text.strip()
                        details = [ li.text.strip() for li in div.findAll("ul")[-1].findAll("li")]
                        image = div.find("img")["srcset"] if div.find("img") else None

                        final_list.append({"url" : link,
                                        "title" : title,
                                        "postal_raw" : postal,
                                        "price_raw" : price,
                                        "details"  : details,
                                        "image" : image})

            else:
                print(f"unsuccessful to parse page: {str(page)}")


    df = pd.DataFrame(final_list)
    # df = clean(df)
    return df

def clean(df2):

    #Cleaning DataFrame
    df = df2.copy()

    df["address"] = df.title
    df[["postal_code", "postal_code_letter"]] = df.postal_raw.str.split(expand=True).iloc[:,:2]
    df["city"] = df.postal_raw.apply(convert_city)
    
    df["price"] = df.price_raw.apply(convert_price)
    # df["area"] = df.details.str[0].apply(convert_area)
    # df["room"] = df.details.str[-2].apply(convert_room)
    parsed = df["details"].apply(parse_details).apply(pd.Series)
    df = pd.concat([df, parsed], axis=1)
    df["price_per_m2"] = round(df.price / df.area)
    df["full_address"] = df.apply(get_full_address, axis=1)
    #loc = Nominatim(user_agent="Geopy Library")
    #df['lat'], df['lon'] = zip(*df['full_address'].apply(lambda address: get_lat_lon(loc, address)))
    df["country"] = "netherlands"
    df["source"] = "funda"
    df["id"] = df.url.str.split("/").str[-2]
    df["query_date"] = datetime.date.today()
    df["status"] = "active"
    df["url"] = "https://www.funda.nl" + df.url
    df = df.drop(columns=['postal_raw','price_raw','details'])
    return df

def convert_price(price):
    try:
        price = price.split()[1].replace(",", "")
        return float(price)
    except ValueError:
        return np.nan
    
# def convert_room(room):
#     try:
#         room = room.replace(",", ".").strip()
#         return float(room)
#     except ValueError:
#         return np.nan
    
# def convert_area(area):
#     try:
#         area = area.replace("m²", "").replace(".", "").replace(",", ".").strip()
#         return float(area)
#     except AttributeError:
#         return np.nan

def convert_city(postal_raw):
    return " ".join(postal_raw.split()[2:]).strip()

def get_full_address(row):
    return row["address"] + " " + row["postal_code"] + " " + row["postal_code_letter"] + " " + row["city"]
        
def get_lat_lon(loc_object, address: str) -> tuple:
    getLoc = loc_object.geocode(address)
    if getLoc:
        return [float(getLoc.latitude), float(getLoc.longitude)]
    return [None,None]

def parse_details(details):
    result = {"area": None, "bedrooms": None}
    if not details:
        return result

    items = [str(i).strip() for i in details] if isinstance(details, list) else re.findall(r"[\w\s]+m²|\d+|[A-G]\+*", str(details))
    areas = []

    for item in [str(i).strip() for i in items]:
        if "m²" in item:
            val = re.sub(r"[^\d]", "", item)
            if val: areas.append(int(val))
        # elif re.fullmatch(r"[A-G]\+*", item):
        #     result["energy_label"] = item
        elif re.fullmatch(r"\d+", item):
            result["bedrooms"] = int(item)

    if len(areas) >= 1: result["area"] = areas[0]
    # if len(areas) >= 2: result["land_area_m2"] = areas[1]
    return result

#%%

# List of Dutch province names
dutch_provinces = [
    "provincie-drenthe",
    "provincie-flevoland",
    "provincie-friesland",
    "provincie-gelderland",
    "provincie-groningen",
    "provincie-limburg",
    "provincie-noord-brabant",
    "provincie-noord-holland",
    "provincie-overijssel",
    "provincie-zuid-holland",
    "provincie-utrecht",
    "provincie-zeeland"
]

#%%
def analyse(df):

    #Most expensive 20 cities per m2
    df_return = df.groupby("city")["price_per_m2"].agg(["mean","count"]) \
        .query("count > 50").dropna() \
        .sort_values(by="mean", ascending=False).iloc[:20].round()
    
    return df_return
# %%
