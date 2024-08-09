# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

options = [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]
options.insert(0, {'label': 'All Sites', 'value': 'ALL'})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(id='site-dropdown',
                 options=options,
                 value='ALL',
                 placeholder='Select a Launch Site here',
                 searchable=True),
    html.Br(),
    
    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                    value=[min_payload, max_payload]),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Aggregate total success and failure counts for all sites
        success_counts = spacex_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        success_counts['class'] = success_counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            success_counts,
            names='class',
            values='count',
            title='Total Success and Failure Launches for All Sites'
        )
    else:
        # Filter dataframe for the selected site and generate success/failure counts
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        success_counts['class'] = success_counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            success_counts,
            names='class',
            values='count',
            title=f'Total Success and Failure Launches for site {entered_site}'
        )
    return fig

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class', 
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites'
        )
    else:
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_filtered_df, x='Payload Mass (kg)', y='class', 
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {entered_site}'
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
