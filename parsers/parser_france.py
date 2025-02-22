import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

def parse() -> pd.DataFrame:

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br'}

    data = []

    for page in range(1,20): #400 hardcoded max pages

        url = f"https://www.french-property.com/properties-for-sale?start_page={page}"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all listings
        listings = soup.find('div', class_='search-results-properties').findAll("li", class_="property_listing")

        for listing in listings:
            title = listing.find('h3').get_text(strip=True)
            url = listing.find('h3').find('a')['href']
            region = listing.find('span', class_='region').get_text(strip=True)
            department = listing.find('span', class_='department').get_text(strip=True)
            location_raw = listing.find('span', class_='commune').get_text(strip=True)
            desc = listing.find('div', class_='description').get_text(strip=True)
            bedrooms = listing.find('i', {'title' : 'Bedrooms'}).find_next().get_text(strip=True) if listing.find('i', {'title' : 'Bedrooms'}) else None
            bathrooms = listing.find('i', {'title' : 'Bathrooms'}).find_next().get_text(strip=True) if listing.find('i', {'title' : 'Bathrooms'}) else None
            area = listing.find('i', {'title' : 'Habitable Size'}).find_next().get_text(strip=True) if listing.find('i', {'title' : 'Habitable Size'}) else None
            land_area = listing.find('i', {'title' : 'Land Size'}).find_next().get_text(strip=True) if listing.find('i', {'title' : 'Land Size'}) else None
            price = listing.find('div', class_='price').get_text(strip=True)
            image = listing.find('img', class_="lazyload")['data-src'] if listing.find('img', class_="lazyload") else None

            data.append({
                'title': title,
                'price_raw': price,
                'url': 'https://www.french-property.com' + url,
                'region': region,
                'municipality_raw': department,
                'location': location_raw,
                'desc': desc,
                'bedrooms_raw': bedrooms,
                'bathrooms_raw': bathrooms,
                'area_raw': area,
                'land_area_raw': land_area,
                'image': image
            })

    df = pd.DataFrame(data)
    return df

def clean(df:pd.DataFrame) -> pd.DataFrame:
    df = df[~df.price_raw.str.contains("POA")].reset_index(drop=True)
    df['price'] = df['price_raw'].str.replace('€', '').str.replace(',', '').str.strip().astype(float)
    df['bedrooms'] = df['bedrooms_raw'].str.extract(r'(\d+)').astype(float)
    df['bathrooms'] = df['bathrooms_raw'].str.extract(r'(\d+)').astype(float)
    df['area'] = df['area_raw'].str.extract(r'(\d+)').astype(float)
    df['price_per_m2'] = round(df['price'] / df['area'],0)
    df['land_area'] = df['land_area_raw'].str.replace(",","").str.extract(r'(\d+)').astype(float)
    df['municipality'] = df['municipality_raw'].str.extract(r':\s*(.*?)\s*\(')
    df['source'] = 'french-property.com'
    df['query_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
    df = df.drop(['price_raw', 'bedrooms_raw', 'bathrooms_raw', 'area_raw', 'land_area_raw', 'municipality_raw'], axis=1)
    return df