import pandas as pd
import streamlit as st
import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection
from geopy.geocoders import Photon

st.set_page_config(page_title="Italy Real Estate Market", page_icon="🍕", layout="wide")

# Create a connection object.
conn = st.connection("gsheets_italy", type=GSheetsConnection)

st.title("🍕 Italy Real Estate Market")

df = conn.read()
df['query_date'] = pd.to_datetime(df['query_date'])

column1, column2, column3, column4, column5, column6 = st.columns(6)
with column1:
    tile = column1.container(height="content", border=True)
    tile.write("Number of ads analysed")
    tile.subheader(f"🧮{df.shape[0]}")
with column2:
    tile = column2.container(height="content", border=True)
    tile.write("Mean price")
    tile.subheader(f"💶 {round(df.price.mean().round()/1000)} k€")
with column3:
    tile = column3.container(height="content", border=True)
    tile.write("Mean number of rooms")
    tile.subheader(f"🏡 {df.rooms.mean().round(2)}")
with column4:
    tile = column4.container(height="content", border=True)
    tile.write("Mean real estate area")
    tile.subheader(f"🏡 {round(df.area.mean().round()):,.0f} m²")
with column5:
    tile = column5.container(height="content", border=True)
    tile.write("Mean unit price")
    tile.subheader(f"📈 {round(df.price_per_m2.mean().round()):,.0f} €/m²")
with column6:
    today = datetime.date.today()
    t = today.strftime("%Y-%m-%d")
    added_today = df.query("query_date == @t").shape[0]
    tile = column6.container(height="content", border=True)
    tile.write("New ads published today")
    tile.subheader(f"🆕{added_today}")

st.markdown("""---""")

ordered_columns = ['image', 'title', 'province', 'price', 'area', \
                   'price_per_m2', 'rooms', 'query_date', 'url']

column1, column2, column3, column4, column5 = st.columns([2, 2, 1, 3, 2], gap="large")

with column1:
    low_price, high_price = st.select_slider('Price Range', options=range(0,2000001), value=(0,500000))

with column2:
    low_area, high_area = st.select_slider('Area', options=range(0,650), value=(60,200))
  
# with column3:
#     low_room, high_room = st.select_slider('Room Number', options=range(0,50), value=(3,6))

series_city = df.county.value_counts()
common_cities = series_city[series_city > 10].index.tolist()

with column4:
    locations = st.multiselect("Cities", common_cities,[])
    all_options = st.checkbox("Select all cities", value=True)

    if all_options:
        locations = common_cities

with column5:

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


#queried dataframe
df_query = df.query("price >= @low_price and price <= @high_price") \
            .query("area >= @low_area and area <= @high_area") \
            .query("county in @locations") \
            .query("query_date.dt.strftime('%Y-%m-%d') in @dates")

ordered_columns = ['image', 'title', 'province', 'county', 'price', 'area', \
                   'price_per_m2', 'rooms', 'query_date', 'url']

st.dataframe(
    df_query[ordered_columns].sort_values(by="price_per_m2"),
    column_config={
        "image": st.column_config.ImageColumn('📷Image', width="small"),
        "price_per_m2" : st.column_config.NumberColumn('💎PricePerArea',format="%0f €/m²"),
        "price" : st.column_config.NumberColumn('💶Price €',format="%.0f €"),
        # "sale_ratio" : st.column_config.NumberColumn('📈Sale Ratio'),
        "area" : st.column_config.NumberColumn('📐Area',format="%0f m²"),
        "rooms" : st.column_config.TextColumn('🏨Room'),
        "province" : st.column_config.TextColumn('🗺️Province'),
        "county" : st.column_config.TextColumn('🧭County'),
        "title" : st.column_config.TextColumn('📕Title'),
        "query_date" : st.column_config.DateColumn('📅Creation_Date',format="DD.MM.YYYY"),
        "url" : st.column_config.LinkColumn('🔗URL')
    },
    hide_index=True,use_container_width=True
)

# Filter and group data
most_popular_cities = df.county.value_counts()[df.county.value_counts() > 10].index.tolist()

# Streamlit columns
column1, column2= st.columns([10,6])

from random import randrange
# Streamlit columns

def get_lat_lon( address: str) -> tuple:
    loc = Photon(user_agent="measurements")
    getLoc = loc.geocode(address + " Italy")
    if getLoc:
        return [float(getLoc.latitude), float(getLoc.longitude)]
    return [None,None]

with column1:
    column1_1, column1_2, column1_3, column1_4 = st.columns([4,4,6,1])
    with column1_1:
        # index = st.number_input(label="index", value=13585)
        link = st.text_input(label="URL to inspect")
        if link == "":
            index = 1
        else:
            index = df.query("url == @link").index.values[0]
        st.image(df.iloc[index].image, caption=df.iloc[index].title)
        st.markdown(f"[Link to Real Estate]({df.iloc[index].url})")
        if pd.notna(df.iloc[index].description):
            with st.expander("See description"):
                st.write(df.iloc[index].description)
    with column1_2:
        st.metric(label="Price", value=f"{df.iloc[index].price:,.0f} €")
        st.metric(label="Area", value=f"{df.iloc[index].area:,.0f} m²")
        st.metric(label="City", value=df.iloc[index].province)
        
    with column1_3:
        st.metric(label="Price per m²", value=f"{df.iloc[index].price_per_m2:,.0f} €/m²", delta_color="inverse")
        #st.metric(label="Reference price per m²", value=f"{df.iloc[index].ref_price_per_m2 / 37:,.0f} €/m²")
        st.metric(label="County", value=df.iloc[index].county)
        #st.metric(label="Type", value=df.iloc[index].estate_type)

with column2:
    try:
        lat, lon = get_lat_lon(df.iloc[index].county)
        if lat and lon:
            st.map(pd.DataFrame([{"lat": lat,"lon": lon}]), zoom=11, use_container_width=True)
    except:
            st.map(pd.DataFrame([{"lat": 51.233,"lon": 6.783}]), zoom=7, use_container_width=True)



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
    st.subheader("Mean unit price in € per m²")
    left_column.plotly_chart(fig, use_container_width=True)

df2 = df[df.county.isin(most_popular_cities)] \
    .groupby(["county"])[["price_per_m2"]] \
    .mean().sort_values(by="price_per_m2").round(1)

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=df2.index,
    y=df2["price_per_m2"],
    name="Price € per m²",
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
    st.subheader("Average Price € per m²")
    st.plotly_chart(fig3, use_container_width=True)


most_popular_cities = df.county.value_counts()[df.county.value_counts() > 10].index.tolist()

df_price = df[df.county.isin(most_popular_cities)].groupby(["county"])["price"] \
          .agg(["mean"]) \
          .sort_values(by="mean") \
          .round(2)

fig2 = go.Figure()

fig2.add_trace(go.Bar(
    x=df_price.index,
    y=df_price["mean"],
    name="mean price in €"
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
