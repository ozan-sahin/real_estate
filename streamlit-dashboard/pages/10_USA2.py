import pandas as pd
import streamlit as st
import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection
from geopy.geocoders import Photon

st.set_page_config(page_title="USA Real Estate Market (Zillow)", page_icon="🌭", layout="wide")

# Create a connection object.
conn = st.connection("gsheets_usa2", type=GSheetsConnection)

st.title("🌭 USA Real Estate Market (Zillow)")

df = conn.read()
df['query_date'] = pd.to_datetime(df['query_date'])

column1, column2, column3, column4, column5, column6 = st.columns(6)
with column1:
    tile = column1.container( border=True)
    tile.write("Number of ads analysed")
    tile.subheader(f"🧮{df.shape[0]}")
with column2:
    tile = column2.container( border=True)
    tile.write("Mean price")
    tile.subheader(f"💶 {round(df.price.mean().round()/1000)} k$")
with column3:
    tile = column3.container( border=True)
    tile.write("Mean number of bedrooms")
    tile.subheader(f"🏡 {df.bedrooms.mean().round(2)}")
with column4:
    tile = column4.container( border=True)
    tile.write("Mean real estate area")
    tile.subheader(f"🏡 {round(df.area_m2.mean().round()):,.0f} m²")
with column5:
    tile = column5.container( border=True)
    tile.write("Mean unit price")
    tile.subheader(f"📈 {round(df.price_per_m2.replace([float('inf'), float('-inf')], pd.NA).mean().round()):,.0f} $/m²")
with column6:
    today = datetime.date.today()
    added_today = df[df['query_date'].dt.date == today].shape[0]
    tile = column6.container( border=True)
    tile.write("New ads published today")
    tile.subheader(f"🆕{added_today}")

st.markdown("""---""")

ordered_columns = ['img', 'state', 'city', 'price', 'area_m2', \
                   'price_per_m2', 'bedrooms', 'query_date', 'url']

column1, column3, column5, column6 = st.columns([4, 2, 2, 1])

@st.cache_data
def get_filter_options(df):
    return {
        'states': df.state.sort_values().unique().tolist(),
        'cities': df.city.sort_values().unique().tolist(),
    }

@st.cache_data
def filter_df(df, low_price, high_price, low_area, high_area,
                  states, cities, date_to_select):

    if date_to_select == "Today":
        date_mask = df['query_date'].dt.date == datetime.date.today()
    elif date_to_select == "Last Week":
        cutoff = datetime.date.today() - datetime.timedelta(days=7)
        date_mask = df['query_date'].dt.date >= cutoff
    elif date_to_select == "Last Month":
        cutoff = datetime.date.today() - datetime.timedelta(days=30)
        date_mask = df['query_date'].dt.date >= cutoff
    else:
        date_mask = pd.Series(True, index=df.index)

    mask = (
        date_mask &
        df['price'].between(low_price, high_price) &
        df['area_m2'].between(low_area, high_area) &
        df['state'].isin(states) &
        df['city'].isin(cities)
    )

    return df[mask].copy()

# --- UI ---
options = get_filter_options(df)

with column1:
    low_price, high_price = st.select_slider('Price Range', options=range(0, 10_000_001, 10_000), value=(0, 800000))
    low_area, high_area = st.select_slider('Area', options=range(0, 750), value=(60, 200))

with column3:
    states = st.multiselect("States", options['states'], [])
    all_options = st.checkbox("Select all states", value=True)
    if all_options:
        states = options['states']

with column5:
    cities = st.multiselect("Cities", options['cities'], [])
    all_options_cities = st.checkbox("Select all cities", value=True)
    if all_options_cities:
        cities = options['cities']

with column6:
    date_options = ["Today", "Last Week", "Last Month", "All Time"]
    date_to_select = st.selectbox("Date Range", date_options)

# --- Filter ---
df_query = filter_df(
    df,
    low_price, high_price,
    low_area, high_area,
    tuple(states), tuple(cities),  # tuples for cache hashing
    date_to_select
)

ordered_columns = ['img', 'state', 'city', 'price', 'area_m2', 'sale_ratio', 'zestimate', 'return',\
                   'price_per_m2', 'bedrooms', 'bathrooms', 'query_date', 'url']

