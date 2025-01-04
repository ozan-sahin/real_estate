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

@st.cache_data(ttl=600)
def load_data():
    return conn.read()

df = load_data()

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

column1, column2, column3, column4 = st.columns([2, 2, 2, 2], gap="large")
column5, column6, column7, column8, column9= st.columns([2, 2, 2, 2, 2], gap="large")

with column1:
    low_price, high_price = st.select_slider('Price Range', options=range(0,10000001), value=(0,500000))

with column2:
    low_area, high_area = st.select_slider('Area', options=range(0,650), value=(60,200))
  
with column3:
    low_room, high_room = st.select_slider('Room Number', options=range(0,50), value=(3,6))

with column4:
    low_return, high_return = st.select_slider('Return in Years', options=range(0,100), value=(0,35))

series_city = df.city.value_counts()
common_cities = series_city[series_city > 15].index.tolist()

with column5:
    locations = st.multiselect("Cities", common_cities,["Düsseldorf", "Köln"])
    all_options = st.checkbox("Select all cities", value=False)

    if all_options:
        locations = common_cities

with column6:
    states = st.multiselect("State", df.state.unique().tolist(), "Nordrhein-Westfalen")

with column7:
    distribution_types = st.multiselect("Type" ,["Buy", "Rent"], ["Rent"])

with column8:
    types = st.multiselect("Estate Type", ["apartment", "house"],["apartment"])

with column9:

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
            #.query("room >= @low_room and room <= @high_room") \
            #.query("return_in_years >= @low_return and return_in_years <= @high_return")

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

# left_column, right_column = st.columns([3,5], gap="large")

# bins = [60,90,120,150,180,210]
# df['category'] = pd.cut(df['area'], bins)
# df_area_return = df.groupby("category")["return_in_years"].agg(["mean"])
# df_area_return.index = bins[:-1]

# fig = px.bar(
#     df_area_return,
#     y='mean',
#     x=df_area_return.index.tolist(),
# )

# fig.update_layout(xaxis_title='Area of estate',yaxis_title='Return of investment in years',
#                   legend=dict(orientation = "h",
#                     yanchor="bottom", y=-0.3,
#                     xanchor="left", x=0.01))

# with left_column:
#     st.subheader("Return of investment per m²")
#     left_column.plotly_chart(fig, use_container_width=True)

# most_popular_cities = df.city.value_counts()[df.city.value_counts() > 50].index.tolist()

# df_returns = df[df.city.isin(most_popular_cities)].groupby(["city", "estate_type"])["return_in_years"] \
#           .agg(["count", "mean"]) \
#           .query("count > 30") \
#           .sort_values(by="mean") \
#           .round(2)["mean"] \
#           .unstack()

# fig2 = go.Figure()
# for estate_type in df_returns.columns:
#     fig2.add_trace(go.Bar(
#         x=df_returns.index,
#         y=df_returns[estate_type],
#         name=estate_type
#     ))

# fig2.update_layout(
#                    legend=dict(orientation = "h",
#                     yanchor="bottom", y=-0.7,
#                     xanchor="left", x=0.01))

# with right_column:
#     st.subheader("Return of investment of biggest cities")
#     right_column.plotly_chart(fig2, use_container_width=True)

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


# df2 = df[df.city.isin(most_popular_cities)] \
#     .groupby(["city"])[["price_per_m2", "ref_rent_price"]] \
#     .mean().round(1)

# fig3 = go.Figure()
# fig3.add_trace(go.Bar(
#     x=df2.index,
#     y=df2["price_per_m2"],
#     name="Price per m²",
#     yaxis="y1"
# ))

# fig3.add_trace(go.Bar(
#     x=df2.index,
#     y=df2["ref_rent_price"],
#     name="Reference rent per m² (right axis)",
#     yaxis="y2"
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

# with column2:
#     st.subheader("Average Price per m² and Reference Rent Price by City")
#     st.plotly_chart(fig3, use_container_width=True)

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

    st.subheader("Tax")
    gebaude_wert_anteil = st.number_input('Gebäudewertanteil [%]', value=60)

