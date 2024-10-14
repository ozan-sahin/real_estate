import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Real Estate Analytics", page_icon=":house:", layout="wide")

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

st.title(":house: Welcome to Real Estate Analytics")

df = conn.read()

column1, column2, column3, column4, column5 = st.columns(5)
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

st.markdown("""---""")

ordered_columns = ['image', 'url', 'title', 'city', 'district', 'price', 'area', \
                   'price_per_m2', 'ref_price', 'sale_ratio', 'return_in_years', 'source']

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
        "sale_ratio" : st.column_config.ProgressColumn('💰Discount (%)',format="%f",min_value=-50,max_value=100),
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
        .query("count > 20") \
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

fig.update_layout(legend=dict(orientation = "h",
                    yanchor="bottom", y=-0.3,
                    xanchor="left", x=0.01))


left_column.plotly_chart(fig, use_container_width=True)

df_returns = df.groupby(["city", "estate_type"])["return_in_years"] \
          .agg(["count", "mean"]) \
          .query("count > 17") \
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

fig2.update_layout(
                   legend=dict(orientation = "h",
                    yanchor="bottom", y=-0.3,
                    xanchor="left", x=0.01))

with right_column:
    st.subheader("Return of investment in years")
    right_column.plotly_chart(fig2, use_container_width=True)

st.subheader("Finance")

column1, column2, column3 = st.columns([2,6,3])

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

    if remaining_debt >= annuitat:
        interest_payment = remaining_debt * zinsen / 100
        principal_payment = annuitat - interest_payment
        total_payment = interest_payment + principal_payment
        remaining_debt -= principal_payment
    else:
        interest_payment = remaining_debt * zinsen / 100
        principal_payment = remaining_debt - interest_payment
        total_payment = interest_payment + principal_payment
        remaining_debt = 0

        
    amortization_schedule.append({
        "Year": year,
        "Interest": round(interest_payment, 2),
        "Payback": round(principal_payment, 2),
        "Total Payment": round(total_payment, 2),
        "Remaining Debt": round(remaining_debt, 2),
        "Monthly" : round(total_payment / 12, 2)
    })

df_amortization = pd.DataFrame(amortization_schedule)

with column2:
    st.dataframe(df_amortization , column_config={
        "Interest" : st.column_config.NumberColumn('Interest',format="%.0f €"),
        "Payback" : st.column_config.NumberColumn('Payback',format="%.0f €"),
        "Total Payment" : st.column_config.NumberColumn('Total Payment',format="%.0f €"),
        "Remaining Debt" : st.column_config.NumberColumn('Remaining Debt',format="%.0f €"),
        "Monthly" : st.column_config.NumberColumn('Monhtly',format="%.0f €")
    },
        hide_index=True,use_container_width=True, height=500)

    column11, column22, column33 = st.columns(3)
    column44, column55, column66 = st.columns(3)

    with column11:
        tile = column11.container(height=None, border=True)
        tile.metric(label="Eigenkapital", value=f"{price*eigen/100:,.0f} €")
    with column22:
        tile = column22.container(height=None, border=True)
        tile.metric(label="Money Borrowed", value=f"{price*(1 + (grunderwerb+notar+grundbuch+provision)/100)*(1 - eigen/100):,.0f} €")
    with column33:
        tile = column33.container(height=None, border=True)
        tile.metric(label="Remaining Debt", value=f"{df_amortization.loc[year-1, 'Remaining Debt'].round():,.0f} €")
    with column44:
        tile = column44.container(height=None, border=True)
        tile.metric(label="Total Interest Payment", value=f"{df_amortization['Interest'].sum().round():,.0f} €")
    with column55:
        tile = column55.container(height=None, border=True)
        tile.metric(label="Total Payback", value=f"{df_amortization['Payback'].sum().round():,.0f} €")
    with column66:
        tile = column66.container(height=None, border=True)
        tile.metric(label="Monthly Payment", value=f"{(df_amortization.loc[1,'Total Payment']/12).round()}")

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=df_amortization['Year'],
    y=df_amortization['Interest'],
    name='Interest',
    marker_color='indianred'
))

# Add Payback bars
fig3.add_trace(go.Bar(
    x=df_amortization['Year'],
    y=df_amortization['Payback'],
    name='Debt Payment',
    marker_color='lightsalmon'
))

# Update layout for better appearance
fig3.update_layout(
    xaxis_title='Year',yaxis_title='Amount (€)',barmode='stack',
    legend=dict(orientation = "h",
    yanchor="bottom", y=-0.3,
    xanchor="left", x=0.01)
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
