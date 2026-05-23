#%%
from curl_cffi import requests
import re
import json
import pandas as pd
from bs4 import BeautifulSoup

def parse():

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9'}

    provinces = {'Alicante': 'https://www.fotocasa.es/en/buy/all-the-houses/alicante-province/all-zones/l', 'Almería': 'https://www.fotocasa.es/en/buy/all-the-houses/almeria-province/all-zones/l', 'Asturias': 'https://www.fotocasa.es/en/buy/all-the-houses/asturias-province/all-zones/l', 'Balearic Islands': 'https://www.fotocasa.es/en/buy/all-the-houses/illes-balears-province/all-zones/l', 'Barcelona': 'https://www.fotocasa.es/en/buy/all-the-houses/barcelona-province/all-zones/l', 'Bizkaia': 'https://www.fotocasa.es/en/buy/all-the-houses/bizkaia-province/all-zones/l', 'Cádiz': 'https://www.fotocasa.es/en/buy/all-the-houses/cadiz-province/all-zones/l', 'Cantabria': 'https://www.fotocasa.es/en/buy/all-the-houses/cantabria-province/all-zones/l', 'Castellón': 'https://www.fotocasa.es/en/buy/all-the-houses/castellon-province/all-zones/l', 'Girona': 'https://www.fotocasa.es/en/buy/all-the-houses/girona-province/all-zones/l', 'Granada': 'https://www.fotocasa.es/en/buy/all-the-houses/granada-province/all-zones/l', 'Las Palmas': 'https://www.fotocasa.es/en/buy/all-the-houses/las-palmas-province/all-zones/l', 'Madrid': 'https://www.fotocasa.es/en/buy/all-the-houses/madrid-province/all-zones/l', 'Málaga': 'https://www.fotocasa.es/en/buy/all-the-houseshe-houses/malaga-province/all-zones/l', 'Murcia': 'https://www.fotocasa.es/en/buy/all-the-houses/murcia-province/all-zones/l', 'Santa Cruz de Tenerife': 'https://www.fotocasa.es/en/buy/all-the-houses/santa-cruz-de-tenerife-province/all-zones/l', 'Sevilla': 'https://www.fotocasa.es/en/buy/all-the-houses/sevilla-province/all-zones/l', 'Tarragona': 'https://www.fotocasa.es/en/buy/all-the-houses/tarragona-province/all-zones/l', 'Toledo': 'https://www.fotocasa.es/en/buy/all-the-houses/toledo-province/all-zones/l', 'Valencia': 'https://www.fotocasa.es/en/buy/all-the-houses/valencia-province/all-zones/l'}
    coasts = {'Basque Coast': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-vasca/l', 'Costa Blanca': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-blanca/l', 'Costa Brava': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-brava/l', 'Costa Cálida': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-calida/l', 'Costa del Sol': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-del-sol/l', 'Costa da Morte': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-da-morte/l', 'Costa de Almería': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-de-almeria/l', 'Costa de Cantabria': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-de-cantabria/l', 'Costa de Garraf': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-del-garraf/l', 'Costa de la Luz': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-de-la-luz/l', 'Costa de Valencia': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-de-valencia/l', 'Costa del Azahar': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-del-azahar/l', 'Costa del Maresme': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-del-maresme/l', 'Costa Dorada': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-daurada/l', 'Costa Tropical': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-tropical/l', 'Costa Verde': 'https://www.fotocasa.es/en/buy/all-the-houses/area/costa-verde/l', 'Rías Altas': 'https://www.fotocasa.es/en/buy/all-the-houses/area/rias-altas/l', 'Rías Bajas': 'https://www.fotocasa.es/es/comprar/viviendas/area/rias-bajas/l'}

    def parse_script_tag(soup):
        
        script = soup.find("script", {"id": "sui-scripts"})

        if script is None:
            print("Script tag with id 'sui-scripts' not found.")
            return pd.DataFrame()  # or raise ValueError("Script tag not found")
        # Extract the JSON string from window assignment
        raw = script.string
        matches = re.findall(r"JSON\.parse\('(.+?)'\)", raw, re.DOTALL)
        json_str = matches[1]  # 0 = first, 1 = second, 2 = third etc.
        # Unescape the string (it's double-escaped)
        unescaped = json_str.encode("utf-8").decode("unicode_escape")
        data = json.loads(unescaped)
        
        df2 = pd.DataFrame(data["initialSearch"]["result"]["realEstates"])
        # df2 = pd.json_normalize(df2.to_dict(orient='records'))

        columns = [
                'address', 'buildingSubtype', 'buildingType','coordinates',
                'date', 'description','detail', 'features', 'id', 'location',
                'multimedia','price', 'rawPrice'
        ]

        df2["description"] = df2["description"].str.encode("utf-8", "ignore").str.decode("utf-8")
        # Filter the columns list to include only existing columns in the DataFrame
        existing_columns = [col for col in columns if col in df2.columns]

        df2 = df2[existing_columns]
        return df2

    final = []

    for _, url in coasts.items():
        for page in range(1, 3): # 30 ads per page
            response = requests.get(url + f"/{str(page)}", headers=headers, params = {'sortType' : 'publicationDate'})
            if response.status_code != 200:
                print(f"Failed to retrieve data from {url} page {page}")
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            dfTemp = parse_script_tag(soup)
            final.append(dfTemp)

    return pd.concat(final, ignore_index=True)


def clean(df2: pd.DataFrame) -> pd.DataFrame:

    df = df2.copy()

    def extract_feature(features, key):
        if isinstance(features, list):
            for f in features:
                if f.get("key") == key:
                    return f.get("value")
        return None

    df["surface"] = df["features"].apply(lambda x: extract_feature(x, "surface"))
    df["bathrooms"] = df["features"].apply(lambda x: extract_feature(x, "bathrooms"))
    df["rooms"] = df["features"].apply(lambda x: extract_feature(x, "rooms"))

    df["url"] = 'https://www.fotocasa.es' + df["detail"].apply(lambda x: x.get("en-GB") if isinstance(x, dict) else None)

    df["lat"] = df["coordinates"].apply(lambda x: x.get("latitude") if isinstance(x, dict) else None)
    df["lon"] = df["coordinates"].apply(lambda x: x.get("longitude") if isinstance(x, dict) else None)

    def get_first_src(m):
        if isinstance(m, list) and len(m) > 0 and isinstance(m[0], dict):
            return m[0].get("src")
        return None

    df["image"] = df["multimedia"].apply(get_first_src)

    address_df = df["address"].apply(lambda x: x if isinstance(x, dict) else {}).apply(pd.Series)

    # df["publish_date"] = df["date"].apply(lambda x: pd.to_datetime(x.get("timestamp"), unit='ms').date() if isinstance(x, dict) else None)

    df = pd.concat([df, address_df], axis=1)
    df["price"] = df["rawPrice"]

    df = df.drop(columns=["features", "detail", "coordinates", "multimedia", "address", "date", "rawPrice"])

    df["description"] = df["description"].apply(lambda x: x.strip().replace("\n", "") if isinstance(x, str) else None)
    df["price_per_m2"] = df.apply(lambda row: row["price"] / row["surface"] if not pd.isna(row["surface"]) and row["surface"] > 0 else None, axis=1).round(2)
    
    df["source"] = "fotocasa.es"
    df["query_date"] = pd.to_datetime("today").date()

    return df

def save(df:pd.DataFrame):
    df.to_csv("delete.csv", index=False, encoding="utf-8-sig", sep=";")
#%%