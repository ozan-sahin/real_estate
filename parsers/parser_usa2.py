#%%
import requests
import pandas as pd
import json

def parse() -> pd.DataFrame:

    url = 'https://www.zillow.com/async-create-search-page-state'

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7,tr;q=0.6,hu;q=0.5",
        "content-type": "application/json",
        #"cookie": "zguid=24|%247cbe939a-690a-49c0-974f-7bc91d457854; zgsession=1|2a01f2a8-179b-4a94-b042-3cd2e8ca03f5; ...",
        "origin": "https://www.zillow.com",
        "priority": "u=1, i",
        "referer": "https://www.zillow.com/homes/for_sale/?searchQueryState=...",
        "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
    }
    payload = {
        "searchQueryState": {
            "pagination": {"currentPage": 1},
            "isMapVisible": False,
            "mapBounds": {
                "east": -71.0939045615199,
                "west": -87.0240803427699,
                "south": 24.748372651494503,
                "north": 45.738044121032985
            },
            "mapZoom": 6,
            "filterState": {
                "sortSelection": {"value": "days"},
                "isComingSoonStatus": {"value": False},
                "isZillowPreview": {"value": False},
                "isApartment": {"value": False},
                "isApartmentOrCondo": {"value": False},
                "isCondo": {"value": False},
                "isLotLand": {"value": False},
                "isManufactured": {"value": False},
                "isMultiFamily": {"value": False},
                "isTownhouse": {"value": False}
            },
            "isListVisible": True
        },
        "wants": {"cat1": ["listResults"]},
        "requestId": 2,
        "isDebugRequest": False,
        "treatments": {
            "SXP_PENDING_BACKUP_STATUS_UPDATE": "off"
        }
    }

    final_results = []
    for page in range(1,2):
        items = []
        payload["searchQueryState"]["pagination"]["currentPage"] = page
        r = requests.put(url, headers=headers, json=payload)
        items = json.loads(r.text)["cat1"]["searchResults"]["listResults"]
        final_results.extend(items)

    df = pd.DataFrame([item["hdpData"]["homeInfo"] for item in final_results])
    df["image"] = [item.get("imgSrc") for item in final_results]
    df["url"] = [item.get("detailUrl") for item in final_results]
    return df

def clean(df_in : pd.DataFrame) -> pd.DataFrame:
    df = df_in.copy()
    df = df[df.price.notna() & (df.price != 0)]
    df["sale_ratio"] = (df["price"] / df["zestimate"] - 1).round(3)
    df["return"] = round(df["price"] / (df["rentZestimate"] * 12), 2)
    df["area"] = round(df["livingArea"] * 0.092903)
    df["price_per_m2"] = round(df["price"] / df["area"], 2)
    df["source"] = "zillow"
    df["query_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
    columns_to_remove = [
        "isFeatured", "shouldHighlight", "listing_sub_type",
        "isUnmappable", "isPreforeclosureAuction", "homeStatusForHDP",
        "isNonOwnerOccupied", "isPremierBuilder", "isZillowOwned",
        "currency", "country", "taxAssessedValue", "lotAreaValue",
        "lotAreaUnit", "isShowcaseListing", "datePriceChanged",
        "priceChange","comingSoonOnMarketDate",
        "newConstructionType", "priceReduction", "unit", "openHouse",
        "open_house_info", "providerListingID", "group_type", "priceSuffix"
    ]
    df = df.drop(columns=columns_to_remove, errors="ignore")
    return df.reset_index(drop=True)

def save(df:pd.DataFrame):
    df.to_csv("usa.csv", index=False, encoding="utf-8-sig", sep=";", decimal=".")
#%%