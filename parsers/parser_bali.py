#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def parse() -> pd.DataFrame:

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br'}

    data = []

    # Fetch the webpage content
    for page in range(1,25):
            url = f'https://propertia.com/page/{page}/?sortby=d_date'
            response = requests.get(url, headers=headers)

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'lxml')
            listings = soup.findAll("div", {"class" : "item-listing-wrap"})
            for listing in listings:
                temp = {}
                title = listing.find('h2').get_text(strip=True)
                image = listing.find('img')['src'] if listing.find('img') else None
                parent_tag = listing.find('img').parent if listing.find('img') else None
                url = parent_tag.get("href") if parent_tag else None
                address = listing.find('address').get_text(strip=True)
                details = listing.find('ul', {'class' : 'item-amenities'})
                for detail in details.findAll("li"):
                    temp.update({detail.get("class")[0] : detail.text})
                for label in listing.find("div", {"class" : "labels-wrap"}).findAll("a"):
                    temp.update({label.get("class")[0] : label.text.capitalize()})

                temp.update({
                    'url': url,
                    'title': title,
                    'address': address,
                    'image': image,
                    'source' : 'propertia.com'
                })

                data.append(temp)

    df = pd.DataFrame(data)
    return df

def clean(df : pd.DataFrame)->pd.DataFrame:

    df["id"] = df["h-property-id"].str.split("ID: ", expand=True)[1]
    df["land-area"] = pd.to_numeric(
    df["h-land-area"].str.split(expand=True)[0].str.replace(",", "."),errors='coerce') * 100

    
    def IDR_EUR_currency()->float:
        source_currency = "IDR"
        target_currency = "EUR"
        response = requests.get(f"https://www.x-rates.com/calculator/?from={source_currency}&to={target_currency}&amount=1")
        soup = BeautifulSoup(response.text, "lxml")
        
        text1 = soup.find(class_="ccOutputCode").previous_sibling
        #text2 = soup.find(class_="ccOutputCode").get_text(strip=True)
        rate = "{}".format(text1)
        return float(rate)

    df["price"] = pd.to_numeric(df["item-price"].str.replace(",", "", regex=False) \
                                .str.replace("IDR", "", regex=False) \
                                .str.replace(".", "", regex=False) \
                                .str.strip().replace("", None, regex=False) \
                                ,errors='coerce') * IDR_EUR_currency()
    df["room"] = df["h-beds"].str.replace("BEDS:", "").astype(float)
    df["area"] = df["h-area"].str.replace("M2", "").str.replace("m²","").str.replace("m2","").str.replace(",","").astype(float)
    df["price_per_m2"] = df["price"] / df["area"]
    df["label-status"] = df["label-status"].str.strip()
    df["hz-label"] = df["hz-label"].str.strip()
    df["source"] = "propertia.com"
    df["query_date"] = pd.Timestamp.today().date().strftime("%Y-%m-%d")
    columns_drop = ["h-property-id", "h-land-area", "item-price" ,  "h-beds" , "h-area"]
    df.drop(columns=columns_drop, inplace=True)

    return df

def save(df:pd.DataFrame):
    df.to_csv("delete.csv", index=False, encoding="utf-8-sig", sep=";")
#%%