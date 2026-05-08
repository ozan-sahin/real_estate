import pandas as pd
import streamlit as st
import math
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.subheader("Finance")

column1, column2, column3 = st.columns([2,6,3])

with column1:
    grunderwerb = st.number_input('Grunderwerbssteuer [%]', value=6.5)
    notar = st.number_input('Notarkosten [%]', value=1.5)
    grundbuch = st.number_input('Grundbucheintrag [%]', value=0.5)
    provision = st.number_input('Maklerprovision [%]', value=3.57)
    price = st.number_input('Real Estate Price', value=170000)
    eigen = st.number_input('Eigenkapital [%]', value=20.0)

    zinsen = st.number_input('Zinssatz [%/year]', value=3.94)
    tilgung = st.number_input('Tilgungssatz [%/year]', value=3.0)
    years = st.number_input('Years', value=5, key=int)

    st.subheader("Tax")
    gebaude_wert_anteil = st.number_input('Gebäudewertanteil [%]', value=85)

    st.subheader("Rent Income Parameters")
    price_per_m2 = st.number_input('Price [€/m2]', value=14.5)
    rent_income_ = st.number_input('Monthly Rent Income', value=price_per_m2*65)

# Total cost including additional fees
total_cost = price * (1 + (grunderwerb + notar + grundbuch + provision) / 100)
loan_amount = total_cost * (1 - eigen / 100)
#loan_amount = 152000
annual_interest = loan_amount * zinsen / 100
annuitat =  loan_amount * (zinsen + tilgung) / 100 / 12

# Amortization schedule over 10 years
remaining_debt = loan_amount
amortization_schedule = []

for month in range(1, (years)*12 ):

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
try:
    amortization_in_total = math.log(annuitat / (annuitat - loan_amount * zinsen / 100 / 12)) / math.log(1 + zinsen / 100 / 12)
except ZeroDivisionError:
    amortization_in_total = float('inf')  # or any other value that makes sense in your context

with column2:

    column11, column22, column33 = st.columns(3)
    column44, column55, column66 = st.columns(3)
    column77, column88, column99 = st.columns(3)

    column111, column222, column333 = st.columns(3)
    column444, column555, column666 = st.columns(3)

    with column11:
        tile = column11.container(height="content", border=True)
        tile.metric(label="Eigenkapital", value=f"💰{total_cost*eigen/100:,.0f} €")
    with column22:
        tile = column22.container(height="content", border=True)
        tile.metric(label="Money Borrowed", value=f"💸{price*(1 + (grunderwerb+notar+grundbuch+provision)/100)*(1 - eigen/100):,.0f} €")
        #tile.metric(label="Money Borrowed", value=f"💸{152000:,.0f} €")
    with column33:
        tile = column33.container(height="content", border=True)
        tile.metric(label="Remaining Debt", value=f"📉{df_amortization.loc[month-1, 'Remaining Debt'].round():,.0f} €")
    with column44:
        tile = column44.container(height="content", border=True)
        tile.metric(label="Total Interest Payment", value=f"💵{df_amortization['Interest'].sum().round():,.0f} €")
    with column55:
        tile = column55.container(height="content", border=True)
        tile.metric(label="Total Payback", value=f"🔄{df_amortization['Payback'].sum().round():,.0f} €")
    with column66:
        tile = column66.container(height="content", border=True)
        tile.metric(label="Monthly Payment", value=f"🗓️{(df_amortization.loc[1,'Total Payment']).round():,.0f} €")
    with column77:
        tile = column77.container(height="content", border=True)
        tile.metric(label="Deductible interest payment p.a.", value=f"🧾{(df_amortization['Interest'].iloc[:12].sum()):,.0f} €")
    with column88:
        tile = column88.container(height="content", border=True)
        tile.metric(label="Building Amortization p.a.", value=f"🏛️{(gebaude_wert_anteil*price/ 100 * 0.025):,.0f} €")
    with column99:
        tile = column99.container(height="content", border=True)
        tile.metric(label="Renovation costs (in first three years at most 15%)", value=f"🛠️{(gebaude_wert_anteil*price/ 100 * 0.15):,.0f} €")
    with column111:
        tile = column111.container(height="content", border=True)
        tile.metric(label="Cashflow", value=f"💶{(65 * price_per_m2 - df_amortization.loc[1,'Total Payment']):,.0f} €")
    with column222:
        tile = column222.container(height="content", border=True)
        #tile.metric(label="Eigenkapital Yield", value=f"📈{(df_amortization.loc[1,'Total Payment'] / (price * eigen / 100) *100):,.1f} %")
        tile.metric(label="Return of Investment", value=f"📈{(total_cost / rent_income_ / 12):,.1f} years")
    with column333:
        tile = column333.container(height="content", border=True)
        tile.metric(label="Amortization Period", value=f"📅{amortization_in_total / 12:,.1f} years")
    with column444:
        tile = column444.container(height="content", border=True)
        tile.metric(label="Total Cost", value=f"📉{total_cost:,.0f} €")
    with column555:
        tile = column555.container(height="content", border=True)
        tile.metric(label="Nebenkosten perc", value=f"📈{((grunderwerb + notar + grundbuch + provision))} %")
    with column666:
        tile = column666.container(height="content", border=True)
        tile.metric(label="Makler Cost", value=f"📈{price*provision/100:,.0f} €")

    st.dataframe(df_amortization , column_config={
    "Interest" : st.column_config.NumberColumn('Interest',format="%.0f €"),
    "Payback" : st.column_config.NumberColumn('Payback',format="%.0f €"),
    "Total Payment" : st.column_config.NumberColumn('Total Payment',format="%.0f €"),
    "Remaining Debt" : st.column_config.NumberColumn('Remaining Debt',format="%.0f €"),
    "Monthly" : st.column_config.NumberColumn('Monhtly',format="%.0f €")
    },
    hide_index=True,width="content", height=500)

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
    column3.plotly_chart(fig3, width="content")


