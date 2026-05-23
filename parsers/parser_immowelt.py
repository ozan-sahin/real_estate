#%%
import bs4 as bs
import requests
import pandas as pd
import datetime
import re
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def parse(location : str):

    #style.use('ggplot')

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9'}

    params = {"distributionTypes" : "Buy,Buy_Auction", #Rent
              "estateTypes" : "House,Apartment",
              "locations" : location, #AD04DE5: Nord-rhein westfalen, AD08DE2112: Düsseldorf
              "locationsInBuildingExcluded" : "Roof_Storey",
              "numberOfRoomsMin" : "",
              "priceMax" : "",
              "projectTypes" : "Investment,Projected,Resale",
              "spaceMin" : "",
              "yearOfConstructionMin" : "",
              "energyCertificate" : "A_PLUS,A,B,C,D,E",
              "order" : "DateDesc",
              "page" : "1"}

    #Find the last page's number
    url = f"https://www.immowelt.de/classified-search"
    r = requests.get(url, params=params, headers=headers)

    soup = bs.BeautifulSoup(r.text, "lxml")
    page_tag = soup.find_all('button', attrs={'aria-label': lambda x: x and 'seite' in x})
    last_page = min(int(page_tag[-2].text), 333)
    print(str(last_page))
    #Scraping all the pages from immowelt.de
    final_list = []

    for page in range(1,last_page+2,1):
        # print(f"page number: {str(page)}")
        params["page"] = str(page)
        r = requests.get(url, params=params, headers=headers)

        if r.status_code == 200:
            soup = bs.BeautifulSoup(r.text, "lxml")
            divs = soup.findAll("div", {"data-testid" : "serp-card-testid"})
            for div in divs:
                if len(div.contents) > 0:

                    link = div.find("a")["href"]
                    title = div.find("a")["title"]
                    image = div.find("img")["src"] if div.find("img") else None
                    makler = div.find("div", {"data-testid" : "cardmfe-provider-test-id"}).text \
                        if div.find("div", {"data-testid" : "cardmfe-provider-test-id"}) else None
                    address = div.find("div", {"data-testid" : "cardmfe-description-box-address"}).text \
                        if div.find("div", {"data-testid" : "cardmfe-description-box-address"}) else None

                    final_list.append({"url" : link,
                                    "title_raw" : title,
                                    "makler"  : makler,
                                    "address" : address,
                                    "image" : image})

        else:
            print(f"unsuccesful to parse page: {str(page)}")


    df = pd.DataFrame(final_list)
    df = clean(df)
    return df

def clean(df2):

    #Cleaning DataFrame
    df = df2.copy()
    #Necessary for calculations
    df_pivot = get_unit_prices()

    df[["title", "city_raw", "price_raw", "others_"]] = df.title_raw.str.split(" - ", expand=True).iloc[:,:4]
    df = df[~df.title_raw.str.contains("Preis auf Anfrage")]
    df["city"] = df.city_raw.apply(convert_city)
    df["district"] = df.address.apply(convert_address)
    df["postal_code"] = df.address.apply(convert_post)
    df["listing_type"] = df.title.apply(convert_listing)
    df["estate_type"] = df.title.apply(convert_estate_type)
    df["type"] = df.apply(return_keyword, axis=1)
    df["price"] = df.price_raw.apply(convert_price)
    df[["room_raw", "area_raw"]] = df.others_.str.split(", ", expand=True).iloc[:,:-2]
    df["room"] = df.room_raw.apply(convert_room)
    df["area"] = df.area_raw.apply(convert_area)
    df["price_per_m2"] = round(df.price / df.area)
    #---
    df["ref_price"] = df.apply(lambda x: return_ref_price(x, df_pivot), axis=1).round()
    df["sale_ratio"] = round((df.ref_price - df.price_per_m2) / df.ref_price * 100)
    df["ref_rent_price"] = df.apply(lambda x : return_rent_price(x, df_pivot), axis=1).round(2)
    df["return_in_years"] = round(df.price / df.ref_rent_price / df.area / 12, 1)
    df["yield_ratio"] = round(1 / df["return_in_years"] * 100, 2)
    #---
    df["source"] = "immowelt"
    df["query_date"] = datetime.date.today()
    df["status"] = "active"
    df["deletion_date"] = None
    df = df.drop(columns=['title_raw','others_','price_raw','room_raw','area_raw','city_raw'])
    ordered_cols = ['url','makler','address','image','title','city','district','postal_code', \
                    'listing_type','estate_type','type','price','room','area','price_per_m2', \
                    'ref_price','sale_ratio','ref_rent_price','return_in_years', \
                    'yield_ratio','source','query_date','status','deletion_date']
    df = df[ordered_cols]
    return df

