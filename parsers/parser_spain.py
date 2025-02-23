#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd

def parse() -> pd.DataFrame:

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br'}

    provinces_of_spain = [
        "a-coruna-provincia", "la-rioja", "las-palmas", "alava", "albacete-provincia", "alicante", "almeria-provincia", "asturias", "avila-provincia", "badajoz-provincia",
        "balears-illes", "barcelona-provincia", "burgos-provincia", "caceres-provincia", "cadiz-provincia",
        "ciudad-real-provincia", "cordoba-provincia", "cuenca-provincia", "girona-provincia",
        "granada-provincia", "guadalajara-provincia", "huelva-provincia", "huesca-provincia", "jaen-provincia", "leon-provincia",
        "lleida-provincia", "lugo-provincia", "madrid-provincia", "malaga-provincia", "murcia-provincia", "ourense-provincia",
        "palencia-provincia", "pontevedra-provincia", "salamanca-provincia",
        "santa-cruz-de-tenerife-provincia", "segovia-provincia", "sevilla-provincia", "soria-provincia", "tarragona-provincia",
        "teruel-provincia", "toledo-provincia", "valencia-provincia", "valladolid-provincia", "zamora-provincia",
        "zaragoza-provincia", "cantabria", "castellon", "guipuzcoa", "navarra", "vizcaya"
    ]

    data = []

    for province in provinces_of_spain:

        base_url = f"https://www.idealista.com/en/venta-viviendas/{province}/"

        for page in range(1,2): # 60 pages max.
            if page == 1:
                param = "?ordenado-por=fecha-publicacion-desc"
            else:
                param = f"pagina-{str(page)}.htm?ordenado-por=fecha-publicacion-desc"
            #print(base_url + param)
            response = requests.get(base_url + param, headers=headers)
            if response.status_code != 200:
                print('Error', response.status_code)
                break
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = soup.find_all('article', class_='item')
            if len(listings) == 0:
                print('No more listings')
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
                room = int(details[0].get_text(strip=True).replace('bed.', '').strip()) if 'bed' in details[0].get_text(strip=True) else None
                other_details = details[2].get_text(strip=True) if len(details) > 2 else None
                
                data.append({
                    'url': "https://www.idealista.com/" + url,
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