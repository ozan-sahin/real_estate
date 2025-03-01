#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd

def parse(ad_type: str, real_estate_type:str, city:str) -> pd.DataFrame:

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9'}

    data = []

    for page in range(1,20): #Max 50 pages
        # Define the URL
        url = f"https://www.emlakjet.com/{ad_type}-{real_estate_type}/{city}/{page}/?siralama=4"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        listings = soup.findAll("div", class_="styles_listingWrapper__I0H_l")

        if len(listings) == 0:
            print('No more listings')
            break

        for listing in listings:

            title = listing.find("h3").get_text(strip=True)
            url = listing.find("a")["href"]
            image = listing.find("img")["src"]
            location_raw = listing.find("span", class_="styles_location__ieVpH").get_text(strip=True) \
                if listing.find("span", class_="styles_location__ieVpH") else None
            details = listing.find("div", class_="styles_quickinfoWrapper__F5BBD").get_text(strip=True) \
                if listing.find("div", class_="styles_quickinfoWrapper__F5BBD") else None
            price_raw = listing.find("span", class_="styles_price__8Z_OS").get_text(strip=True) \
                if listing.find("span", class_="styles_price__8Z_OS") else None
            badges = [child.get_text(strip=True) for child in listing.find("div", class_="styles_badges__5geXK").children] \
                if listing.find("div", class_="styles_badges__5geXK") else None

            data.append({
                'title': title,
                'price_raw': price_raw,
                'ad_type' : ad_type,
                'real_estate_type': real_estate_type,
                'city': city,
                'details': details,
                'location_raw': location_raw,
                'badges': badges,
                'url': 'www.emlakjet.com' + url,
                'image': image,
                'source': 'emlakjet.com',
                'query_date': pd.to_datetime('today').strftime('%Y-%m-%d')
            })

    df = pd.DataFrame(data)
    return df
    
def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df[~df["price_raw"].isna()].reset_index(drop=True)
    def get_exchange_ratio(date, source_currency: str, target_currency: str) -> dict:
        url = f"https://api.frankfurter.dev/v1/{date}?base={source_currency}&symbols={target_currency}"
        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.json()["rates"][target_currency]
    df['price_raw'] = df['price_raw'].str.replace('TL', '',regex=True).str.replace('.', '').str.strip()
    df['price'] = pd.to_numeric(df['price_raw'], errors='coerce')
    cur = get_exchange_ratio(pd.to_datetime("today").strftime("%Y-%m-%d"), "TRY", "EUR")
    df["price_EUR"] = df.price * cur
    df["price_EUR"]  = df["price_EUR"].round()
    def split_details(details, real_estate_type):
        if details:
            parts = details.split("|")
            if real_estate_type == 'arsa':
                return pd.Series([parts[0].strip(), None, None, parts[1].strip()])
            else:
                if len(parts) == 4:
                    return pd.Series([part.strip() for part in parts])
                elif len(parts) == 3:
                    return pd.Series([parts[0].strip(), parts[1].strip(), None, parts[2].strip()])
                else:
                    return pd.Series([None, None, None, None])
    
    df[['type', 'rooms', 'level', 'area']] = df.apply(lambda row: split_details(row['details'], row['real_estate_type']), axis=1)
    df['area'] = df['area'].str.replace(".","").str.extract(r'(\d+)').astype(float)
    #df.loc[df['real_estate_type'] == 'arsa', 'area'] *= 1000
    df["badges"] = df["badges"].apply(lambda x: ", ".join(x) if x else None)
    df['price_per_m2'] = round(df['price'] / df['area'], 0)
    df['price_EUR_per_m2'] = round(df['price_EUR'] / df['area'],0)
    df[["ilce", "mahalle"]] = df.location_raw.str.split(" - ", expand=True)
    ref_price_per_m2 = df.groupby("mahalle")["price_per_m2"].mean().round().sort_values(ascending=False).to_dict()
    df["ref_price_per_m2"] = df["mahalle"].map(ref_price_per_m2)
    def get_sale_ratio(row:pd.DataFrame, mapping) -> pd.DataFrame:
        ref = mapping[row["mahalle"]]
        return round((row["price_per_m2"] - ref) / ref * -100, 2)
    df["sale_ratio"] = df.apply(lambda row: get_sale_ratio(row, ref_price_per_m2), axis=1)
    df = df.drop(['price_raw', 'details', 'location_raw'], axis=1)
    return df

def save(df:pd.DataFrame):
    df.to_csv("delete.csv", index=False, encoding="utf-8-sig", sep=";")

#%%