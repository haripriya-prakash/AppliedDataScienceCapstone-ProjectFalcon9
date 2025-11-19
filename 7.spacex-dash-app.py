# Import required libraries
import pandas as pd
import dash
# FIX: Import html and dcc directly from dash
from dash import html 
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv', 
                        encoding = "ISO-8859-1",
                        dtype={'Div1Airport': str, 'Div1TailNum': str, 
                               'Div2Airport': str, 'Div2TailNum': str})

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                         style={'textAlign': 'center', 'color': '#503D36',
                                                'font-size': 40}),
                                
                                # TASK 1: Dropdown
                                dcc.Dropdown(id='site-dropdown',
                                    options=[
                                            {'label': 'All Sites', 'value': 'ALL'},
                                            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                            ],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                   ),
                                html.Br(),

                                # TASK 2: Pie Chart
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Range Slider
                                dcc.RangeSlider(id='payload-slider',
                                     min=0, max=10000, step=1000,
                                     marks={0: '0', 1000: '1000', 2000: '2000', 3000: '3000', 4000: '4000', 5000: '5000', 6000: '6000', 
                                     7000: '7000', 8000: '8000', 9000: '9000', 10000: '10000'}, 
                                     value=[min_payload, max_payload]),

                                # TASK 4: Scatter Chart
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# --- CALLBACKS ---

# TASK 2: Pie Chart Callback (Corrected Logic)
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
              
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Calculate total successful launches per site
        filtered_df = spacex_df[spacex_df['class'] == 1]
        site_success_counts = filtered_df.groupby('Launch Site')['class'].count().reset_index()
        site_success_counts.rename(columns={'class': 'Success Count'}, inplace=True)
        
        fig = px.pie(site_success_counts,
        values='Success Count',
        names='Launch Site', 
        title='Total Successful Launches By Site')
        return fig
    else:
        # Show success vs. failure counts for a specific site
        specific_site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = specific_site_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        
        fig = px.pie (outcome_counts,
        values='count',
        names='class',
        title='Launch Outcome Success/Failure for: ' + entered_site)
        return fig

# TASK 4: Scatter Chart Callback
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
             Input(component_id='site-dropdown', component_property='value'),
             Input(component_id="payload-slider", component_property="value"))

def get_scatter_slider_chart(entered_site, payload_slider):
    lowPayload, highPayload = payload_slider
    # Filter by payload range (inclusive)
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= lowPayload) & 
                            (spacex_df['Payload Mass (kg)'] <= highPayload)]
                            
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, 
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation Between Payload and Mission Outcomes For All Sites (Payload Range)')
        return fig
    else:
        # Filter the payload-ranged data for the specific site
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        fig = px.scatter(site_filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation Between Payload And Mission Outcomes for: ' + entered_site + ' (Payload Range)')
        return fig

# Run the app
# Run the app
if __name__ == '__main__':
    app.run(debug=True)
