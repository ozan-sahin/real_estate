#%%

import requests
from bs4 import BeautifulSoup
import pandas as pd

def parse() -> pd.DataFrame:

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br'}

    data = []

    params = {'transaction_name': 'buy',
            'item_type': 're_residence',
            'geo_lat_from': 42.21134910950702,
            'geo_lng_from': 30.229145939311962,
            'geo_lat_to': 34.904517973786945,
            'geo_lng_to': 18.4873011385354,
            'sorting' : 'update_desc',
            'page': 1}

    for page in range(1,20): #Hardcoded max number of pages

        # Define the URL of the Spitogatos search page
        url = 'https://www.xe.gr/en/property/results'
        params['page'] = page
        response = requests.get(url, headers=headers, params=params)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all listings
        listings = soup.findAll('div', class_='common-ad')
        if len(listings) == 0:
            print('No more listings')
            break

        for listing in listings:

            title = listing.find("div", {"class": "common-property-ad-title"}).get_text(strip=True)
            price = listing.find("div", {"class": "common-property-ad-price"}).find("span").get_text(strip=True) \
                .replace("\xa0", "").replace("€", "").replace(".", "").strip()
            level = listing.find("div", {"class": "property-ad-level-container"}).get_text(strip=True)
            bedrooms = listing.find("div", {"class": "property-ad-bedrooms-container"}).get_text(strip=True).replace("×", "").strip() \
                if listing.find("div", {"class": "property-ad-bedrooms-container"}) else None
            bathrooms = listing.find("div", {"class": "property-ad-bathrooms-container"}).get_text(strip=True).replace("×", "").strip() \
                if listing.find("div", {"class": "property-ad-bathrooms-container"}) else None
            year = listing.find("div", {"class": "property-ad-construction-year-container"}).get_text(strip=True).replace("×", "").strip() \
                if listing.find("div", {"class": "property-ad-construction-year-container"}) else None
            location = listing.find("div", {"class": "common-property-ad-area-container"}).get_text(strip=True).split("|")[0].strip() 
            type_ = listing.find("div", {"class": "common-property-ad-area-container"}).get_text(strip=True).split("|")[1].strip()
            url = listing.find('a')['href']
            image = listing.find('img')['src']

            data.append({
                'title': title,
                'price': price,
                'level' : level,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'year': year,
                'location': location,
                'type': type_,
                'url': url,
                'image': image,
                'source': 'xe.gr',
                'query_date': pd.to_datetime('today').strftime('%Y-%m-%d')
            })
    df = pd.DataFrame(data)
    return df

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['area'] = df['title'].str.extract(r'(\d+)').astype(int)
    df['price_per_m2'] = round(df['price'] / df['area'],0)
    df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce').fillna(0).astype(int)
    df['bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce').fillna(0).astype(int)
    df['year'] = df['year'].fillna(0).astype(int)
    return df

#%%