def convert_price(price):
    try:
        price = price.replace("€", "").replace(".", "").replace(",", ".").strip()
        return float(price)
    except ValueError:
        return np.nan
    
def convert_room(room):
    try:
        room = room.replace("Zimmer", "").replace(",", ".").strip()
        return float(room)
    except (ValueError, AttributeError):
        return np.nan
    
def convert_area(area):
    try:
        area = area.replace("m²", "").replace(".", "").replace(",", ".").strip()
        return float(area)
    except (ValueError, AttributeError):
        return np.nan

def convert_address(address):
    try:
        address = address.split(",")[-2].strip()
        return re.sub(r'\d', '', address) #removing numbers
    except (IndexError, AttributeError):
        return ""

def convert_city(city):
    try:
        return city.split("/")[0].split("(")[0].strip().capitalize()
    except AttributeError:
        return ""
    
def convert_post(address):
    try:
        post = address.split()[-1].replace("(", "").replace(")", "").strip()
        return str(post)
    except (ValueError, AttributeError):
        return ""
    
def convert_listing(title : str):
    if "kauf" in title.lower():
        return "sale"
    elif "miete" in title.lower():
        return "rent"
    else:
        return ""
    
def convert_estate_type(title : str):
    if "wohnung" in title.lower() or "apartment" in title.lower() or "maisonette" in title.lower():
        return "apartment"
    elif "grundstück" in title.lower():
        return "land"
    else:
        return "house"
    
def return_keyword(row):

    keyword_map = {
        ("sale", "house"): "hauspreise",
        ("sale", "apartment"): "wohnungspreise",
        ("rent", "house"): "mietpreise-haeuser",
        ("rent", "apartment"): "mietspiegel"
    }
    keyword = keyword_map.get((row["listing_type"], row["estate_type"]))
    return keyword

def get_unit_prices():

    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets', \
            "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("sailing-analytics-425909-708f3b5e87ff.json",scope)
    client = gspread.authorize(creds)

    sheet = client.open("unit_price_real_estate").sheet1
    data = sheet.get_all_records()
    existing_data_google_sheets = pd.DataFrame(data)
    existing_data_google_sheets.price_clean = pd.to_numeric(existing_data_google_sheets.price_clean)
    df_pivot = existing_data_google_sheets.pivot_table(index='neighborhood', columns='type', values='price_clean')
    return df_pivot

def return_ref_price(row, df_pivot : pd.DataFrame):
    neighborhood = row["district"].strip().lower().replace(" ", "-").replace("ö","oe").replace("ü","ue").replace("ß","ss")
    city = row["city"].strip().lower().replace(" ", "-").replace("ö","oe").replace("ü","ue").replace("ß","ss")
    type = row["type"]
    try:
        return df_pivot.loc[neighborhood, type]
    except KeyError:
        try:
            return df_pivot.loc[city, type]
        except KeyError:
            return None
        
def return_rent_price(row, df_pivot : pd.DataFrame):
    neighborhood = row["district"].strip().lower().replace(" ", "-").replace("ö","oe").replace("ü","ue").replace("ß","ss")
    city = row["city"].strip().lower().replace(" ", "-").replace("ö","oe").replace("ü","ue").replace("ß","ss")
    if row["estate_type"] == "house":
        type = "mietpreise-haeuser"
    elif row["estate_type"] == "apartment":
        type = "mietspiegel"
    try:
        return df_pivot.loc[neighborhood, type]
    except KeyError:
        try:
            return df_pivot.loc[city, type]
        except KeyError:
            return None

#%%