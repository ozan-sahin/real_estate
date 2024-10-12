import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st
#from streamlit_folium import folium_static
#import folium
#from sqlalchemy import create_engine
import datetime, json
plt.style.use('fivethirtyeight')

st.set_page_config(page_title="Real Estate Analytics", page_icon=":house:", layout="wide")
st.markdown("""---""")

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
