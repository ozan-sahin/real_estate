import pandas as pd
import streamlit as st
import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection
from geopy.geocoders import Photon

st.set_page_config(page_title="USA Real Estate Market", page_icon="🌭", layout="wide")

# Create a connection object.
conn = st.connection("gsheets_usa", type=GSheetsConnection)

st.title("🌭 USA Real Estate Market")

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
    tile.subheader(f"📈 {round(df.price_per_m2.mean().round()):,.0f} $/m²")
with column6:
    today = datetime.date.today()
    added_today = df[df['query_date'].dt.date == today].shape[0]
    tile = column6.container( border=True)
    tile.write("New ads published today")
    tile.subheader(f"🆕{added_today}")

st.markdown("""---""")

ordered_columns = ['img', 'state', 'county', 'city', 'price', 'area_m2', \
                   'price_per_m2', 'bedrooms', 'query_date', 'url']

column1, column2, column3, column4, column5, column6 = st.columns([2, 2, 1, 2, 2, 2])

with column1:
    low_price, high_price = st.select_slider('Price Range', options=range(0, 5_000_001, 10_000), value=(0,800000))

with column2:
    low_area, high_area = st.select_slider('Area', options=range(0,650), value=(60,200))

with column4:
    states = st.multiselect("States", df.state.sort_values().unique().tolist(),[])
    all_options = st.checkbox("Select all states", value=True)

    if all_options:
        states = df.state.sort_values().unique().tolist()

with column5:
    cities = st.multiselect("Cities", df.city.sort_values().unique().tolist(),[])
    all_options_cities = st.checkbox("Select all cities", value=True)

    if all_options_cities:
        cities = df.city.sort_values().unique().tolist()

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
            .query("area_m2 >= @low_area and area_m2 <= @high_area") \
            .query("city in @cities") \
            .query("state in @states") \
            .query("query_date.dt.strftime('%Y-%m-%d') in @dates").copy()

ordered_columns = ['img', 'state', 'county', 'city', 'price', 'area_m2', \
                   'price_per_m2', 'bedrooms', 'bathrooms', 'address', 'query_date', 'url']

st.dataframe(
    df_query[ordered_columns].sort_values(by="price_per_m2"),
    column_config={
        "img": st.column_config.ImageColumn('📷Image', width="small"),
        "price_per_m2" : st.column_config.NumberColumn('💎PricePerArea',format="%0f $/m²"),
        "price" : st.column_config.NumberColumn('💶Price $',format="%,.0f $"),
        "address" : st.column_config.TextColumn('🏠Address'),
        "area_m2" : st.column_config.NumberColumn('📐Area',format="%0f m²"),
        "bedrooms" : st.column_config.TextColumn('🏨Bedrooms'),
        "bathrooms" : st.column_config.TextColumn('🛁Bathrooms'),
        "state" : st.column_config.TextColumn('🗺️State'),
        "county" : st.column_config.TextColumn('🧭County'),
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
    column1_1, column1_2, column1_3 = st.columns([4,2,2])
    with column1_1:
        link = st.text_input(label="URL to inspect")
        if link == "":
            index = 1
        else:
            index = df.query("url == @link").index.values[0]
        st.image(df.iloc[index].img, caption=df.iloc[index].address)
        st.markdown(f"[Link to Real Estate]({df.iloc[index].url})")
    with column1_2:
        st.metric(label="Price", value=f"{df.iloc[index].price:,.0f} $")
        st.metric(label="Area", value=f"{df.iloc[index].area_m2:,.0f} m²")
        st.metric(label="Bathrooms", value=df.iloc[index].bathrooms)
        st.metric(label="City", value=df.iloc[index].city)
        
    with column1_3:
        st.metric(label="Price per m²", value=f"{df.iloc[index].price_per_m2:,.0f} $/m²", delta_color="inverse")
        st.metric(label="Bedrooms", value=df.iloc[index].bedrooms)
        st.metric(label="County", value=df.iloc[index].county)
        st.metric(label="State", value=df.iloc[index].state)
    
with column2:
    try:
        lat, lon = get_lat_lon(df.iloc[index].address)
        if lat and lon:
            st.map(pd.DataFrame([{"lat": lat,"lon": lon}]), zoom=11, width="stretch")
    except:
            st.map(pd.DataFrame([{"lat": 51.233,"lon": 6.783}]), zoom=7, width="stretch")



# left_column, middle_column, right_column = st.columns([3,5, 5], gap="large")

# bins = [30,60,90,120,150,180,210]
# df['category'] = pd.cut(df['area_m2'], bins)
# df_area_return = df.groupby("category")["price_per_m2"].agg(["mean"])
# df_area_return.index = bins[:-1]

# fig = px.bar(
#     df_area_return,
#     y='mean',
#     x=df_area_return.index.tolist(),
# )

# fig.update_layout(xaxis_title='Area of estate',yaxis_title='Mean unit price',
#                   legend=dict(orientation = "h",
#                     yanchor="bottom", y=-0.3,
#                     xanchor="left", x=0.01))

# with left_column:
#     st.subheader("Mean unit price in $ per m²")
#     left_column.plotly_chart(fig, use_container_width=True)

# df2 = df[df.city.isin(most_popular_cities)] \
#     .groupby(["city"])[["price_per_m2"]] \
#     .mean().sort_values(by="price_per_m2").round(1)

# fig3 = go.Figure()
# fig3.add_trace(go.Bar(
#     x=df2.index,
#     y=df2["price_per_m2"],
#     name="Price $ per m²",
#     yaxis="y1"
# ))

# fig3.update_layout(barmode="group",
#                     yaxis2=dict(
#                         anchor='free',
#                         overlaying='y',
#                         side='right',
#                         position=1
#                     ),
#                    legend=dict(orientation = "h",
#                     yanchor="bottom", y=-0.7,
#                     xanchor="left", x=0.01))

# with middle_column:
#     st.subheader("Average Price $ per m²")
#     st.plotly_chart(fig3, use_container_width=True)


# most_popular_cities = df.city.value_counts()[df.city.value_counts() > 10].index.tolist()

# df_price = df[df.city.isin(most_popular_cities)].groupby(["city"])["price"] \
#           .agg(["mean"]) \
#           .sort_values(by="mean") \
#           .round(2)

# fig2 = go.Figure()

# fig2.add_trace(go.Bar(
#     x=df_price.index,
#     y=df_price["mean"],
#     name="mean price in $"

# ))

# fig2.update_layout(
#                    legend=dict(orientation = "h",
#                     yanchor="bottom", y=-0.7,
#                     xanchor="left", x=0.01))

# with right_column:
#     st.subheader("Average price of cities")
#     right_column.plotly_chart(fig2, use_container_width=True)


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
