import pandas as pd
import streamlit as st
import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Photon

st.set_page_config(page_title="Real Estate Analytics", page_icon=":house:", layout="wide")

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

#conn2 = st.connection("gsheets_coordinates", type=GSheetsConnection)

st.title(":house: Welcome to Real Estate Analytics")

# @st.cache_data()
# def load_data():
#     return conn.read()

df = conn.read()

#df_coord = conn2.read()

column1, column2, column3, column4, column5, column6 = st.columns(6)
with column1:
    tile = column1.container(height=None, border=True)
    tile.write("Number of ads analysed")
    tile.subheader(f"🧮{df.shape[0]}")
with column2:
    tile = column2.container(height=None, border=True)
    tile.write("Mean price")
    tile.subheader(f"💶 {round(df.price.mean().round()/1000)} k€")
with column3:
    tile = column3.container(height=None, border=True)
    tile.write("Number of houses")
    tile.subheader(f"🏡 {df.estate_type.value_counts()['house']}")
with column4:
    tile = column4.container(height=None, border=True)
    tile.write("Number of apartments")
    tile.subheader(f"🏢 {df.estate_type.value_counts()['apartment']}")
with column5:
    tile = column5.container(height=None, border=True)
    tile.write("Mean return in years")
    tile.subheader(f"📈 {round(df.return_in_years.mean().round())}")
with column6:
    today = datetime.date.today()
    t = today.strftime("%Y-%m-%d")
    added_today = df.query("query_date == @t").shape[0]
    tile = column6.container(height=None, border=True)
    tile.write("New ads published today")
    tile.subheader(f"🆕{added_today}")

st.markdown("""---""")

df['creation_date'] = pd.to_datetime(df['creation_date'])
df['update_date'] = pd.to_datetime(df['update_date'])

ordered_columns = ['image', 'url', 'title', 'city', 'district', 'price', 'area', \
                   'price_per_m2', 'ref_price', 'sale_ratio', 'return_in_years', 'source']

column11, column22, column33, column44 = st.columns([2, 2, 2, 2])
column55, column66, column77, column88, column99= st.columns([2, 2, 2, 2, 2])

with column11:
    low_price, high_price = st.slider('Price Range', min_value=0, max_value=10000000, value=(0, 500000))

with column22:
    low_area, high_area = st.slider('Area', min_value=0, max_value=650, value=(60, 200))
  
with column33:
    low_room, high_room = st.slider('Room Number', min_value=0, max_value=50, value=(3, 6))

with column44:
    low_return, high_return = st.slider('Return in Years', min_value=0, max_value=100, value=(0, 35))

series_city = df.city.value_counts()
common_cities = series_city[series_city > 15].index.tolist()

with column55:
    locations = st.multiselect("Cities", common_cities,["Düsseldorf"])
    all_options = st.checkbox("Select all cities", value=False)

    if all_options:
        locations = common_cities

with column66:
    states = st.multiselect("State", df.state.unique().tolist(), "Nordrhein-Westfalen")

with column77:
    distribution_types = st.multiselect("Type" ,["Buy", "Rent"], ["Rent"])

with column88:
    types = st.multiselect("Estate Type", ["apartment", "house"],["apartment"])

with column99:

    date_options = ["Today", "Last Week", "Last Month", "All Time"]
    date_to_select = st.selectbox("Date Range", date_options)

    if date_to_select == "Today":
        dates = [datetime.date.today().strftime('%Y-%m-%d')]
    elif date_to_select == "Last Week":
        dates = pd.date_range(end=datetime.date.today(), periods=7).strftime('%Y-%m-%d').tolist()
    elif date_to_select == "Last Month":
        dates = pd.date_range(end=datetime.date.today(), periods=30).strftime('%Y-%m-%d').tolist()
    else:
        dates = df.creation_date.dt.strftime('%Y-%m-%d').unique().tolist()

    # dates = st.multiselect("Creation Date", df.creation_date.dt.strftime('%Y-%m-%d').unique().tolist(), date_to_select)
    # all_options = st.checkbox("Select all dates", value=False)

    # if all_options:
    #     dates = df.creation_date.dt.strftime('%Y-%m-%d').unique().tolist()
      
#queried dataframe
df_query = df.query("price >= @low_price and price <= @high_price") \
            .query("area >= @low_area and area <= @high_area") \
            .query("city in @locations") \
            .query("estate_type in @types") \
            .query("state in @states") \
            .query("distribution_type in @distribution_types") \
            .query("creation_date.dt.strftime('%Y-%m-%d') in @dates") \
            .query("room >= @low_room and room <= @high_room")

if distribution_types == "Buy":
    df_query = df.query("return_in_years >= @low_return and return_in_years <= @high_return")

