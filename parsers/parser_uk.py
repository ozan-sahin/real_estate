#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def parse() -> pd.DataFrame:

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

    url = "https://www.rightmove.co.uk/major-cities.html"

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    cities = soup.find_all('section', class_='majorCities_linkGroup__Vkdnk')
    cities = [city.find("a")["href"] for city in cities]

    baseUrl = 'https://www.rightmove.co.uk'

    data = []

    for city in cities:
        for page in range(1,4):
            response = requests.get(baseUrl + city + f'?index={str(page*24)}&sortType=6', headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if response.status_code != 200:
                print('Error', response.status_code)
                print( response.text)
                break
            
            listings = soup.find_all('div', class_='l-searchResult is-list')

            if len(listings) == 0:
                print('No more listings')
                break

            for listing in listings:
                title = listing.find('h2', class_='propertyCard-title').get_text(strip=True)
                price = listing.find('div', class_='propertyCard-priceValue').get_text(strip=True)
                location = listing.find('address', class_='propertyCard-address').get_text(strip=True)
                details = listing.find('div', class_='propertyCard-description').get_text(strip=True)
                #information = listing.find('div', class_='property-information').get_text(strip=True) if listing.find('div', class_='property-information') else None
                url = listing.find('a', class_='propertyCard-link')['href']
                image = listing.find('div', class_='propertyCard-img').find('img')['src'] if listing.find('div', class_='propertyCard-img') else None

                data.append({
                    'title': title,
                    'price': price,
                    'location': location,
                    'details': details,
                    #'information': information,
                    'url': 'https://www.rightmove.co.uk' + url,
                    'image': image,
                    'county': city.split('/')[-1].replace('.html', '')
                })
            
    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    return df

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df[~df["price"].str.contains("coming soon|POA", case=False, na=False)]
    df["price"] = df["price"].str.replace("£", "").str.replace(",", "").str.strip()
    df["price"] = df["price"].astype(float)
    def get_rooms(row):
        if 'bedroom' in row['title']:
            return int(row['title'].split(' ')[0]) + 1
        elif 'studio' in row['title']:
            return 1
        return None
    df["rooms"] = df.apply(get_rooms, axis=1)
    df["estate_type"] = df["title"].str.split().str[-3]

    def split_information(row):
        #This is not working yet. It has been copied over from Greek parser
        if row["information"]:
            bedrooms = str(re.search(r'(\d+)br', row["information"]).group(1)) if 'br' in row["information"] else None
            bathrooms = str(re.search(r'(\d+)ba', row["information"]).group(1)) if 'ba' in row["information"] else None
            level = str(re.search(r'(\d+)(?:th|nd|st)', row["information"]).group(1)) if re.search(r'(\d+)(?:th|nd|st)', row["information"]) else None
            if level is None and row["information"].startswith("G"):
                level = "0"
        else:
            bedrooms = None
            bathrooms = None
            level = None
        return [level, bedrooms, bathrooms]
    
    def get_area_from_room_number(row):
        # Predefined apartment areas based on room number
        if pd.isna(row["rooms"]):
            return None
        apartment_areas = {1: 43.0, 2: 60.0, 3: 75.0,
                            4: 90.0, 5: 110.0,
                            6: 130.0, 7: 150.0}
        return apartment_areas.get(int(row["rooms"]), row["rooms"] * 35.0)  # Default to 35 sqm per room if not listed
    df["area"] = df.apply(get_area_from_room_number, axis=1)
    def get_exchange_ratio(date, source_currency: str, target_currency: str) -> dict:
        url = f"https://api.frankfurter.dev/v1/{date}?base={source_currency}&symbols={target_currency}"
        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.json()["rates"][target_currency]
    cur = get_exchange_ratio(pd.to_datetime("today").strftime("%Y-%m-%d"), "GBP", "EUR")
    df["price_EUR"] = df.price * cur
    df["price_per_m2"] = round(df["price_EUR"] / df["area"])
    #df[["level", "rooms", "bathrooms"]] = df.apply(split_information, axis=1, result_type="expand")
    df['source'] = 'rightmove'
    df['query_date'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    return df

def save(df:pd.DataFrame):
    df.to_csv("delete.csv", index=False, encoding="utf-8-sig", sep=";")
#%%