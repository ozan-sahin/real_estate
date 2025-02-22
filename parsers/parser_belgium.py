import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

def parse() -> pd.DataFrame:

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br'}

    data = []

    for page in range(1, 20): #Hardcoded max number of pages

        url = f'https://www.immoweb.be/en/search/apartment/for-sale?countries=BE&page={str(page)}&orderBy=newest'

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        listings = soup.find_all('article', class_='card--result')

        for listing in listings:
            title = listing.find('h2', class_='card__title').get_text(strip=True)
            price_dict = listing.find('p', class_='card--result__price').find()[":price"]
            price = json.loads(price_dict)['mainValue']
            location = listing.find('p', class_='card__information card--results__information--locality').get_text(strip=True)
            url = listing.find('a', class_='card__title-link')['href']
            image = listing.find('img', class_='card__media-picture')['src'] if listing.find('img', class_='card__media-picture') else None
            bedrooms_tag = listing.find('p', class_='card__information card--result__information card__information--property').find()
            bedrooms = None
            if bedrooms_tag:
                if bedrooms_tag.has_attr(':title'):
                    bedrooms = bedrooms_tag[":title"].replace("`", "").replace("bedrooms", "").replace("bedroom", "").strip()
            area_tag = listing.find('p', class_='card__information card--result__information card__information--property')
            area = area_tag.text.replace('\n', '').replace('·', '').strip() if area_tag else None

            data.append({
                'title': title,
                'price': price,
                'url' : url,
                'location': location,
                'url': url,
                'image': image,
                'bedrooms': bedrooms,
                'area': area
            })

    df = pd.DataFrame(data)
    return df

        
def clean(df: pd.DataFrame) -> pd.DataFrame:
    df[~df["price"].isna()].reset_index(drop=True)
    df['area'] = pd.to_numeric(df['area'], errors='coerce')
    df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce')
    df['price_per_m2'] = round(df['price'] / df['area'],0)
    df['source'] = 'Immoweb'
    df['query_date'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    return df