# Total cost including additional fees
total_cost = price * (1 + (grunderwerb + notar + grundbuch + provision) / 100)
loan_amount = total_cost * (1 - eigen / 100)
annual_interest = loan_amount * zinsen / 100
annuitat =  loan_amount * (zinsen + tilgung) / 100 / 12

# Amortization schedule over 10 years
remaining_debt = loan_amount
amortization_schedule = []

for month in range(1, (years + 1)*12 ):

    if remaining_debt >= annuitat:
        interest_payment = remaining_debt * zinsen / 100 /12
        principal_payment = annuitat - interest_payment
        total_payment = interest_payment + principal_payment
        remaining_debt -= principal_payment
    else:
        interest_payment = remaining_debt * zinsen / 100 / 12
        principal_payment = remaining_debt - interest_payment
        total_payment = interest_payment + principal_payment
        remaining_debt = 0

        
    amortization_schedule.append({
        "Month": month,
        "Interest": round(interest_payment, 2),
        "Payback": round(principal_payment, 2),
        "Total Payment": round(total_payment, 2),
        "Remaining Debt": round(remaining_debt, 2),
        "Monthly" : round(total_payment, 2)
    })

df_amortization = pd.DataFrame(amortization_schedule)

# Amortization years
amortization_in_total = math.log(annuitat / (annuitat - loan_amount * zinsen / 100 / 12)) / math.log(1 + zinsen / 100 / 12)

with column2:

    column11, column22, column33 = st.columns(3)
    column44, column55, column66 = st.columns(3)
    column77, column88, column99 = st.columns(3)

    column111, column222, column333 = st.columns(3)

    with column11:
        tile = column11.container(height=None, border=True)
        tile.metric(label="Eigenkapital", value=f"💰{price*eigen/100:,.0f} €")
    with column22:
        tile = column22.container(height=None, border=True)
        tile.metric(label="Money Borrowed", value=f"💸{price*(1 + (grunderwerb+notar+grundbuch+provision)/100)*(1 - eigen/100):,.0f} €")
    with column33:
        tile = column33.container(height=None, border=True)
        tile.metric(label="Remaining Debt", value=f"📉{df_amortization.loc[month-1, 'Remaining Debt'].round():,.0f} €")
    with column44:
        tile = column44.container(height=None, border=True)
        tile.metric(label="Total Interest Payment", value=f"💵{df_amortization['Interest'].sum().round():,.0f} €")
    with column55:
        tile = column55.container(height=None, border=True)
        tile.metric(label="Total Payback", value=f"🔄{df_amortization['Payback'].sum().round():,.0f} €")
    with column66:
        tile = column66.container(height=None, border=True)
        tile.metric(label="Monthly Payment", value=f"🗓️{(df_amortization.loc[1,'Total Payment']).round():,.0f} €")
    with column77:
        tile = column77.container(height=None, border=True)
        tile.metric(label="Deductible interest payment p.a.", value=f"🧾{(df_amortization['Interest'].iloc[:12].sum()):,.0f} €")
    with column88:
        tile = column88.container(height=None, border=True)
        tile.metric(label="Building Amortization p.a.", value=f"🏛️{(gebaude_wert_anteil*price/ 100 * 0.02):,.0f} €")
    with column99:
        tile = column99.container(height=None, border=True)
        tile.metric(label="Renovation costs (in first three years at most 15%)", value=f"🛠️{(gebaude_wert_anteil*price/ 100 * 0.15):,.0f} €")
    with column111:
        tile = column111.container(height=None, border=True)
        tile.metric(label="Cashflow", value=f"💶{(df.iloc[index].area * df.iloc[index].ref_rent_price - df_amortization.loc[1,'Total Payment']):,.0f} €")
    with column222:
        tile = column222.container(height=None, border=True)
        tile.metric(label="Eigenkapital Yield", value=f"📈{(df_amortization.loc[1,'Total Payment'] / (price * eigen / 100) *100):,.1f} %")
    with column333:
        tile = column333.container(height=None, border=True)
        tile.metric(label="Amortization Period", value=f"📅{amortization_in_total / 12:,.1f} years")

    st.dataframe(df_amortization , column_config={
    "Interest" : st.column_config.NumberColumn('Interest',format="%.0f €"),
    "Payback" : st.column_config.NumberColumn('Payback',format="%.0f €"),
    "Total Payment" : st.column_config.NumberColumn('Total Payment',format="%.0f €"),
    "Remaining Debt" : st.column_config.NumberColumn('Remaining Debt',format="%.0f €"),
    "Monthly" : st.column_config.NumberColumn('Monhtly',format="%.0f €")
    },
    hide_index=True,use_container_width=True, height=500)

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=df_amortization['Month'],
    y=df_amortization['Interest'],
    name='Interest'#,
    #marker_color='indianred'
))

