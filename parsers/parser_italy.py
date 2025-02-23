#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd

def parse() -> pd.DataFrame:

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br'}

    italy_provinces = ['agrigento-provincia', 'alessandria-provincia', 'alpi-marittime-costa-azzurra', 'ancona-provincia',
                    'aosta-provincia', 'arezzo-provincia', 'ascoli-piceno-provincia', 'asti-provincia',
                    'avellino-provincia', 'bari-provincia', 'barletta-andria-trani', 'belluno-provincia',
                    'benevento-provincia', 'bergamo-provincia', 'biella-provincia', 'bologna-provincia',
                    'bolzano-bozen-provincia', 'brescia-provincia', 'brindisi-provincia', 'cagliari-provincia',
                    'caltanissetta-provincia', 'campobasso-provincia', 'canton-ticino', 'caserta-provincia', 'catania-provincia',
                    'catanzaro-provincia', 'chieti-provincia', 'como-provincia', 'cosenza-provincia', 'cremona-provincia',
                    'crotone-provincia', 'cuneo-provincia', 'enna-provincia', 'fermo-provincia', 'ferrara-provincia',
                    'firenze-provincia', 'foggia-provincia', 'forli-cesena', 'frosinone-provincia', 'genova-provincia',
                    'gorizia-provincia', 'grosseto-provincia', 'imperia-provincia', 'isernia-provincia', 'l-aquila-provincia',
                    'la-spezia-provincia', 'latina-provincia', 'lecce-provincia', 'lecco-provincia', 'livorno-provincia',
                    'lodi-provincia', 'lucca-provincia', 'macerata-provincia', 'mantova-provincia', 'massa-carrara',
                    'matera-provincia', 'messina-provincia', 'milano-provincia', 'modena-provincia', 'monza-brianza',
                    'napoli-provincia', 'novara-provincia', 'nuoro-provincia', 'oristano-provincia', 'padova-provincia',
                    'palermo-provincia', 'parma-provincia', 'pavia-provincia', 'perugia-provincia', 'pesaro-urbino',
                    'pescara-provincia', 'piacenza-provincia', 'pisa-provincia', 'pistoia-provincia', 'pordenone-provincia',
                    'potenza-provincia', 'prato-provincia', 'ragusa-provincia', 'ravenna-provincia', 'reggio-calabria-provincia',
                    'reggio-emilia-provincia', 'rieti-provincia', 'rimini-provincia', 'roma-provincia', 'rovigo-provincia',
                    'salerno-provincia', 'san-marino-provincia', 'sassari-provincia', 'savona-provincia', 'siena-provincia',
                    'sondrio-provincia', 'sud-sardegna', 'siracusa-provincia', 'taranto-provincia', 'teramo-provincia',
                    'terni-provincia', 'trapani-provincia', 'trento-provincia', 'treviso-provincia', 'trieste-provincia',
                    'torino-provincia', 'udine-provincia', 'varese-provincia', 'venezia-provincia', 'verbano-cusio-ossola',
                    'vercelli-provincia', 'verona-provincia', 'vibo-valentia-provincia', 'vicenza-provincia', 'viterbo-provincia']

    data = []

    for province in italy_provinces:

        base_url = f"https://www.idealista.it/en/vendita-case/{province}/"

        for page in range(1,5): # 60 pages max.
            if page == 1:
                param = "?ordine=pubblicazione-desc"
            else:
                param = f"lista-{str(page)}.htm?ordine=pubblicazione-desc"
            print(str(page) + " " + province)
            response = requests.get(base_url + param, headers=headers)
            if response.status_code != 200:
                print('Error', response.status_code)
                break
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = soup.find_all('article', class_='item')
            if len(listings) == 0:
                print(f'No more listings found in {province}')
                break

            for listing in listings:
                title = listing.find('a', class_='item-link').get_text(strip=True)
                url = listing.find('a', class_='item-link')['href']
                image = listing.find('img')['src'] if listing.find('img') else None
                estate_type = title.split(' in ')[0]
                address = title.split(' in ')[-1]
                price = int(listing.find('span', class_='item-price').get_text(strip=True).replace('€','').replace(',','').strip())
                details = listing.find_all('span', class_='item-detail')
                area = int(details[1].get_text(strip=True).replace('m²', '').replace(',','').strip()) if len(details) > 1 and 'm²' in details[1].get_text(strip=True) else None
                price_per_m2 = round(price / area) if area else None
                room = int(details[0].get_text(strip=True).replace('rooms', '').strip()) if 'rooms' in details[0].get_text(strip=True) else None
                other_details = details[2].get_text(strip=True) if len(details) > 2 else None
                
                data.append({
                    'url': "https://www.idealista.it" + url,
                    'title': title,
                    'address': address,
                    'province': province,
                    'estate_tpye' : estate_type,
                    'price': price,
                    'price_per_m2': price_per_m2,
                    'details': details,
                    'area': area,
                    'room': room,
                    'other': other_details,
                    'image': image
                })

    df = pd.DataFrame(data)
    return df

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df['source'] = 'idealista'
    df['query_date'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    return df

#%%