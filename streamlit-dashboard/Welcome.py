import pandas as pd
import streamlit as st
import datetime, json
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Real Estate Analytics", page_icon=":house:", layout="wide")

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

st.title(":house: Welcome to Real Estate Analytics")

st.markdown("""---""")

df = conn.read()

ordered_columns = ['image', 'url', 'title', 'city', 'district', 'price', 'area', \
                   'price_per_m2', 'ref_price', 'sale_ratio', 'return_in_years', 'source']

# st.dataframe(
#     df[ordered_columns].sort_values(by="return_in_years"),
#     column_config={
#         "image": st.column_config.ImageColumn('📷Image', width="small"),
#         "url" : st.column_config.LinkColumn('🔗URL'),
#         "price_per_m2" : st.column_config.NumberColumn('💎PricePerArea',format="%0f €/m²"),
#         "price" : st.column_config.NumberColumn('💶Price',format="%.0f €"),
#         "area" : st.column_config.NumberColumn('📐Area',format="%0f m²"),
#         "sale_ratio" : st.column_config.ProgressColumn('💰Discount (%)',format="%f",min_value=-100,max_value=100),
#         "ref_price" : st.column_config.NumberColumn('🏷️ReferencePrice',format="%0f €/m²"),
#         "return_in_years" : st.column_config.NumberColumn('💰ReturnInYears'),
#         "city" : st.column_config.TextColumn('🌍City'),
#         "district" : st.column_config.TextColumn('📌District'),
#         "source" : st.column_config.TextColumn('⚓Source'),
#         "title" : st.column_config.TextColumn('📕Title')
#     },
#     hide_index=True,use_container_width=True
# )

column1, column2, column3, column4, column5 = st.columns([2, 2, 1, 2, 3], gap="large")

with column1:
    low_price, high_price = st.select_slider('Price Range', options=range(0,1000001), value=(0,500000))

with column2:
    low_area, high_area = st.select_slider('Area', options=range(0,250), value=(60,200))
  
with column3:
    low_room, high_room = st.select_slider('Room Number', options=range(0,10), value=(3,6))

with column4:
    low_return, high_return = st.select_slider('Return in Years', options=range(0,100), value=(0,35))

series_city = df.city.value_counts()
common_cities = series_city[series_city > 15].index.tolist()

with column5:
    locations = st.multiselect("Cities", common_cities,["Düsseldorf", "Köln"])
    all_options = st.checkbox("Select all cities", value=False)

    if all_options:
        locations = common_cities
      
#queried dataframe
df_query = df.query("price >= @low_price and price <= @high_price") \
            .query("area >= @low_area and area <= @high_area") \
            .query("return_in_years >= @low_return and return_in_years <= @high_return") \
            .query("city in @locations")
            #.query("room >= @low_room and area <= @high_room")

ordered_columns = ['image', 'url', 'title', 'city', 'district', 'price', 'area', 'room', \
                   'price_per_m2', 'ref_price', 'sale_ratio', 'return_in_years', 'source']

st.dataframe(
    df_query[ordered_columns].sort_values(by="return_in_years"),
    column_config={
        "image": st.column_config.ImageColumn('📷Image', width="small"),
        "url" : st.column_config.LinkColumn('🔗URL'),
        "price_per_m2" : st.column_config.NumberColumn('💎PricePerArea',format="%0f €/m²"),
        "price" : st.column_config.NumberColumn('💶Price',format="%.0f €"),
        "area" : st.column_config.NumberColumn('📐Area',format="%0f m²"),
        "room" : st.column_config.NumberColumn('🏨Room'),
        "sale_ratio" : st.column_config.ProgressColumn('💰Discount (%)',format="%f",min_value=-100,max_value=100),
        "ref_price" : st.column_config.NumberColumn('🏷️ReferencePrice',format="%0f €/m²"),
        "return_in_years" : st.column_config.NumberColumn('💰ReturnInYears'),
        "city" : st.column_config.TextColumn('🌍City'),
        "district" : st.column_config.TextColumn('📌District'),
        "source" : st.column_config.TextColumn('⚓Source'),
        "title" : st.column_config.TextColumn('📕Title')
    },
    hide_index=True,use_container_width=True
)

column1, column2, column3, column4 = st.columns(4)
with column1:
    tile = column1.container(height=None, border=True)
    tile.write("Number of Ads analysed:")
    tile.subheader(f"🧮{df.shape[0]}")
with column2:
    tile = column2.container(height=None, border=True)
    tile.write("Mean price per Ad:")
    tile.subheader(f"💶 {round(df.price.mean().round()/1000)} k€")
with column3:
    tile = column3.container(height=None, border=True)
    tile.write("Number of houses:")
    tile.subheader(f"🏡 {df.estate_type.value_counts()["house"]}")
with column4:
    tile = column4.container(height=None, border=True)
    tile.write("Number of apartments:")
    tile.subheader(f"🏢 {df.estate_type.value_counts()["apartment"]}")


df_sales = df.groupby(["city"])["sale_ratio"] \
        .agg(["count", "mean"]) \
        .query("count > 5") \
        .sort_values(by="mean", ascending=False) \
        .query("mean <= 0") \
        .round(2)

fig = px.bar(
    df_sales,
    x='mean',
    y=df_sales.index,
    orientation='h',
    title='Mean Sale Ratio by City (Count > 5, Mean <= 0)',
    labels={'mean': 'Mean Sale Ratio', 'y': 'City'}
)

# Update the layout for better appearance
fig.update_layout(
    xaxis_title='Mean Sale Ratio',
    yaxis_title='City',
    height=600,  # You can adjust the height as needed
)

left_column, right_column = st.columns([2,8], gap="large")

left_column.plotly_chart(fig, use_container_width=True)

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
