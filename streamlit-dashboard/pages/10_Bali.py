import pandas as pd
import streamlit as st
import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection
from geopy.geocoders import Photon

st.set_page_config(page_title="Bali Real Estate Market", page_icon="🌴", layout="wide")

# Create a connection object.
conn = st.connection("gsheets_bali", type=GSheetsConnection)

st.title("🌴 Bali Real Estate Market")

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
    tile.subheader(f"💶 {round(df.price.mean().round()/1000)} k€")
with column3:
    tile = column3.container( border=True)
    tile.write("Mean number of bedrooms")
    tile.subheader(f"🏡 {df.room.mean().round(2)}")
with column4:
    tile = column4.container( border=True)
    tile.write("Mean real estate area")
    tile.subheader(f"🏡 {round(df.area.mean().round()):,.0f} m²")
with column5:
    tile = column5.container( border=True)
    tile.write("Mean unit price")
    tile.subheader(f"📈 {round(df.price_per_m2.mean().round()):,.0f} €/m²")
with column6:
    today = datetime.date.today()
    added_today = df[df['query_date'].dt.date == today].shape[0]
    tile = column6.container( border=True)
    tile.write("New ads published today")
    tile.subheader(f"🆕{added_today}")

st.markdown("""---""")

ordered_columns = ['image', 'title', 'address', 'price', 'area', \
                   'price_per_m2', 'room', 'query_date', 'url']

column1, column2, column3, column6 = st.columns([2, 2, 1, 2])

with column1:
    low_price, high_price = st.select_slider('Price Range', options=range(0, 5_000_001, 10_000), value=(0,800000))

with column2:
    low_area, high_area = st.select_slider('Area', options=range(0,650), value=(60,200))

with column3:
    addresses = st.multiselect("Neighborhood", df.address.sort_values().unique().tolist(),[])
    all_options = st.checkbox("Select all neighborhoods", value=True)

    if all_options:
        addresses = df.address.sort_values().unique().tolist()
        

# with column5:
#     cities = st.multiselect("Cities", df.city.sort_values().unique().tolist(),[])
#     all_options_cities = st.checkbox("Select all cities", value=True)

#     if all_options_cities:
#         cities = df.city.sort_values().unique().tolist()

with column6:

    date_options = ["Today", "Last Week", "Last Month", "All Time"]
    date_to_select = st.selectbox("Date Range", date_options)

    if date_to_select == "Today":
        dates = [datetime.date.today().strftime('%Y-%m-%d')]
    elif date_to_select == "Last Week":
        dates = pd.date_range(end=datetime.date.today(), periods=7).strftime('%Y-%m-%d').tolist()
    elif date_to_select == "Last Month":
        dates = pd.date_range(end=datetime.date.today(), periods=30).strftime('%Y-%m-%d').tolist()
    else:
        dates = df.query_date.dt.strftime('%Y-%m-%d').unique().tolist()

df_query = df.query("price >= @low_price and price <= @high_price") \
            .query("area >= @low_area and area <= @high_area") \
            .query("address in @addresses") \
            .query("query_date.dt.strftime('%Y-%m-%d') in @dates").copy()

ordered_columns = ['image', 'title', 'address', 'price', 'area', \
                   'price_per_m2', 'room', 'query_date', 'url']

st.dataframe(
    df_query[ordered_columns].sort_values(by="price_per_m2"),
    column_config={
        "image": st.column_config.ImageColumn('📷Image', width="small"),
        "price_per_m2" : st.column_config.NumberColumn('💎PricePerArea',format="%0f $/m²"),
        "title" : st.column_config.TextColumn('Title'),
        "price" : st.column_config.NumberColumn('💶Price $',format="%,.0f $"),
        "address" : st.column_config.TextColumn('🏠Address'),
        "area" : st.column_config.NumberColumn('📐Area',format="%0f m²"),
        "room" : st.column_config.TextColumn('🏨Bedrooms'),
        "query_date" : st.column_config.DateColumn('📅Creation_Date',format="DD.MM.YYYY"),
        "url" : st.column_config.LinkColumn('🔗URL')
    },
    hide_index=True,width="stretch"
)

# Streamlit columns
column1, column2= st.columns([10,6])

from random import randrange
# Streamlit columns

def get_lat_lon( address: str) -> tuple:
    loc = Photon(user_agent="measurements")
    getLoc = loc.geocode(address + " Indonesia")
    if getLoc:
        return [float(getLoc.latitude), float(getLoc.longitude)]
    return [None,None]

with column1:
    column1_1, column1_2, column1_3 = st.columns([4,2,2])
    with column1_1:
        link = st.text_input(label="URL to inspect")
        if link == "":
            index = 1
        else:
            index = df.query("url == @link").index.values[0]
        st.image(df.iloc[index].image, caption=df.iloc[index].title)
        st.markdown(f"[Link to Real Estate]({df.iloc[index].url})")
    with column1_2:
        st.metric(label="Price", value=f"{df.iloc[index].price:,.0f} $")
        st.metric(label="Area", value=f"{df.iloc[index].area:,.0f} m²")
        st.metric(label="Bathrooms", value=df.iloc[index].bathrooms)
        st.metric(label="City", value=df.iloc[index].city)
        
    with column1_3:
        st.metric(label="Price per m²", value=f"{df.iloc[index].price_per_m2:,.0f} $/m²", delta_color="inverse")
        st.metric(label="Bedrooms", value=df.iloc[index].room)
        st.metric(label="Address", value=df.iloc[index].address)
    
with column2:
    try:
        lat, lon = get_lat_lon(df.iloc[index].address)
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
