import pandas as pd
import streamlit as st
import datetime, json
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Real Estate Analytics", page_icon=":house:", layout="wide")

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

st.title(":house: Welcome to Real Estate Analytics")

df = conn.read()

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

st.markdown("""---""")

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

left_column, right_column = st.columns([3,7], gap="large")

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
    title='Cheapest Cities'
)

left_column.plotly_chart(fig, use_container_width=True)

df_returns = df.groupby(["city", "estate_type"])["return_in_years"] \
          .agg(["count", "mean"]) \
          .query("count > 20") \
          .sort_values(by="mean") \
          .round(2)["mean"] \
          .unstack()

fig2 = go.Figure()
for estate_type in df_returns.columns:
    fig2.add_trace(go.Bar(
        x=df_returns.index,
        y=df_returns[estate_type],
        name=estate_type
    ))

fig2.update_layout(title_text='Return of investment in years')

right_column.plotly_chart(fig2, use_container_width=True)

column1, column2, column3 = st.columns([2,3,5])

with column1:
    grunderwerb = st.number_input('Grunderwerbssteuer [%]', value=6.5)
    notar = st.number_input('Notarkosten [%]', value=1.5)
    grundbuch = st.number_input('Grundbucheintrag [%]', value=0.5)
    provision = st.number_input('Maklerprovision [%]', value=3.75)
    price = st.number_input('Real Estate Price', value=500000)
    eigen = st.number_input('Eigenkapital [%]', value=25)

    zinsen = st.number_input('Zinssatz [%/year]', value=3.1)
    tilgung = st.number_input('Tilgungssatz [%/year]', value=4.0)
    years = st.number_input('Years', value=10, key=int)

# Total cost including additional fees
total_cost = price * (1 + (grunderwerb + notar + grundbuch + provision) / 100)
loan_amount = total_cost * (1 - eigen / 100)
annual_interest = loan_amount * zinsen / 100
annuitat =  loan_amount * (zinsen + tilgung) / 100

# Amortization schedule over 10 years
remaining_debt = loan_amount
amortization_schedule = []

for year in range(1, years + 1):
    interest_payment = remaining_debt * zinsen / 100
    principal_payment = annuitat - interest_payment
    total_payment = interest_payment + principal_payment
    remaining_debt -= principal_payment
    
    amortization_schedule.append({
        "Year": year,
        "Interest Payment": round(interest_payment, 2),
        "Principal Payment": round(principal_payment, 2),
        "Total Payment": round(total_payment, 2),
        "Remaining Debt": round(remaining_debt, 2)
    })

df_amortization = pd.DataFrame(amortization_schedule)

with column2:
    st.dataframe(df_amortization ,
                    hide_index=True,use_container_width=True)

    st.write(f"Total initial debts: {price*(1 + (grunderwerb+notar+grundbuch+provision)/100)*(1 - eigen/100)}")
    st.write(f"Remaning debts: {df_amortization.loc[year-1, "Remaining Debt"].round()}")
    st.write(f"Money paid to interest: {df_amortization["Interest Payment"].sum().round()}")
    st.write(f"Debt paid back: {df_amortization["Principal Payment"].sum().round()}")

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=df_amortization['Year'],
    y=df_amortization['Interest Payment'],
    name='Interest Payment',
    marker_color='indianred'
))

# Add Principal Payment bars
fig3.add_trace(go.Bar(
    x=df_amortization['Year'],
    y=df_amortization['Principal Payment'],
    name='Debt Payment',
    marker_color='lightsalmon'
))

# Update layout for better appearance
fig3.update_layout(
    title='Amortization Schedule',
    xaxis_title='Year',
    yaxis_title='Amount (€)',
    barmode='stack',
    height=500,
    width=1000
)

with column3:
    column3.plotly_chart(fig3, use_container_width=True)

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