# Add Payback bars
fig3.add_trace(go.Bar(
    x=df_amortization['Month'],
    y=df_amortization['Payback'],
    name='Debt Payment'#,
    #marker_color='lightsalmon'
))

# Update layout for better appearance
fig3.update_layout(
    xaxis_title='Month',yaxis_title='Amount (€)',barmode='stack',
    legend=dict(orientation = "h",
    yanchor="bottom", y=-0.3,
    xanchor="left", x=0.01)
)

with column3:
    column3.plotly_chart(fig3, use_container_width=True)


st.subheader("Income Statement")

salary = 100000
try:
    rent_income = round(df.iloc[index].area * df.iloc[index].ref_rent_price * 12)
except ValueError:
    rent_income = 0
interest_cost = df_amortization['Interest'].iloc[:12].sum()
amortization_cost = (gebaude_wert_anteil*price/ 100 * 0.02)

tax = (salary + rent_income - interest_cost - amortization_cost) * (0.43)
earnings_after_tax = (salary + rent_income - interest_cost - amortization_cost) * (1-0.43)

figX = go.Figure(go.Waterfall(
    name="20", orientation="v",
    measure=["relative", "relative", "total", "relative", "relative", "total", "relative", "total"],
    x=["Salary", "Rent income", "Net income", "Interest payment",  \
       "Amortisation", "Profit before tax", "Income Tax", "Profit after tax"],
    textposition="outside",
    text=[f"+{salary:.0f}", f"+{rent_income:.0f}", f"{(salary+rent_income):.0f}",  \
          f"-{interest_cost:.0f}", f"-{amortization_cost:.0f}", "Profit before tax", f"-{tax:.0f}", f"{earnings_after_tax:.0f}"],
    y=[salary, rent_income, 0, interest_cost*-1, amortization_cost*-1, 0 , tax*-1 , 0],
    connector={"line": {"color": "rgb(63, 63, 63)"}},
))

st.plotly_chart(figX)


st.markdown("""
| Tax Type | Description | Deductible |
| ----------- | ----------- |----------- |
| Grunderwerbsteuer | |
| Grundsteuer | |
| Einkommen-/Körperschaftsteuer | |
| Erbschaft- und Schenkungsteuer | |
| Umsatzsteuer | |
| Gewerbesteuer | |
\
""")

st.markdown("""
| Costs | Description | Deductible |
| ----------- | ----------- |----------- |
| Instandhaltungsrücklage  | Die Instandhaltungsrücklage (auch Erhaltungsrücklage) ist der Spartopf, \
            auf den Wohnungs- oder Hauseigentümer zurückgreifen, wenn Reparaturen anfallen. \
            Das Wohnungseigentumsgesetz (WEG) empfiehlt eine Instandhaltungsrücklage anzulegen, gesetzlich vorgeschrieben ist sie aber nicht. \
            Bei einem Verkauf steigert die Instandhaltungsrücklage den Wert des Hauses oder der Eigentumswohnung. \
            ```Höhe der jährlichen Rücklagen = Baukosten pro m² x 1,5 : 80 Jahre x 0,7 x Fläche in m²``` \
            i.e. 164 € / monat | yes \
| Paragraph | Text |
""")

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
