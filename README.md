# 🏠 Real Estate Analysis — Germany

A Python pipeline that scrapes German property listings from **Immowelt**, stores them in SQLite and Google Sheets, calculates investment metrics, and presents everything in a **Streamlit dashboard**.

---

## Overview

This project automates the end-to-end workflow for monitoring the German real estate market:

1. **Scrape** — Parses listings across all 16 German federal states from Immowelt (buy & rent, houses & apartments).
2. **Store** — Persists data to a local SQLite database and syncs new/deleted listings to Google Sheets.
3. **Enrich** — Calculates price-per-m², reference prices, sale ratio, rental yield, and payback period.
4. **Visualise** — Displays the enriched data in an interactive Streamlit dashboard.

---

## Project Structure

```
real_estate/
├── main.py                        # Entry point: scrape → SQLite → Google Sheets
├── main_version2.py               # Refactored pipeline (v2)
├── main_others.py                 # Experimental / alternative flows
├── parser_immowelt_version2.py    # Core scraper + data cleaning logic
├── parsers/                       # Additional parser modules
├── streamlit-dashboard/           # Streamlit app source
├── .streamlit/                    # Streamlit config (theme, etc.)
├── .devcontainer/                 # Dev container setup
└── README.md
```

---

## Features

### Data Collection
- Scrapes all 16 German federal states (`AD04DE1` – `AD04DE16`) in a single run.
- Filters by distribution type (Buy / Buy_Auction / Rent), estate type (House / Apartment), and energy class.
- Handles pagination up to 333 pages per state.
- Extracts structured fields: address, price, area, rooms, floors, building state, agent info, images, and more.

### Deduplication & Change Tracking
- New listings are appended; existing ones are skipped (keyed on `url`, `makler`, `address`, `title`, `city`).
- Listings no longer present on Immowelt are marked `inactive` with a `deletion_date` in Google Sheets.

### Investment Metrics
| Metric | Description |
|---|---|
| `price_per_m2` | Asking price ÷ living area |
| `ref_price` | Reference market price for the neighbourhood/city from Google Sheets lookup |
| `sale_ratio` | `(ref_price − price_per_m2) / ref_price × 100` — positive means below market |
| `ref_rent_price` | Reference monthly rent per m² |
| `return_in_years` | Years to recoup the purchase price via rental income |
| `yield_ratio` | `1 / return_in_years × 100` — gross rental yield % |

### Streamlit Dashboard
Interactive dashboard in `streamlit-dashboard/` for filtering, sorting, and visualising listings and their investment metrics.

---

## Setup

### Prerequisites

- Python 3.9+
- A Google Cloud service account with access to Google Sheets API and Google Drive API
- A `sailing-analytics-XXXXXX-XXXXXXXXXX.json` credentials file in the project root
- Two Google Sheets:
  - `real_estate_table` — main listings table
  - `unit_price_real_estate` — reference price lookup table (neighbourhood/city × type)

### Install dependencies

```bash
pip install -r requirements.txt
```

Key packages:

```
requests
beautifulsoup4
lxml
pandas
numpy
sqlalchemy
gspread
oauth2client
streamlit
```

### Run the scraper

```bash
python main.py
```

This will:
- Scrape all 16 states from Immowelt
- Write new rows to `germany_real_estate_database.db`
- Sync new listings to Google Sheets
- Mark deleted listings as `inactive`

### Run the dashboard

```bash
cd streamlit-dashboard
streamlit run app.py
```

---

## Data Storage

### SQLite (`germany_real_estate_database.db`)
Local database with a `main_table` containing all listings. Used as the primary store for offline analysis.

### Google Sheets (`real_estate_table`)
Live sheet with columns including: `source`, `id`, `status`, `energyClass`, `city`, `district`, `zip_code`, `price`, `area`, `room`, `price_per_m2`, `sale_ratio`, `yield_ratio`, `return_in_years`, `query_date`, `status`, `deletion_date`, and more.

---

## Reference Price Lookup

The `unit_price_real_estate` Google Sheet provides per-m² benchmark prices indexed by neighbourhood (or city fallback) and property type:

| type | description |
|---|---|
| `wohnungspreise` | Apartment buy price per m² |
| `hauspreise` | House buy price per m² |
| `mietspiegel` | Apartment rent per m² |
| `mietpreise-haeuser` | House rent per m² |

The parser normalises German umlauts (`ö→oe`, `ü→ue`, `ä→ae`, `ß→ss`) and lowercases/hyphenates neighbourhood names before lookup.

---

## Environment & Credentials

> **Never commit** your service account JSON file to version control.

Add it to `.gitignore`:

```
*.json
*.db
```

For production or CI use, inject the credentials via an environment variable or a secrets manager.

---

## Roadmap

- [ ] Schedule scraping via cron / GitHub Actions
- [ ] Add geocoding and map view to the dashboard
- [ ] Extend to additional portals (Immoscout24, eBay Kleinanzeigen)
- [ ] Add price history tracking per listing
- [ ] Containerise with Docker

---

## License

MIT
