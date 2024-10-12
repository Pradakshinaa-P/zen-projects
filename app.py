import streamlit as st
import pandas as pd
import pymysql
import re  # Import regular expressions module for pattern matching
import requests  # Import requests for Lottie animation loading
from streamlit_lottie import st_lottie

heading_text = "<span style='color:#FF0000'>Redbus Ticket Booking</span>"
st.markdown(f"<h1>{heading_text}</h1>", unsafe_allow_html=True)

# Function to load Lottie animation from URL
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load Lottie animation
lottie_url = "https://lottie.host/dfd3552c-4284-476b-81df-b91e3a51f8b3/OPTemFxjcj.json"
lottie_hello = load_lottieurl(lottie_url)

st_lottie(
    lottie_hello,
    speed=1,
    reverse=False,
    loop=True,
    quality="low"
)

# Database credentials
user = 'root'
password = 'Prad@123'
host = '127.0.0.1'
database = 'red'

# Connect to MySQL database
conn = pymysql.connect(
    user=user,
    password=password,
    host=host,
    database=database
)

# Function to clean Seat_Availability column
def clean_seat_availability(value):
    # Extract numeric part from string, assuming format like '1 Seat available'
    match = re.search(r'\d+', value)
    if match:
        return int(match.group())
    else:
        return 0  # Default to 0 if no numeric value found

# Select RTC
st.sidebar.success("Select a page from above")
rtc_options = [
    'APSRTC_Bus_Details',
    'ASTC_Bus_Details',
    'BSRTC_Bus_Details',
    'HRTC_Bus_Details',
    'KSRTC_Bus_Details',
    'KTCL_Bus_Details',
    'PEPSU_Bus_Details',
    'SBSTC_Bus_Details',
    'RSRTC_Details',
    'UPSRTC_Bus_Details'
]
selected_rtc = st.selectbox('Select RTC:', rtc_options)
# Construct SQL query based on selected RTC
query = f"SELECT * FROM {selected_rtc}"

# Execute SQL query and fetch data into a DataFrame
try:
    df = pd.read_sql(query, conn)
except Exception as e:
    st.error(f"Error fetching data: {str(e)}")
    df = pd.DataFrame()  # Empty DataFrame in case of error

# Display RTC data table
st.subheader(f'Table for {selected_rtc}')
st.write(df)

# Filter options
selected_routes = st.multiselect('Select Bus Route(s):', df['Route_Name'].unique() if not df.empty else [])
selected_bus_types = st.multiselect('Select Bus Type(s):', df['Bus_Type'].unique() if not df.empty else [])

# Calculate min and max price range from the data
min_price = int(df['Price'].min()) if not df.empty else 0
max_price = int(df['Price'].max()) if not df.empty else 1000
price_range = st.slider('Price Range:', min_value=min_price, max_value=max_price, value=(min_price, max_price))

star_rating = st.slider('Star Rating:', min_value=1.0, max_value=5.0, step=0.1, value=(1.0, 5.0))
seats_available = st.slider('Seats Available:', min_value=0, max_value=100, value=(0, 100))

# Apply filters and fetch data based on user selections
filters = []

if selected_routes:
    route_conditions = " OR ".join([f"Route_Name = '{route}'" for route in selected_routes])
    filters.append(f"({route_conditions})")

if selected_bus_types:
    type_conditions = " OR ".join([f"Bus_Type = '{bus_type}'" for bus_type in selected_bus_types])
    filters.append(f"({type_conditions})")

filters.append(f"Price BETWEEN {price_range[0]} AND {price_range[1]}")
filters.append(f"Star_Rating BETWEEN {star_rating[0]} AND {star_rating[1]}")
filters.append(f"Seat_Availability BETWEEN {seats_available[0]} AND {seats_available[1]}")

# Construct SQL query with filters
if filters:
    filter_query = " AND ".join(filters)
    filtered_query = f"{query} WHERE {filter_query}"
else:
    filtered_query = query

# Execute filtered SQL query and fetch data into a DataFrame
try:
    filtered_df = pd.read_sql(filtered_query, conn)
    st.subheader('Filtered Results')
    st.write(filtered_df)
except Exception as e:
    st.error(f"Error fetching filtered data: {str(e)}")

# Close the database connection
conn.close()