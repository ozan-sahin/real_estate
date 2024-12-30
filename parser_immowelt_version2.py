import bs4 as bs
import requests
import pandas as pd
import json
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def parse(state:str) -> pd.DataFrame:
    
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9'}

    params = {"distributionTypes" : "Buy,Buy_Auction", #Rent
                "estateTypes" : "House,Apartment",
                "locations" : state,
                "locationsInBuildingExcluded" : "Roof_Storey",
                "numberOfRoomsMin" : "",
                "priceMax" : "",
                "projectTypes" : "",
                "spaceMin" : "",
                "yearOfConstructionMin" : "",
                "energyCertificate" : "A_PLUS,A,B,C,D,E",
                "order" : "DateDesc",
                "page" : "1"}

    #Find the last page's number
    url = f"https://www.immowelt.de/classified-search"
    r = requests.get(url, params=params, headers=headers)

    soup = bs.BeautifulSoup(r.text, "lxml")
    page_tag = soup.find_all('button', attrs={'aria-label': lambda x: x and 'seite' in x})
    last_page = min(int(page_tag[-2].text), 333)
    print(str(last_page))
    #Scraping all the pages from immowelt.de
    final_list = []

    # for page in range(1,last_page+2,1):
    for page in range(1,20,1):
        # print(f"page number: {str(page)}")
        params["page"] = str(page)
        r = requests.get(url, params=params, headers=headers)

        if r.status_code == 200:
            soup = bs.BeautifulSoup(r.text, "lxml")

            final_list.append(parse_script_tag(soup))
        else:
            print(f"unsuccesful to parse page: {str(page)}")


    dfFinal = pd.concat(final_list, ignore_index=True)
    return dfFinal

def parse_script_tag(soup):
    
    json_string = soup.findAll("script")[-5].string.split('JSON.parse(')[-1].split(');</script>')[0]

    # Step 2: Unescape the escaped characters
    json_string = json_string.replace('\\"', '"')[1:-3]
    json_string = json_string.replace('\\\\"', "")

    try:
    # Step 3: Parse the JSON string into a Python dictionary
        json_object = json.loads(json_string)
    except json.JSONDecodeError:
        print(f"unsuccesful to parse page due to JSONDecodeError")
        return pd.DataFrame()

    df = pd.DataFrame(json_object['data']['classified-serp-init-data']['pageProps']['classifiedsData']).T.reset_index(drop=True)
    df2 = pd.json_normalize(df.to_dict(orient='records'))

    columns = [
        'brand', 'id', 'status', 'energyClass',
        'mainDescription.description', 'mainDescription.headline',
        'type', 'url',
        'metadata.creationDate', 'metadata.updateDate',
        'location.address.country',
        'location.address.city',
        'location.address.zipCode',
        'location.address.district',
        'hardFacts.title', 'hardFacts.facts',
        'hardFacts.price.value', 'hardFacts.titleAdditions',
        'gallery.images',
        'tracking.building_state',
        'provider.website', 'provider.isPrivateOwner', 'provider.phoneNumbers',
        'provider.intermediaryCard.title',
        'rawData.distributionType', 'rawData.propertyType', 'rawData.price'
    ]

    # Filter the columns list to include only existing columns in the DataFrame
    existing_columns = [col for col in columns if col in df2.columns]

    df2 = df2[existing_columns]
    return df2

