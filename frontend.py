import streamlit as st
from streamlit_lottie import st_lottie
import requests

# Set the page configuration
st.set_page_config(
    page_title="Homepage",
    page_icon="🏠",
)

# Load Lottie animation from a URL

st.markdown(
    """
    <h1 style='text-align: center; color: black;'>
        Welcome to the Homepage of 
        <span style='color: black;'>Red Bus Data insights</span> 
    """,
    unsafe_allow_html=True
)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_hello = load_lottieurl("https://lottie.host/844cdd43-d748-41ac-9731-ceb187a1bc61/iKZ6tDvtGd.json")


st_lottie(
    lottie_hello,
    speed=1,
    reverse=False,
    loop=True,
    quality="low"
)

st.markdown(
    """
    <h5 style='color: black;'>
    The Red Bus data insights is built to Ease the process of finding the Right Bus.Searching Buses on the website is 
    time consuming . So here is the app built to find buses in few seconds.
""",unsafe_allow_html=True)
st.write("""The RED BUS DATA INSIGHTS is built using the following technologies:\n
Selenium\n
Python\n
Streamlit\n
Pandas\n
SQL
""")
st.markdown("<span style='color:black;'>The developing process has three stages</span>", unsafe_allow_html=True)
st.write("""Data set gathering using selenium ->
Loading them into the SQL Database->
Deploy them in a app using streamlit with Dynamic Filters.
""")
st.markdown("<span style='color:red;'>Domain:</span> <span style='color:cyan;'>Transportation</span>", unsafe_allow_html=True)
st.markdown("<span style='color: red;'>Skills take away From This Project:</span> <span style='color: cyan;'>Web Scraping using Selenium, Python, Streamlit, SQL</span>", unsafe_allow_html=True)


