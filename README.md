# 🏠 Real Estate Analysis — Multi-Country Pipeline

A Python scraping and analytics pipeline that collects property listings from **8 countries across Europe**, stores them in SQLite and Google Sheets, calculates investment metrics, and presents everything in a **Streamlit dashboard**.

---

## Overview

This project automates the end-to-end workflow for monitoring European real estate markets:

1. **Scrape** — Country-specific parsers pull listings from the leading local portals (Immowelt, Fotocasa, Funda, Immobiliare, Immoweb, Idealista, French-Property, Emlakjet).
2. **Store** — Persists data to a local SQLite database and syncs new/deleted listings to Google Sheets.
3. **Enrich** — Calculates price-per-m², reference prices, sale ratio, rental yield, and payback period.
4. **Visualise** — Displays the enriched data in an interactive Streamlit dashboard.

---

## Supported Countries & Portals

| Country | Portal | Coverage | Distribution Types |
|---|---|---|---|
| 🇩🇪 Germany | [immowelt.de](https://www.immowelt.de) | All 16 federal states | Buy, Buy_Auction, Rent |
| 🇹🇷 Turkey | [emlakjet.com](https://www.emlakjet.com) | Any city (configurable) | Buy (`satilik`), Rent (`kiralik`) |
| 🇪🇸 Spain | [fotocasa.es](https://www.fotocasa.es) | 20 provinces + 18 coastal zones | Buy |
| 🇫🇷 France | [french-property.com](https://www.french-property.com) | National | Buy |
| 🇳🇱 Netherlands | [funda.nl](https://www.funda.nl) | All 12 provinces | Buy |
| 🇵🇹 Portugal | [idealista.pt](https://www.idealista.pt) | All 18 districts + Azores + Madeira | Buy |
| 🇮🇹 Italy | [immobiliare.it](https://www.immobiliare.it) | 19 provinces (south + centre + north) | Buy |
| 🇧🇪 Belgium | [immoweb.be](https://www.immoweb.be) | National | Buy |

---

## Project Structure

```
real_estate/
├── main.py                          # Entry point v1: scrape → SQLite → Google Sheets (Germany)
├── main_version2.py                 # Entry point v2: scrape → clean → analytics → Google Sheets
├── main_others.py                   # Experimental / alternative flows
├── parser_immowelt_version2.py      # Immowelt parser (root-level, used by main.py)
├── parsers/
│   ├── parser_immowelt_version2.py  # Germany — immowelt.de
│   ├── parser_turkey.py             # Turkey  — emlakjet.com
│   ├── parser_spain.py              # Spain   — fotocasa.es
│   ├── parser_france.py             # France  — french-property.com
│   ├── parser_netherlands.py        # Netherlands — funda.nl
│   ├── parser_portugal.py           # Portugal — idealista.pt
│   ├── parser_italy.py              # Italy   — immobiliare.it
│   └── parser_belgium.py            # Belgium — immoweb.be
├── streamlit-dashboard/             # Streamlit app source
├── .streamlit/                      # Streamlit config (theme, etc.)
├── .devcontainer/                   # Dev container setup
└── README.md
```

---

## Parser Details

Each parser exposes a consistent `parse()` / `clean()` interface, adapted to the data structure of its source portal.

### 🇩🇪 Germany — `parser_immowelt_version2.py`
- Scrapes `immowelt.de` using state codes `AD04DE1`–`AD04DE16`.
- Filters by energy class, distribution type, and estate type via URL params.
- Parses embedded JSON from a `<script>` tag with LZ-string decompression.
- `clean()` extracts structured fields from nested JSON (`hardFacts.facts`), renames columns, and runs the full investment metrics calculation.
- `apply_analytics()` computes `ref_price`, `sale_ratio`, `ref_rent_price`, `return_in_years`, and `yield_ratio` via a pivot lookup against the `unit_price_real_estate` Google Sheet.

### 🇹🇷 Turkey — `parser_turkey.py`
- Scrapes `emlakjet.com` with configurable `ad_type`, `real_estate_type`, and `city`.
- Supports property types: `daire`, `villa`, `arsa`, `dükkan`, `ofis`, `bahçe`, `tarla`.
- `clean()` converts TRY prices to EUR using the live [Frankfurter API](https://api.frankfurter.dev) exchange rate at the query date.

### 🇪🇸 Spain — `parser_spain.py`
- Scrapes `fotocasa.es` across 20 provinces and 18 coastal zones (Costa del Sol, Costa Blanca, etc.).
- Uses `curl_cffi` to handle bot-protection headers.
- Parses listing data from an embedded `JSON.parse()` script tag (`initialSearch.result.realEstates`).
- Extracts surface, rooms, bathrooms, coordinates, and multimedia from nested feature arrays.

### 🇫🇷 France — `parser_france.py`
- Scrapes `french-property.com` for national buy listings.
- Parses HTML with BeautifulSoup: title, region, department, municipality, description, bedrooms, bathrooms, habitable area, land area, price.
- `clean()` strips "POA" (price on application) listings, casts numeric fields, and computes `price_per_m2`.

### 🇳🇱 Netherlands — `parser_netherlands.py`
- Scrapes `funda.nl` across all 12 Dutch provinces using province slugs (e.g. `provincie-noord-holland`).
- Uses mobile user-agent headers to access the listing cards.
- Includes optional geocoding via `geopy` / Nominatim for address enrichment.

### 🇵🇹 Portugal — `parser_portugal.py`
- Scrapes `idealista.pt` across 18 mainland districts plus Azores and Madeira.
- Parses title, address, district, estate type, price, area (m²), room count, and image.
- Handles the Azores with an alternate URL pattern; includes `time.sleep()` to stay within rate limits.

### 🇮🇹 Italy — `parser_italy.py`
- Scrapes `immobiliare.it` across 19 southern, central, and northern provinces.
- Uses mobile sec-ch-ua headers matching Chrome on Android to avoid bot detection.
- Parses price, title, province, details (piped string), description, and image per listing.

### 🇧🇪 Belgium — `parser_belgium.py`
- Scrapes `immoweb.be` for apartments for sale nationally.
- Extracts price from a Vue.js `:price` attribute embedded in the listing card HTML.
- `clean()` computes `price_per_m2` and adds `source` and `query_date`.

---

## Features

### Deduplication & Change Tracking (Germany pipeline)
- New listings are appended; existing ones are skipped (keyed on `url`, `makler`, `address`, `title`, `city` in v1; on `id` in v2).
- Listings no longer present on Immowelt are marked `inactive` with a `deletion_date` in Google Sheets via batch update.

### Investment Metrics (Germany pipeline)
| Metric | Formula |
|---|---|
| `price_per_m2` | `price ÷ area` |
| `ref_price` | Market benchmark per m² from Google Sheets (neighbourhood → city fallback) |
| `sale_ratio` | `(ref_price − price_per_m2) / ref_price × 100` — positive = below market |
| `ref_rent_price` | Reference monthly rent per m² from Google Sheets |
| `return_in_years` | `price / ref_rent_price / area / 12` |
| `yield_ratio` | `1 / return_in_years × 100` — gross rental yield % |

### Streamlit Dashboard
Interactive dashboard in `streamlit-dashboard/` for filtering, sorting, and visualising listings and their investment metrics across countries.

---

## Setup

### Prerequisites

- Python 3.9+
- A Google Cloud service account with Sheets API and Drive API enabled
- A `sailing-analytics-XXXXXX-XXXXXXXXXX.json` credentials file in the project root
- Two Google Sheets (for the Germany pipeline):
  - `real_estate_table` — main listings table
  - `unit_price_real_estate` — reference price lookup (neighbourhood/city × property type)

### Install dependencies

```bash
pip install -r requirements.txt
```

Key packages:

```
requests
curl_cffi          # Spain parser (bot-protection bypass)
beautifulsoup4
lxml
pandas
numpy
sqlalchemy
gspread
oauth2client
geopy              # Netherlands parser (optional geocoding)
lzstring           # Germany parser (script tag decompression)
streamlit
```

### Run a country scraper

**Germany (v2 pipeline):**
```bash
python main_version2.py
```

**Any other country** — import and call directly:
```python
import parsers.parser_turkey as turkey
df_raw = turkey.parse(ad_type="satilik", real_estate_type="daire", city="istanbul")
df_clean = turkey.clean(df_raw)
```

### Run the dashboard

```bash
cd streamlit-dashboard
streamlit run app.py
```

---

## Data Storage

### SQLite (`germany_real_estate_database.db`)
Local database with a `main_table` containing all Germany listings. Used as the primary store for offline analysis and as a deduplication source.

### Google Sheets
| Sheet | Purpose |
|---|---|
| `real_estate_table` | Main Germany listings (v1) with `status` and `deletion_date` tracking |
| `real_estate_table_germany_2` | Germany listings (v2) keyed on `id` |
| `unit_price_real_estate` | Reference price lookup: neighbourhood × `wohnungspreise` / `hauspreise` / `mietspiegel` / `mietpreise-haeuser` |

---

## Reference Price Lookup (Germany)

The `unit_price_real_estate` sheet provides per-m² benchmarks indexed by neighbourhood (city fallback if not found):

| Column | Description |
|---|---|
| `wohnungspreise` | Apartment buy price per m² |
| `hauspreise` | House buy price per m² |
| `mietspiegel` | Apartment rent per m² |
| `mietpreise-haeuser` | House rent per m² |

Neighbourhood names are normalised before lookup: lowercased, hyphenated, and German umlauts converted (`ö→oe`, `ü→ue`, `ä→ae`, `ß→ss`).

---

## Environment & Credentials

> **Never commit** your service account JSON file to version control.

Add to `.gitignore`:

```
*.json
*.db
```

For production or CI use, inject credentials via an environment variable or a secrets manager instead of reading the JSON file directly.

---

## Roadmap

- [ ] Schedule scraping via cron / GitHub Actions
- [ ] Extend investment metrics (ref price lookup) to all country parsers
- [ ] Add geocoding and map view to the dashboard
- [ ] Unified deduplication and change tracking across all countries
- [ ] Add price history tracking per listing
- [ ] Containerise with Docker

---

## License

MIT
