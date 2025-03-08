#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd

def parse() -> pd.DataFrame:

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9'}

    italy_provinces = ['sardegna','sicilia','calabria','puglia','basilicata',
        'campania','molise','lazio','abruzzo','marche','umbria','toscana',
        'emilia-romagna','veneto','friuli-venezia-giulia','litorale-sloveno',
        'istria-e-quarnaro','liguria','provenza-alpi-costa-azzurra']

    params = {"criterio" : "data",
              "ordine" : "desc",
              "pag" : "1"}
    data = []

    for province in italy_provinces:

        base_url = f"https://www.immobiliare.it/en/vendita-case/{province}/"

        for page in range(1,20): # 60 pages max.
            params["pag"] = str(page)
            response = requests.get(base_url, params=params, headers=headers)
            if response.status_code != 200:
                print('Error', response.status_code)
                break
            soup = BeautifulSoup(response.content, 'lxml')
            listings = soup.findAll('li', class_='nd-list__item in-searchLayoutListItem')
            if len(listings) == 0:
                print(f'No more listings found in {province}')
                break

            for listing in listings:

                price = listing.find('div', class_='in-listingCardPrice').find("span"). \
                    get_text(strip=True).replace("from", "").replace('€','').replace(',','').strip()
                title = listing.find('a').get_text(strip=True)
                url = listing.find('a')['href']
                details = "|".join([item.text for item in listing.findAll("div", class_="in-listingCardFeatureList__item")])
                desc = listing.find("div", class_="in-listingCardDescription").get_text(strip=True) \
                    if listing.find("div", class_="in-listingCardDescription") else None
                image = listing.find("img")["src"]

                data.append({
                        'url': url,
                        'title': title,
                        'province': province,
                        'price_raw': price,
                        'details': details,
                        'description' : desc,
                        'image': image
                    })

    df = pd.DataFrame(data)
    return df

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df[~df["price_raw"].str.lower().str.contains("price", na=False)].reset_index(drop=True)
    df["price"] = df["price_raw"].astype(float)
    df["area"] = df.details.str.replace(",", "").str.extract(r'(\d+\.?\d*) m²').astype(float)
    df = df[~df["area"].isnull()].reset_index(drop=True)
    df["price_per_m2"] = round(df["price"] / df["area"], 0)
    df["county"] = df.title.str.split(",").str[-1].str.strip()
    #ref_price_per_m2 = df.groupby("county")["price_per_m2"].mean().round().to_dict()
    #df["ref_price_per_m2"] = df["county"].map(ref_price_per_m2)
    #df['sale_ratio'] = df.apply(lambda row: get_sale_ratio(row, ref_price_per_m2), axis=1)
    #county_counts = df["county"].value_counts()
    #df.loc[df["county"].isin(county_counts[county_counts < 5].index), "sale_ratio"] = None
    df["rooms"] = df.details.str.extract(r'(\d+\.?\d*) rooms').astype(float)
    df['source'] = 'immobiliare'
    df['query_date'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    df.drop(columns=['price_raw', 'details'], inplace=True)
    return df

def get_sale_ratio(row:pd.DataFrame, mapping) -> pd.DataFrame:

    ref = mapping[row["county"]]
    if ref == 0 or ref is None:
        return None
    return round((row["price_per_m2"] - ref) / ref * -100, 2)

def save(df:pd.DataFrame):
    df.to_csv("delete.csv", index=False, encoding="utf-8-sig", sep=";")
#%%