st.dataframe(
    df_query[ordered_columns].sort_values(by="price_per_m2"),
    column_config={
        "img": st.column_config.ImageColumn('📷Image', width="small"),
        "price_per_m2" : st.column_config.NumberColumn('💎PricePerArea',format="%0f $/m²"),
        "price" : st.column_config.NumberColumn('💶Price $',format="%,.0f $"),
        "sale_ratio" : st.column_config.ProgressColumn('💰Discount',format="%f",min_value=-50,max_value=100),
        "zestimate" : st.column_config.NumberColumn('🏷️ReferencePrice',format="%0f $"),
        "return" : st.column_config.NumberColumn('💰ReturnInYears'),
        "area_m2" : st.column_config.NumberColumn('📐Area',format="%0f m²"),
        "bedrooms" : st.column_config.TextColumn('🏨Bedrooms'),
        "bathrooms" : st.column_config.TextColumn('🛁Bathrooms'),
        "state" : st.column_config.TextColumn('🗺️State'),
        "city" : st.column_config.TextColumn('🏙️City'),
        "query_date" : st.column_config.DateColumn('📅Creation_Date',format="DD.MM.YYYY"),
        "url" : st.column_config.LinkColumn('🔗URL')
    },
    hide_index=True,width="stretch"
)

# Filter and group data
most_popular_cities = df.city.value_counts()[df.city.value_counts() > 50].index.tolist()

# Streamlit columns
column1, column2= st.columns([10,6])

from random import randrange
# Streamlit columns

def get_lat_lon( address: str) -> tuple:
    loc = Photon(user_agent="measurements")
    getLoc = loc.geocode(address + " USA")
    if getLoc:
        return [float(getLoc.latitude), float(getLoc.longitude)]
    return [None,None]

with column1:
    column1_1, column1_2, column1_3, column1_4 = st.columns([4,2,2,2])
    with column1_1:
        link = st.text_input(label="URL to inspect")
        if link == "":
            index = df.sample(1).index[0]
        else:
            index = df.query("url == @link").index.values[0]
        st.image(df.iloc[index].img, caption=df.iloc[index].address)
        st.markdown(f"[Link to Real Estate]({df.iloc[index].url})")
    with column1_2:
        st.metric(label="Price", value=f"{df.iloc[index].price:,.0f} $", delta=f"{round(df.iloc[index].price - df.iloc[index].zestimate)} $", delta_color="inverse")
        st.metric(label="Area", value=f"{df.iloc[index].area_m2:,.0f} m²")
        st.metric(label="Bathrooms", value=df.iloc[index].bathrooms)
        st.metric(label="City", value=df.iloc[index].city)
        
    with column1_3:
        st.metric(label="Price per m²", value=f"{df.iloc[index].price_per_m2:,.0f} $/m²", delta=f"{round(df.iloc[index].sale_ratio *100,1)} %", delta_color="inverse")
        st.metric(label="Reference rent price", value=f"{(df.iloc[index].rentZestimate / df.iloc[index].area_m2):,.2f} $/m²")
        st.metric(label="Bedrooms", value=df.iloc[index].bedrooms)
        st.metric(label="State", value=df.iloc[index].state)

    with column1_4: 
        try:
            st.metric(label="Expected annual rent", value=f"{(df.iloc[index].rentZestimate * 12):,.0f} $/year")
            st.metric(label="Expected monthly rent", value=f"{(df.iloc[index].rentZestimate):,.0f} $/month")
            st.metric(label="Return", value=f"{(df.iloc[index]["return"]):.2f} years")
            #st.metric(label="Days since last update", value=(datetime.date.today() - df.iloc[index].update_date.date()).days)
        except ValueError:
            st.metric(label="", value="")
    
with column2:
    try:
        lat = df.iloc[index].latitude
        lon = df.iloc[index].longitude
        if lat and lon:
            st.map(pd.DataFrame([{"lat": lat,"lon": lon}]), zoom=11, width="stretch")
    except:
            st.map(pd.DataFrame([{"lat": 51.233,"lon": 6.783}]), zoom=7, width="stretch")

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            section[data-testid="stSidebar"] {
                    width: 200px !important;
                    }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
