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

    url = "https://www.rightmove.co.uk/major-cities.html"

    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')

    cities = soup.find_all('section', class_='majorCities_linkGroup__Vkdnk')
    cities = [city.find("a")["href"] for city in cities]

    baseUrl = 'https://www.rightmove.co.uk'

    data = []

    for city in cities:
        for page in range(1,4):
            response = requests.get(baseUrl + city + f'?index={str(page*24)}&sortType=6')
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all listings
            listings = soup.find_all('div', class_='l-searchResult is-list')

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
    def get_rooms(row):
        if 'bedroom' in row['title']:
            return int(row['title'].split(' ')[0]) + 1
        elif 'studio' in row['title']:
            return 1
        return None
    df["rooms"] = df.apply(get_rooms, axis=1)
    df["estate_type"] = df["title"].str.split().str[-3]

    def split_details(row):
        bedrooms = int(re.search(r'(\d+)br', row["details"]).group(1)) if 'br' in row["details"] else None
        bathrooms = int(re.search(r'(\d+)ba', row["details"]).group(1)) if 'ba' in row["details"] else None
        level = int(re.search(r'(\d+)(?:th|nd|st)', row["details"]).group(1)) if re.search(r'(\d+)(?:th|nd|st)', row["details"]) else None
        if level is None and row["details"].startswith("G"):
            level = 0
        return [level, bedrooms, bathrooms]
    
    df[["level", "rooms", "bathrooms"]] = df.apply(split_details, axis=1, result_type="expand")
    df['source'] = 'rightmove'
    df['query_date'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    return df

#%%