def clean_data(df):

    df_pivot = get_unit_prices()

    df['metadata.creationDate'] = pd.to_datetime(df['metadata.creationDate'], format='%Y-%m-%dT%H:%M:%S.%f').dt.floor('S')
    df['metadata.updateDate'] = pd.to_datetime(df['metadata.updateDate'], format='%Y-%m-%dT%H:%M:%S.%f').dt.floor('S')
    df["type"] = df["type"].str.capitalize()
    df["rawData.propertyType"] = df["rawData.propertyType"].str.lower()
    df["tracking.building_state"] = df["tracking.building_state"].str.capitalize()
    df["rawData.distributionType"] = df["rawData.distributionType"].str.capitalize()
    df['image'] = df["gallery.images"].str[0].str["url"]
    df = df.drop(columns=["gallery.images"])
    df['hardFacts.titleAdditions'] = df['hardFacts.titleAdditions'].str[0]
    df["provider.phoneNumbers"] = df["provider.phoneNumbers"].str[0]

    def extract_facts(facts):
        type_list = ["numberOfRooms", "livingSpace", "numberOfFloors", "overallSpace", "plotSpace"]
        if isinstance(facts, list):
            return {item['type']: item['splitValue'].replace(".", "").strip().replace(",", ".") if item['splitValue'] is not None else None for item in facts if item['type'] in type_list}
        else:
            return {}

    # Apply the function to each row in the 'hardFacts_facts' column
    extracted_facts = df['hardFacts.facts'].apply(extract_facts)

    # Convert the extracted facts to a DataFrame
    facts_df = pd.DataFrame(list(extracted_facts))
    df2 = pd.concat([df.reset_index(drop=True), facts_df], axis=1).drop(columns=['hardFacts.facts'])

    df2['numberOfRooms'] = pd.to_numeric(df2['numberOfRooms'], errors='coerce')
    df2['livingSpace'] = pd.to_numeric(df2['livingSpace'], errors='coerce')
    df2['numberOfFloors'] = pd.to_numeric(df2['numberOfFloors'], errors='coerce')
    df2['overallSpace'] = pd.to_numeric(df2['overallSpace'], errors='coerce')
    df2['plotSpace'] = pd.to_numeric(df2['plotSpace'], errors='coerce')

    column_mapping = {'brand' : 'source','mainDescription.description' : 'description',
    'mainDescription.headline' : 'headline','metadata.creationDate' : 'creation_date',
    'metadata.updateDate' : 'update_date','location.address.country' : 'country',
    'location.address.city' : 'city','location.address.zipCode' : 'zip_code',
    'location.address.district' : 'district','hardFacts.title' : 'title',
    'hardFacts.price.value' : 'price_raw','hardFacts.titleAdditions' : 'title_additions',
    'tracking.building_state' : 'building_state','provider.website' : 'makler_website',
    'provider.isPrivateOwner' : 'is_private_owner','provider.phoneNumbers' : 'phone_number',
    'provider.intermediaryCard.title' : 'makler','rawData.distributionType' : 'distribution_type',
    'rawData.propertyType' : 'estate_type','rawData.price' : 'price', 'livingSpace' : 'area',
    'type' : 'profile', 'numberOfRooms' : 'room'}
    
    df2 = df2.rename(columns=column_mapping)
    
    #---
    df2["district"] = df2["district"].fillna("")
    df2["city"] = df2["city"].fillna("")
    df2["price_per_m2"] = round(df2['price'] / df2['area'])
    df2["type"] = df2.apply(return_keyword, axis=1)
    df2["ref_price"] = df2.apply(lambda x: return_ref_price(x, df_pivot), axis=1).round()
    df2["sale_ratio"] = round((df2.ref_price - df2.price_per_m2) / df2.ref_price * 100)
    df2["ref_rent_price"] = df2.apply(lambda x : return_rent_price(x, df_pivot), axis=1).round(2)
    df2["return_in_years"] = round(df2.price / df2.ref_rent_price /  df2['area'] / 12, 1)
    df2["yield_ratio"] = round(1 / df2["return_in_years"] * 100, 2)
    #---

    df2["query_date"] = datetime.date.today()
   
    ordered_cols = ['source', 'id', 'status', 'energyClass', 'description', 'headline',
       'profile', 'url', 'creation_date', 'update_date', 'country', 'city',
       'zip_code', 'district', 'title', 'price_raw', 'title_additions',
       'building_state', 'makler_website', 'is_private_owner', 'phone_number',
       'makler', 'distribution_type', 'estate_type', 'price', 'image', 'room',
       'area', 'plotSpace', 'numberOfFloors', 'overallSpace',
       'price_per_m2', 'type', 'ref_price', 'sale_ratio', 'ref_rent_price',
       'return_in_years', 'yield_ratio', 'query_date']
    
    df2 = df2[ordered_cols]

    return df2


def return_keyword(row):

    keyword_map = {
        ("Buy", "house"): "hauspreise",
        ("Buy_auction", "house"): "hauspreise",
        ("Buy", "apartment"): "wohnungspreise",
        ("Buy_auction", "apartment"): "wohnungspreise",
        ("Rent", "house"): "mietpreise-haeuser",
        ("Rent", "apartment"): "mietspiegel"
    }
    keyword = keyword_map.get((row["distribution_type"], row["estate_type"]))
    return keyword

def get_unit_prices():

    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets', \
            "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("sailing-analytics-425909-708f3b5e87ff.json",scope)
    client = gspread.authorize(creds)

    sheet = client.open("unit_price_real_estate").sheet1
    data = sheet.get_all_records()
    existing_data_google_sheets = pd.DataFrame(data)
    existing_data_google_sheets.price_clean = pd.to_numeric(existing_data_google_sheets.price_clean)
    df_pivot = existing_data_google_sheets.pivot_table(index='neighborhood', columns='type', values='price_clean')
    return df_pivot

def return_ref_price(row, df_pivot : pd.DataFrame):
    neighborhood = row["district"].strip().lower().replace(" ", "-").replace("ö","oe").replace("ü","ue").replace("ß","ss").replace("ä","ae")
    city = row["city"].strip().lower().replace(" ", "-").replace("ö","oe").replace("ü","ue").replace("ß","ss").replace("ä","ae")
    try:
        return df_pivot.loc[neighborhood, row["type"]]
    except KeyError:
        try:
            return df_pivot.loc[city, row["type"]]
        except KeyError:
            return None
        
def return_rent_price(row, df_pivot : pd.DataFrame):
    neighborhood = row["district"].strip().lower().replace(" ", "-").replace("ö","oe").replace("ü","ue").replace("ß","ss").replace("ä","ae")
    city = row["city"].strip().lower().replace(" ", "-").replace("ö","oe").replace("ü","ue").replace("ß","ss").replace("ä","ae")
    if row["estate_type"] == "house":
        type_var = "mietpreise-haeuser"
    elif row["estate_type"] == "apartment":
        type_var = "mietspiegel"
    else:
        return None
    try:
        return df_pivot.loc[neighborhood, type_var]
    except KeyError:
        try:
            return df_pivot.loc[city, type_var]
        except KeyError:
            return None
#dfFinal = clean_data(dfFinal)
#dfFinal.to_csv("delete.csv", index=False, encoding='utf-8-sig', sep=';')