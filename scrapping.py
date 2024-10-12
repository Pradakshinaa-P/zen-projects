import time
import pandas as pd
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Function to collect route names and links from the current page
def collect_routes_from_page(driver):
    route_names = []
    route_links = []
    routes = driver.find_elements(By.XPATH, "//a[@class='route']")
    for route in routes:
        route_names.append(route.get_attribute('title'))
        route_links.append(route.get_attribute('href'))
    return route_names, route_links


# Function to extract bus details
def extract_bus_details(driver, route_name, route_link):
    bus_details_list = []
    time.sleep(5)  # Consider replacing this with a wait for specific elements

    bus_items = driver.find_elements(By.XPATH, '//div[contains(@class, "bus-item")]')

    for bus_item in bus_items:
        bus_details = {
            "Bus Name": bus_item.find_element(By.XPATH, './/div[contains(@class, "travels")]').text.strip() or 'N/A',
            "Bus Type": bus_item.find_element(By.XPATH, './/div[contains(@class, "bus-type")]').text.strip() or 'N/A',
            "Start of Journey": bus_item.find_element(By.XPATH,
                                                      './/div[contains(@class, "dp-time")]').text.strip() or 'N/A',
            "End of Journey": bus_item.find_element(By.XPATH,
                                                    './/div[contains(@class, "bp-time")]').text.strip() or 'N/A',
            "Duration": bus_item.find_element(By.XPATH, './/div[contains(@class, "dur")]').text.strip() or 'N/A',
            "Price": bus_item.find_element(By.XPATH,
                                           './/div[contains(@class, "fare")]//span[contains(@class, "f-19 f-bold")]').text.strip() or 'N/A',
            "Star Rating": bus_item.find_element(By.XPATH,
                                                 './/div[contains(@class, "rating")]//span').text.strip() or 'N/A',
            "Seat Availability": bus_item.find_element(By.XPATH,
                                                       './/div[contains(@class, "seat-left")]').text.strip() or 'N/A',
            "Route Name": route_name,
            "Route Link": route_link
        }
        bus_details_list.append(bus_details)

    return bus_details_list


# Initialize the Chrome driver
driver = webdriver.Chrome()

try:
    # Open the desired URL
    driver.get("https://www.redbus.in/online-booking/rsrtc")
    wait = WebDriverWait(driver, 20)

    # Wait for the pagination container element
    pagination_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'DC_117_paginationTable')))

    all_route_names = []
    all_route_links = []

    # Iterate through each page
    for page in range(1, 3):  # Adjust the range based on your requirement
        xpath_expression = f'//div[contains(@class, "DC_117_pageTabs") and contains(text(), "{page}")]'
        page_button = pagination_container.find_element(By.XPATH, xpath_expression)

        actions = ActionChains(driver)
        actions.move_to_element(page_button).perform()
        page_button.click()
        time.sleep(3)  # Wait for the new page to load

        # Collect routes from the current page
        route_names, route_links = collect_routes_from_page(driver)
        all_route_names.extend(route_names)
        all_route_links.extend(route_links)

    # Container for all bus details
    all_bus_details = []

    for route_link, route_name in zip(all_route_links, all_route_names):
        driver.get(route_link)
        driver.maximize_window()
        time.sleep(2)

        # Click all "View Buses" buttons
        try:
            view_buses_buttons = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[@class='button' and contains(text(),'View Buses')]"))
            )
            time.sleep(5)

            for button in reversed(view_buses_buttons):
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(1)
                    button.click()
                    time.sleep(2)
                except Exception as e:
                    print(f"Error clicking button: {e}")
                    continue
        except Exception as e:
            print(f"Error during 'View Buses' button processing: {e}")

        # Scroll to the bottom of the page to ensure all buses are loaded
        scroll_pause_time = 2
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Extract bus details after all content is loaded
        try:
            bus_details = extract_bus_details(driver, route_name, route_link)
            all_bus_details.extend(bus_details)
        except Exception as e:
            print(f"Error extracting bus details for route {route_name}: {e}")

finally:
    # Close the browser
    driver.quit()

# Convert bus details to a DataFrame and remove duplicates
df = pd.DataFrame(all_bus_details)
# Display the DataFrame
print(df.head())

# Database connection details
user = 'root'
password = 'Prad@123'
host = '127.0.0.1'
database = 'red'

# Connect to the MySQL database
conn = mysql.connector.connect(user=user, password=password, host=host, database=database)
cursor = conn.cursor()

# Create the table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS RSRTC_Bus_Details(
    id INT AUTO_INCREMENT PRIMARY KEY,
    Bus_Name VARCHAR(100),
    Bus_Type VARCHAR(100),
    Start_of_Journey VARCHAR(100),
    End_of_Journey VARCHAR(100),
    Duration VARCHAR(100),
    Price FLOAT,
    Star_Rating FLOAT,
    Seat_Availability VARCHAR(100),
    Route_Name VARCHAR(255),
    Route_link VARCHAR(255)
)
"""
cursor.execute(create_table_query)

# Insert data into the table
for index, row in df.iterrows():
    try:
        insert_query = """
            INSERT INTO RSRTC_Bus_Details (
                Bus_Name, Bus_Type, Start_of_Journey, End_of_Journey, Duration, Price, Star_Rating, Seat_Availability, Route_Name, Route_link
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        price = float(row["Price"].replace(",", "")) if row["Price"] not in ['N/A', ''] else None
        star_rating = float(row["Star Rating"]) if row["Star Rating"] not in ['N/A', ''] else None

        cursor.execute(insert_query, (
            row["Bus Name"], row["Bus Type"], row["Start of Journey"], row["End of Journey"], row["Duration"],
            price, star_rating,
            row["Seat Availability"], row["Route Name"], row["Route Link"]
        ))
    except Exception as e:
        print(f"Error inserting row {index}: {e}")

# Commit and close the connection
conn.commit()
cursor.close()
conn.close()