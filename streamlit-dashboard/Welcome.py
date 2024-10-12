import pandas as pd
import streamlit as st
import datetime, json

st.set_page_config(page_title="Real Estate Analytics", page_icon=":house:", layout="wide")

st.title(":house: Welcome to Real Estate Analytics")

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
