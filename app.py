import dash
from dash import html, dcc, Input, Output, State
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import random
import time
import numpy as np
import plotly.express as px

#STEP 1

def fetch_hotel_data(city, checkin_date, checkout_date):
    checkin_date = datetime.strptime(checkin_date, "%Y-%m-%d").strftime("%Y-%m-%d")
    checkout_date = datetime.strptime(checkout_date, "%Y-%m-%d").strftime("%Y-%m-%d")

    headers = {
        #"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    }

    hotels = []

    page = 0

    while True:
        # Update URL with the current page number
        offset = page * 25
        #location = "Taichung"
        #base_url = 'https://www.booking.com/searchresults.html?ss={}&checkin_year_month_monthday={}&checkout_year_month_monthday={}&rows=25&offset={}'
        base_url = "https://www.booking.com/searchresults.en-gb.html?ss={}&checkin={}&checkout={}&offset={}"
        # Fetch the page content
        url = base_url.format(city, checkin_date, checkout_date, offset)
        #print(offset)
        #print(url)
        response = requests.get(url, headers=headers)
        #print(response.status_code)
        #time.sleep(0.2)
        #print(response.status_code)
        soup = BeautifulSoup(response.content, 'html.parser')
        #time.sleep(0.2)
        information = soup.find('h1', class_='f6431b446c d5f78961c3').get_text(strip=True) if soup.find('h1', class_='f6431b446c d5f78961c3') else "No Information"
        if information == "No Information":
            break
        # else:
        #     print(information)

        # Extract hotel data
        hotel_boxes = soup.find_all("div", class_="c82435a4b8 a178069f51 a6ae3c2b40 a18aeea94d d794b7a0f7 f53e278e95 c6710787a4")  # Update with the correct class name
        #print(hotel_boxes)

        if hotel_boxes == []:
            break  # Break if no hotels are found (end of pages)

            
        for hotel_box in hotel_boxes:
            name = hotel_box.find('div', class_='f6431b446c a15b38c233').get_text(strip=True) if hotel_box.find('div', class_='f6431b446c a15b38c233') else "No Name"
            location = hotel_box.find('span', class_='aee5343fdb def9bc142a').get_text(strip=True) if hotel_box.find('span', class_='aee5343fdb def9bc142a') else "No Location"

            price = hotel_box.find("div", xpath="/html/body/div[5]/div/div[4]/div/div[2]/div[3]/div[2]/div[2]/div[3]/div[38]/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/span/div/div[1]/span[1]").text.get_text(strip=True) if hotel_box.find("div", xpath="/html/body/div[5]/div/div[4]/div/div[2]/div[3]/div[2]/div[2]/div[3]/div[38]/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/span/div/div[1]/span[1]") else "No Price"

            rating = hotel_box.find("div", class_="a3b8729ab1 d86cee9b25").get_text(strip=True) if hotel_box.find("div", class_="a3b8729ab1 d86cee9b25") else "No Rating"
            distance = hotel_box.find("span", {"data-testid": "distance"}).get_text(strip=True) if hotel_box.find("span", {"data-testid": "distance"}) else "No Distance"
            comment = hotel_box.find('div', class_='a3b8729ab1 e6208ee469 cb2cbb3ccb').get_text(strip=True) if hotel_box.find('div', class_='a3b8729ab1 e6208ee469 cb2cbb3ccb') else "No Comment"

            #print(name)
            hotels.append({"Name": name, "Location": location, "Price": price, "Rating": rating, "Distance": distance, "Comment": comment})

        page += 1

    return pd.DataFrame(hotels)

# STEP 2
def process_hotel_data(df):
    # If Price is missing, assign a random number between 200 and 10000
    df['Price'] = df['Price'].replace('No Price', np.nan)
    df['Price'] = df['Price'].fillna(random.randint(200, 10000))
    df['Price'] = df['Price'].astype('Int64')

    # Convert Rating to numeric and coerce errors
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').astype(float)

    # Ensure Comment is of string type
    df['Comment'] = df['Comment'].astype(str)

    # Function to convert Distance to float kilometers
    def convert_distance(dist):
        if pd.isna(dist):
            return np.nan
        if 'km' in dist:
            return float(dist.split(' ')[0])
        if 'm' in dist:
            return float(dist.split(' ')[0]) / 1000
        return np.nan

    # Apply the convert_distance function to the Distance column
    df['Distance'] = df['Distance'].astype(str).apply(convert_distance)

    return df

# Example usage
# df = fetch_hotel_data("Taoyuan", "2023-12-15", "2023-12-18")
# print(df)

#df = fetch_hotel_data(input("city"), input("check-in"), input("check-out"))
#print(df)


# Initialize the Dash application
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Hotel Data Web Crawler"),
    html.Div([
        dcc.Input(id='city-input', type='text', placeholder='Enter city'),


        # Date Picker for Check-in Date
        html.Label('Check-in Date:'),
        dcc.DatePickerSingle(
            id='checkin-date-input',
            min_date_allowed=pd.Timestamp('today').to_pydatetime(),
            max_date_allowed=pd.Timestamp('today').to_pydatetime() + pd.DateOffset(years=5),
            initial_visible_month=pd.Timestamp('today').to_pydatetime(),
            placeholder='Select a date'
        ),
        
        # Date Picker for Check-out Date
        html.Label('Check-out Date:'),
        dcc.DatePickerSingle(
            id='checkout-date-input',
            min_date_allowed=pd.Timestamp('today').to_pydatetime(),
            max_date_allowed=pd.Timestamp('today').to_pydatetime() + pd.DateOffset(years=5),
            initial_visible_month=pd.Timestamp('today').to_pydatetime(),
            placeholder='Select a date'
        ),
        html.Button('Fetch Data', id='fetch-button')
    ]),
    html.Div(id='output-container')
])

# Callback for the fetch button
@app.callback(
    Output('output-container', 'children'),
    Input('fetch-button', 'n_clicks'),
    State('city-input', 'value'),
    State('checkin-date-input', 'date'),
    State('checkout-date-input', 'date'),
)
def update_output(n_clicks, city, checkin_date, checkout_date):
    if n_clicks is None:
        return 'Enter details and click "Fetch Data" to see results.'
    else:
        # Call the web crawler function
        df = fetch_hotel_data(city, checkin_date, checkout_date)
        # Convert the data to a DataFrame and display it
        df = process_hotel_data(df)
        #df = pd.DataFrame(data)
        df_plot = df.dropna(subset=['Price', 'Distance', 'Rating'])

        # Create the scatter plot
        fig = px.scatter(df_plot, x='Price', y='Distance', color='Rating', hover_name="Name" ,hover_data=['Location', 'Comment'],
                 labels={"Price": "Price", "Distance": "Distance (km)", "Rating": "Rating"},
                 title="Hotel Price and Distance Scatter Plot")

        return dcc.Graph(figure=fig)



        # return html.Div([
        #     html.H3('Results:'),
        #     dcc.Graph(
        #         figure=px.bar(df, x='Hotel Name', y='Price')  # Example: create a bar chart
        #     )
        # ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
