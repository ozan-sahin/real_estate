#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def parse() -> pd.DataFrame:

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br'}

    portgual_districts = [
        "aveiro-distrito", "beja-distrito", "braga-distrito", "braganca-distrito", "castelo-branco-distrito",
        "coimbra-distrito", "evora-distrito", "faro-distrito", "guarda-distrito", "leiria-distrito", "lisboa-distrito",
        "portalegre-distrito", "porto-distrito", "santarem-distrito", "setubal-distrito", "viana-do-castelo-distrito",
        "vila-real-distrito", "viseu-distrito","acores", "madeira-ilha"
    ]

    data = []

    for district in portgual_districts:

        base_url = f"https://www.idealista.pt/en/comprar-casas/{district}/"

        for page in range(1,10): # 60 pages max.
            if page == 1:
                param = "?ordem=atualizado-desc"
            else:
                param = f"pagina-{str(page)}?ordem=atualizado-desc"
            print(base_url + param)
            if district == "acores":
                response = requests.get(f"https://www.idealista.pt/en/geo/comprar-casas/{district}/" + param, headers=headers, timeout=10)
                time.sleep(2)
            else:
                try:
                    response = requests.get(base_url + param, headers=headers, timeout=10)
                except (ConnectionError, requests.exceptions.ReadTimeout):
                    print('ConnectionError')
                    continue
            if response.status_code != 200:
                print('Error', response.status_code)
                break
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = soup.find_all('article', class_='item')

            for listing in listings:
                title = listing.find('a', class_='item-link').get_text(strip=True)
                url = listing.find('a', class_='item-link')['href']
                image = listing.find('img')['src'] if listing.find('img') else None
                estate_type = title.split(' in ')[0]
                address = title.split(' in ')[-1]
                price = listing.find('span', class_='item-price').get_text(strip=True)
                details = listing.find_all('span', class_='item-detail')
                area = details[1].get_text(strip=True) if len(details) > 1 and 'm²' in details[1].get_text(strip=True) else None
                room = details[0].get_text(strip=True) if 'T' in details[0].get_text(strip=True) else None
                other_details = details[2].get_text(strip=True) if len(details) > 2 else None
                
                data.append({
                    'url': "https://www.idealista.pt" + url,
                    'title': title,
                    'address': address,
                    'district': district,
                    'estate_tpye' : estate_type,
                    'price': price,
                    'details': details,
                    'area': area,
                    'room': room,
                    'other': other_details,
                    'image': image
                })
            
    df = pd.DataFrame(data)
    return df

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df["price"] = df["price"].str.replace('€','').str.replace(',','').astype(float)
    df["area"] = df["area"].str.replace('m²','').str.replace(',','').astype(float)
    df["price_per_m2"] = round(df.price / df.area)
    df["room"] = df.room.str.replace('T', '').str.strip().astype(float)
    # df[~df["price"].isna()].reset_index(drop=True)
    # df['area'] = pd.to_numeric(df['area'], errors='coerce')
    # df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce')
    # df['price_per_m2'] = round(df['price'] / df['area'],0)
    df['source'] = 'idealista'
    df['query_date'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    return df

#%%