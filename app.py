import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Import your web crawler function
from web_crawler.ipynb import fetch_hotel_data

# Initialize Dash application
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    dcc.Input(id='location-input', type='text', placeholder='Location'),
    dcc.Input(id='checkin-date', type='date', placeholder='Check-in Date'),
    dcc.Input(id='checkout-date', type='date', placeholder='Check-out Date'),
    html.Button('Submit', id='submit-button', n_clicks=0),
    dcc.Graph(id='hotel-data-visualization')
])

# Callback for updating the graph
@app.callback(
    Output('hotel-data-visualization', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('location-input', 'value'),
     State('checkin-date', 'value'),
     State('checkout-date', 'value')]
)
def update_graph(n_clicks, location, check_in, check_out):
    if n_clicks > 0:
        # Fetch and clean data using your web crawler function
        df = your_web_crawler_function(location, check_in, check_out)
        
        # Data cleaning steps here

        # Create a Plotly figure
        fig = px.scatter(df, x='Price', y='Distance', color='Rating')
        return fig
    else:
        # Return an empty figure or some default figure
        return px.scatter()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
