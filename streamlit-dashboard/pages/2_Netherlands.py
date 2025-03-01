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

st.set_page_config(page_title="Netherlands Real Estate Market", page_icon=":tulip:", layout="wide")

# Create a connection object.
conn = st.connection("gsheets_netherlands", type=GSheetsConnection)

st.title(":tulip: Netherlands Real Estate Market")

df = conn.read()

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
    tile.write("Mean number of rooms")
    tile.subheader(f"🏡 {df.room.mean().round(2)}")
with column4:
    tile = column4.container(height=None, border=True)
    tile.write("Mean real estate area")
    tile.subheader(f"🏡 {round(df.area.mean().round()):,.0f} m²")
with column5:
    tile = column5.container(height=None, border=True)
    tile.write("Mean unit price")
    tile.subheader(f"📈 {round(df.price_per_m2.mean().round()):,.0f} €/m²")
with column6:
    today = datetime.date.today()
    t = today.strftime("%Y-%m-%d")
    added_today = df.query("query_date == @t").shape[0]
    tile = column6.container(height=None, border=True)
    tile.write("New ads published today")
    tile.subheader(f"🆕{added_today}")

st.markdown("""---""")

ordered_columns = ['image', 'address', 'city', 'price', 'area', \
                   'price_per_m2', 'room', 'source', 'url']

column1, column2, column3, column4= st.columns([2, 2, 1, 3], gap="large")

with column1:
    low_price, high_price = st.select_slider('Price Range', options=range(0,2000001), value=(0,500000))

with column2:
    low_area, high_area = st.select_slider('Area', options=range(0,650), value=(60,200))
  
with column3:
    low_room, high_room = st.select_slider('Room Number', options=range(0,50), value=(3,6))

series_city = df.city.value_counts()
common_cities = series_city[series_city > 25].index.tolist()

with column4:
    locations = st.multiselect("Cities", common_cities,["Den Haag"])
    all_options = st.checkbox("Select all cities", value=False)

    if all_options:
        locations = common_cities

      
#queried dataframe
df_query = df.query("price >= @low_price and price <= @high_price") \
            .query("area >= @low_area and area <= @high_area") \
            .query("city in @locations") \
            .query("room >= @low_room and room <= @high_room")

ordered_columns = ['image', 'address', 'city', 'price', 'area', \
                   'price_per_m2', 'room', 'source', 'url']

st.dataframe(
    df_query[ordered_columns].sort_values(by="price_per_m2"),
    column_config={
        "image": st.column_config.ImageColumn('📷Image', width="small"),
        "price_per_m2" : st.column_config.NumberColumn('💎PricePerArea',format="%0f €/m²"),
        "price" : st.column_config.NumberColumn('💶Price',format="%.0f €"),
        "area" : st.column_config.NumberColumn('📐Area',format="%0f m²"),
        "room" : st.column_config.NumberColumn('🏨Room'),
        "city" : st.column_config.TextColumn('🌍City'),
        "address" : st.column_config.TextColumn('Address'),
        "source" : st.column_config.TextColumn('⚓Source'),
        "title" : st.column_config.TextColumn('📕Title'),
        "url" : st.column_config.LinkColumn('🔗URL')
    },
    hide_index=True,use_container_width=True
)

# Filter and group data
most_popular_cities = df.city.value_counts()[df.city.value_counts() > 30].index.tolist()

# Streamlit columns
column1, column2= st.columns([10,6])

from random import randrange
# Streamlit columns

def get_lat_lon( address: str) -> tuple:
    loc = Photon(user_agent="measurements")
    getLoc = loc.geocode(address)
    if getLoc:
        return [float(getLoc.latitude), float(getLoc.longitude)]
    return [None,None]

with column1:
    column1_1, column1_2, column1_3, column1_4 = st.columns([4,2,4,2])
    with column1_1:
        # index = st.number_input(label="index", value=13585)
        link = st.text_input(label="URL to inspect")
        if link == "":
            index = 1
        else:
            index = df.query("url == @link").index.values[0]
        st.image(df.iloc[index].image, caption=df.iloc[index].title)
        st.markdown(f"[Link to Real Estate]({df.iloc[index].url})")
    with column1_2:
        st.metric(label="Price", value=f"{df.iloc[index].price:,.0f} €")
        st.metric(label="Area", value=f"{df.iloc[index].area:,.0f} m²")
        st.metric(label="City", value=df.iloc[index].city)
        
    with column1_3:
        st.metric(label="Price per m²", value=f"{df.iloc[index].price_per_m2:,.0f} €/m²", delta_color="inverse")
        st.metric(label="Address", value=df.iloc[index].address)
    # with column1_4: 
    #     try:
    #         st.metric(label="Expected annual rent", value=f"{(df.iloc[index].area * df.iloc[index].ref_rent_price * 12):,.0f} €/year")
    #         st.metric(label="Expected monthly rent", value=f"{(df.iloc[index].area * df.iloc[index].ref_rent_price):,.0f} €/month")
    #         st.metric(label="Yield ", value=f"{round((1 / df.iloc[index].return_in_years) * 100, 2)} %")
    #     except ValueError:
    #         st.metric(label="", value="")

with column2:
    try:
        lat, lon = get_lat_lon(df.iloc[index].address)
        if lat and lon:
            st.map(pd.DataFrame([{"lat": lat,"lon": lon}]), zoom=8, use_container_width=True)
    except:
            st.map(pd.DataFrame([{"lat": 51.233,"lon": 6.783}]), zoom=5.5, use_container_width=True)



left_column, middle_column, right_column = st.columns([3,5, 5], gap="large")

bins = [30,60,90,120,150,180,210]
df['category'] = pd.cut(df['area'], bins)
df_area_return = df.groupby("category")["price_per_m2"].agg(["mean"])
df_area_return.index = bins[:-1]

fig = px.bar(
    df_area_return,
    y='mean',
    x=df_area_return.index.tolist(),
)

fig.update_layout(xaxis_title='Area of estate',yaxis_title='Mean unit price',
                  legend=dict(orientation = "h",
                    yanchor="bottom", y=-0.3,
                    xanchor="left", x=0.01))

with left_column:
    st.subheader("Mean unit price per m²")
    left_column.plotly_chart(fig, use_container_width=True)

df2 = df[df.city.isin(most_popular_cities)] \
    .groupby(["city"])[["price_per_m2"]] \
    .mean().sort_values(by="price_per_m2").round(1)

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=df2.index,
    y=df2["price_per_m2"],
    name="Price per m²",
    yaxis="y1"
))

fig3.update_layout(barmode="group",
                    yaxis2=dict(
                        anchor='free',
                        overlaying='y',
                        side='right',
                        position=1
                    ),
                   legend=dict(orientation = "h",
                    yanchor="bottom", y=-0.7,
                    xanchor="left", x=0.01))

with middle_column:
    st.subheader("Average Price per m²")
    st.plotly_chart(fig3, use_container_width=True)


most_popular_cities = df.city.value_counts()[df.city.value_counts() > 50].index.tolist()

df_price = df[df.city.isin(most_popular_cities)].groupby(["city"])["price"] \
          .agg(["mean"]) \
          .sort_values(by="mean") \
          .round(2)

fig2 = go.Figure()

fig2.add_trace(go.Bar(
    x=df_price.index,
    y=df_price["mean"],
    name="mean price"
))

fig2.update_layout(
                   legend=dict(orientation = "h",
                    yanchor="bottom", y=-0.7,
                    xanchor="left", x=0.01))

with right_column:
    st.subheader("Average price of cities")
    right_column.plotly_chart(fig2, use_container_width=True)


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