# st.subheader("Income Statement")

# salary = 100000
# try:
#     rent_income = round(65*price_per_m2 * 12)
# except ValueError:
#     rent_income = 0
# interest_cost = df_amortization['Interest'].iloc[:12].sum()
# amortization_cost = (gebaude_wert_anteil*price/ 100 * 0.025)
# laufende_kosten = 0

# tax = (salary + rent_income - interest_cost - amortization_cost) * (0.43)
# earnings_after_tax = (salary + rent_income - interest_cost - amortization_cost) * (1-0.43)

# figX = go.Figure(go.Waterfall(
#     name="20", orientation="v",
#     measure=["relative", "relative", "total", "relative", "relative", "total", "relative", "total"],
#     x=["Salary", "Rent income", "Net income", "Interest payment",  \
#        "Amortisation", "Profit before tax", "Income Tax", "Profit after tax"],
#     textposition="outside",
#     text=[f"+{salary:.0f}", f"+{rent_income:.0f}", f"{(salary+rent_income):.0f}",  \
#           f"-{interest_cost:.0f}", f"-{amortization_cost:.0f}", "Profit before tax", f"-{tax:.0f}", f"{earnings_after_tax:.0f}"],
#     y=[salary, rent_income, 0, interest_cost*-1, amortization_cost*-1, 0 , tax*-1 , 0],
#     connector={"line": {"color": "rgb(63, 63, 63)"}},
# ))

# st.plotly_chart(figX)

#-------
st.subheader("Income statement with bank loan")

rent_income = round(65 * price_per_m2 * 12)
interest_cost = df_amortization['Interest'].iloc[:12].sum()
amortization_cost = (gebaude_wert_anteil*price/ 100 * 0.025)
laufende_kosten = 1000
tax = ( rent_income - interest_cost - amortization_cost) * (0.42)
earnings_after_tax2 = (rent_income - interest_cost - amortization_cost) * (1-0.42)

figX = go.Figure(go.Waterfall(
    name="20", orientation="v",
    measure=["relative", "relative", "relative", "relative", "total", "relative", "total", "relative", "total" , "relative", "total"],
    x=[ "Rent income",  "Interest payment",  "Amortisation", "Laufende Kosten", "Taxable Income", \
       "Income Tax", "Profit after tax", "Without Amortisation", "Income", "7%/pa Return of S&P 500 investment", "Final Income"],
    textposition="outside",
    text=[f"+{rent_income:.0f}", f"-{interest_cost:.0f}", f"-{amortization_cost:.0f}",  f"-{laufende_kosten:.0f}", \
          f"{(rent_income-interest_cost-amortization_cost-laufende_kosten):.0f}",f"-{tax:.0f}", f"{earnings_after_tax2:.0f}", \
          f"+{amortization_cost:.0f}", f"{(earnings_after_tax2+amortization_cost):.0f} €", f"{(total_cost - total_cost*eigen/100) *0.07:.0f} €"],
    y=[rent_income, interest_cost*-1, amortization_cost*-1, laufende_kosten*-1, 0 , tax*-1 , earnings_after_tax2, amortization_cost,0,
       (total_cost - total_cost*eigen/100) *0.07, 0],
    connector={"line": {"color": "rgb(63, 63, 63)"}},
))

st.plotly_chart(figX)

#-------
st.subheader("Income statement with cash")

rent_income = round(65 * price_per_m2 * 12)
tax = ( rent_income ) * (0.42)
earnings_after_tax3 = (rent_income) * (1-0.42)

figX = go.Figure(go.Waterfall(
    name="20", orientation="v",
    measure=["relative", "relative", "total"],
    x=[ "Rent income", "Income Tax", "Final Income"],
    textposition="outside",
    text=[f"+{rent_income:.0f}",f"-{tax:.0f}", f"{earnings_after_tax3:.0f}"],
    y=[rent_income, tax*-1 , earnings_after_tax3 ],
    connector={"line": {"color": "rgb(63, 63, 63)"}},
))

st.plotly_chart(figX)

#-------

st.metric(label="Benefit of getting a mortgage", value=f"📈{(earnings_after_tax2 + amortization_cost + (total_cost - total_cost*eigen/100) *0.07 - earnings_after_tax3):,.1f} €")

st.markdown("""
| Tax Type | Description | Deductible |
| ----------- | ----------- |----------- |
| Grunderwerbsteuer | |
| Grundsteuer | Immobilienwert x Grundsteuermesszahl [0,034%] x Hebesatz [440%] = 258 €/Jahr. | Yes
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

