import dash
from dash import html, dcc, Input, Output, State
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import numpy as np
import plotly.express as px

# STEP 1

def fetch_hotel_data(city, checkin_date, checkout_date):
    checkin_date = datetime.strptime(checkin_date, "%Y-%m-%d").strftime("%Y-%m-%d")
    checkout_date = datetime.strptime(checkout_date, "%Y-%m-%d").strftime("%Y-%m-%d")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    }

    hotels = []

    # Loop through first 4 pages
    for page in range(4):
        offset = page * 25
        base_url = "https://www.booking.com/searchresults.en-gb.html?ss={}&checkin={}&checkout={}&offset={}"
        url = base_url.format(city, checkin_date, checkout_date, offset)
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        information = soup.find('h1', class_='f6431b446c d5f78961c3').get_text(strip=True) if soup.find('h1', class_='f6431b446c d5f78961c3') else "No Information"
        if information == "No Information":
            break

        hotel_boxes = soup.find_all("div", class_="c82435a4b8 a178069f51 a6ae3c2b40 a18aeea94d d794b7a0f7 f53e278e95 c6710787a4")
        
        if not hotel_boxes:
            break

        for hotel_box in hotel_boxes:
            name = hotel_box.find('div', class_='f6431b446c a15b38c233').get_text(strip=True) if hotel_box.find('div', class_='f6431b446c a15b38c233') else "No Name"
            location = hotel_box.find('span', class_='aee5343fdb def9bc142a').get_text(strip=True) if hotel_box.find('span', class_='aee5343fdb def9bc142a') else "No Location"
            price = hotel_box.find('span', class_="f6431b446c fbfd7c1165 e84eb96b1f").get_text(strip=True) if hotel_box.find('span', class_="f6431b446c fbfd7c1165 e84eb96b1f") else "No Price"
            rating = hotel_box.find("div", class_="a3b8729ab1 d86cee9b25").get_text(strip=True) if hotel_box.find("div", class_="a3b8729ab1 d86cee9b25") else "No Rating"
            distance = hotel_box.find("span", {"data-testid": "distance"}).get_text(strip=True) if hotel_box.find("span", {"data-testid": "distance"}) else "No Distance"
            comment = hotel_box.find('div', class_='a3b8729ab1 e6208ee469 cb2cbb3ccb').get_text(strip=True) if hotel_box.find('div', class_='a3b8729ab1 e6208ee469 cb2cbb3ccb') else "No Comment"

            hotels.append({"Name": name, "Location": location, "Price": price, "Rating": rating, "Distance": distance, "Comment": comment})

    return pd.DataFrame(hotels)

# STEP 2
def process_hotel_data(df):
    df['Price'] = df['Price'].astype(str)
    df['Price'] = df['Price'].str.replace(',', '').str.replace('TWD\xa0', '')
    df['Price'] = df['Price'].replace('No Price', np.nan)
    df['Price'] = df['Price'].astype('Int64')
    df['Price'].fillna(0, inplace=True)

    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').astype(float)
    df['Comment'] = df['Comment'].astype(str)

    def convert_distance(dist):
        if pd.isna(dist):
            return np.nan
        if 'km' in dist:
            return float(dist.split(' ')[0])
        if 'm' in dist:
            return float(dist.split(' ')[0]) / 1000
        return np.nan

    df['Distance'] = df['Distance'].astype(str).apply(convert_distance)

    return df

# Initialize the Dash application
app = dash.Dash(__name__)

# Custom CSS styles for a better appearance
app.layout = html.Div([
    html.H1("Hotel Data Web Crawler", style={'textAlign': 'center', 'color': '#007BFF'}),
    html.Div([
        dcc.Input(id='city-input', type='text', placeholder='Enter city', style={'margin': '10px', 'padding': '10px', 'width': '200px'}),
        html.Label('Check-in Date:', style={'margin': '10px'}),
        dcc.DatePickerSingle(
            id='checkin-date-input',
            min_date_allowed=pd.Timestamp('today').to_pydatetime(),
            max_date_allowed=pd.Timestamp('today').to_pydatetime() + pd.DateOffset(years=5),
            initial_visible_month=pd.Timestamp('today').to_pydatetime(),
            placeholder='Select a date',
            style={'margin': '10px'}
        ),
        html.Label('Check-out Date:', style={'margin': '10px'}),
        dcc.DatePickerSingle(
            id='checkout-date-input',
            min_date_allowed=pd.Timestamp('today').to_pydatetime(),
            max_date_allowed=pd.Timestamp('today').to_pydatetime() + pd.DateOffset(years=5),
            initial_visible_month=pd.Timestamp('today').to_pydatetime(),
            placeholder='Select a date',
            style={'margin': '10px'}
        ),
        html.Button('Fetch Data', id='fetch-button', style={'margin': '10px', 'padding': '10px', 'background-color': '#28A745', 'color': 'white', 'border': 'none', 'cursor': 'pointer'}),
    ], style={'textAlign': 'center'}),
    html.Div(id='output-container', style={'margin': '20px'})
], style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'})

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
        return html.Div('Enter details and click "Fetch Data" to see results.', style={'textAlign': 'center', 'color': '#DC3545'})
    else:
        df = fetch_hotel_data(city, checkin_date, checkout_date)
        df = process_hotel_data(df)
        df_plot = df.dropna(subset=['Price', 'Distance', 'Rating'])
        fig = px.scatter(df_plot, x='Price', y='Distance', color='Rating', hover_name="Name", hover_data=['Location', 'Comment'],
                         labels={"Price": "Price", "Distance": "Distance (km)", "Rating": "Rating"},
                         title="Hotel Price and Distance Scatter Plot")
        return dcc.Graph(figure=fig)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)