ordered_columns = ['image', 'title', 'city', 'district', 'price', 'area', 'room','price_per_m2', \
                    'ref_price', 'sale_ratio', 'return_in_years', 'source', 'creation_date', 'url', "makler"]

st.dataframe(
    df_query[ordered_columns].sort_values(by="return_in_years"),
    column_config={
        "image": st.column_config.ImageColumn('📷Image', width="small"),
        "price_per_m2" : st.column_config.NumberColumn('💎PricePerArea',format="%0f €/m²"),
        "price" : st.column_config.NumberColumn('💶Price',format="%.0f €"),
        "area" : st.column_config.NumberColumn('📐Area',format="%0f m²"),
        "room" : st.column_config.NumberColumn('🏨Room'),
        "sale_ratio" : st.column_config.ProgressColumn('💰Discount (%)',format="%f",min_value=-50,max_value=100),
        "ref_price" : st.column_config.NumberColumn('🏷️ReferencePrice',format="%0f €/m²"),
        "return_in_years" : st.column_config.NumberColumn('💰ReturnInYears'),
        "city" : st.column_config.TextColumn('🌍City'),
        "district" : st.column_config.TextColumn('📌District'),
        "source" : st.column_config.TextColumn('⚓Source'),
        "title" : st.column_config.TextColumn('📕Title'),
        "creation_date" : st.column_config.DateColumn('📅Creation_Date',format="DD.MM.YYYY"),
        "url" : st.column_config.LinkColumn('🔗URL'),
        "makler" : st.column_config.TextColumn('Makler')
    },
    hide_index=True,use_container_width=True
)

# Filter and group data
most_popular_cities = df.city.value_counts()[df.city.value_counts() > 50].index.tolist()

# Streamlit columns
column1, column2= st.columns([10,6])

from random import randrange
import math
# Streamlit columns

def get_lat_lon( address: str) -> tuple:
    loc = Photon(user_agent="measurements")
    getLoc = loc.geocode(address)
    if getLoc:
        return [float(getLoc.latitude), float(getLoc.longitude)]
    return [None,None]

with column1:
    column1_1, column1_2, column1_3, column1_4 = st.columns([4,2,2,2])
    with column1_1:
        # index = st.number_input(label="index", value=13585)
        link = st.text_input(label="URL to inspect")
        if link == "":
            index = randrange(df.shape[0])
        else:
            index = df.query("url == @link").index.values[0]
        st.image(df.iloc[index].image, caption=df.iloc[index].headline)
        st.markdown(f"[Link to Real Estate]({df.iloc[index].url})")
        if pd.notna(df.iloc[index].description):
            with st.expander("See description"):
                st.write(df.iloc[index].description)
    with column1_2:
        st.metric(label="Price", value=f"{df.iloc[index].price:,.0f} €")
        st.metric(label="Area", value=f"{df.iloc[index].area:,.0f} m²")
        st.metric(label="City", value=df.iloc[index].city)
        st.metric(label="District", value=df.iloc[index].district)
        if pd.notna(df.iloc[index].makler):
            st.markdown(f"Makler: [{df.iloc[index].makler}]({df.iloc[index].makler_website})")
    with column1_3:
        st.metric(label="Price per m²", value=f"{df.iloc[index].price_per_m2:,.0f} €/m²", delta=f"{df.iloc[index].sale_ratio * -1} %", delta_color="inverse")
        st.metric(label="Reference rent price", value=f"{df.iloc[index].ref_rent_price:,.0f} €/m²")
        st.metric(label="Return in years", value=df.iloc[index].return_in_years)
        st.metric(label="Days since creation", value=(datetime.date.today() - df.iloc[index].creation_date.date()).days)
        st.metric(label="Type", value=df.iloc[index].distribution_type)
    with column1_4: 
        try:
            st.metric(label="Expected annual rent", value=f"{(df.iloc[index].area * df.iloc[index].ref_rent_price * 12):,.0f} €/year")
            st.metric(label="Expected monthly rent", value=f"{(df.iloc[index].area * df.iloc[index].ref_rent_price):,.0f} €/month")
            st.metric(label="Yield ", value=f"{round((1 / df.iloc[index].return_in_years) * 100, 2)} %")
            st.metric(label="Days since last update", value=(datetime.date.today() - df.iloc[index].update_date.date()).days)
        except ValueError:
            st.metric(label="", value="")

with column2:
    try:
        lat, lon = get_lat_lon(df.iloc[index].zip_code + " " + df.iloc[index].city+ " " + df.iloc[index].district)
        if lat and lon:
            st.map(pd.DataFrame([{"lat": lat,"lon": lon}]), zoom=6.5, use_container_width=True)
    except:
            st.map(pd.DataFrame([{"lat": 51.233,"lon": 6.783}]), zoom=7, use_container_width=True)


#---- HIDE STREAMLIT STYLE ----
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
