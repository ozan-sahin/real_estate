#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def parse() -> pd.DataFrame:

    headers = {
        "authority": "www.rightmove.co.uk",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7,tr;q=0.6,hu;q=0.5",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=0, i",
        "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
    }

    url = "https://www.rightmove.co.uk/major-cities.html"

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    cities = soup.find_all('section', class_='JdzhVdvXNWIccxl43Plb')
    cities = [city.find("a")["href"] for city in cities]

    baseUrl = 'https://www.rightmove.co.uk'

    data = []

    for city in cities:
        for page in range(1,4):
            response = requests.get(baseUrl + city + f'?index={str(page*24)}&sortType=6', headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            # print(f"Scraping {city} {str(page)}")
            if response.status_code != 200:
                print('Error', response.status_code)
                break
            
            listings = soup.find_all("div", class_=lambda x: x and "PropertyCard_propertyCardContainer" in x)

            if len(listings) == 0:
                print('No more listings')
                break

            for listing in listings:
                title = listing.find("address").get_text(strip=True).replace("\r", " ").replace("\n", "")
                price = listing.find_all("div", class_=lambda x: x and "PropertyPrice_price__VL65t" in x)[-1].get_text()
                location = title
                details = listing.find("p", class_=lambda x: x and "PropertyCardSummary_summary" in x).get_text(strip=True)
                estate_type = listing.find('div', class_='PropertyInformation_container__2wY0G').find(True).get_text(strip=True) if listing.find('div', class_='PropertyInformation_container__2wY0G') else None
                bedroom = listing.find("div", class_=lambda x: x and "PropertyInformation_bedContainer___rN7d" in x).get_text(strip=True) if listing.find("div", class_=lambda x: x and "PropertyInformation_bedContainer___rN7d" in x) else None
                # bathroom = listing.find("div", class_=lambda x: x and "PropertyInformation_bathContainer__ut8VY" in x).get_text(strip=True) if listing.find("div", class_=lambda x: x and "PropertyInformation_bathContainer__ut8VY" in x) else None
                url = listing.find("a", class_=lambda x: x and "PropertyPrice_priceLink" in x)["href"] if listing.find("a", class_=lambda x: x and "PropertyPrice_priceLink" in x) else None
                images = listing.findAll('img')
                image = images[3]["src"] if len(images) > 3 else None

                data.append({
                    'title': title,
                    'price': price,
                    'location': location,
                    'details': details,
                    'url': 'https://www.rightmove.co.uk' + url,
                    'image': image,
                    'county': city.split('/')[-1].replace('.html', ''),
                    'rooms': bedroom,
                    'estate_type': estate_type,
                })
            
    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    return df

def clean(df2: pd.DataFrame) -> pd.DataFrame:

    df = df2.copy()
    df = df[df["price"].str.contains("£", case=False, na=False)]
    df["price"] = df["price"].str.replace("£", "").str.replace(",", "").str.strip()
    df["price"] = df["price"].astype(float)

    def get_area_from_room_number(row):
        # Predefined apartment areas based on room number
        if pd.isna(row["rooms"]):
            return None
        apartment_areas = {1: 43.0, 2: 60.0, 3: 75.0,
                            4: 90.0, 5: 110.0,
                            6: 130.0, 7: 150.0}
        return apartment_areas.get(int(row["rooms"]), int(row["rooms"]) * 35.0)  # Default to 35 sqm per room if not listed
    df["area"] = df.apply(get_area_from_room_number, axis=1)
    def get_exchange_ratio(date, source_currency: str, target_currency: str) -> dict:
        url = f"https://api.frankfurter.dev/v1/{date}?base={source_currency}&symbols={target_currency}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        return response.json()["rates"][target_currency]
    cur = get_exchange_ratio(pd.to_datetime("today").strftime("%Y-%m-%d"), "GBP", "EUR")
    #cur = 1.14  # This is a placeholder. You can use the function above to get the actual exchange rate.
    df["price_EUR"] = df.price * cur
    df["price_per_m2"] = round(df["price_EUR"] / df["area"])
    #df[["level", "rooms", "bathrooms"]] = df.apply(split_information, axis=1, result_type="expand")
    df['source'] = 'rightmove'
    df['query_date'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    return df

def save(df:pd.DataFrame):
    df.to_csv("delete.csv", index=False, encoding="utf-8-sig", sep=";")
#%%