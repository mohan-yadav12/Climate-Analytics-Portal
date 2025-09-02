from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from .data import load_sea_level_data, load_sea_ice_data, calculate_seasonal_cycle, calculate_monthly_trends

def create_sea_levels_layout():
    """Create the layout for sea levels component."""
    return html.Div([
        html.Div(
            children=[
                html.H1(
                    children='Sea Level & Ice Analysis',
                    style={'font-size': '36px', 'color': 'white'}
                ),
                html.P(
                    children='This dashboard visualizes Global Sea Level rise and Sea Ice Extent data.',
                    style={'font-size': '20px', 'color': 'white', 'margin-top': '0px'}
                )
            ],
            style={
                'text-align': 'center',
                'padding-top': '50px',
                "display": 'block',
                "font-family": "PT Sans Narrow"
            }
        ),
        
        html.Div(
            children=[
                # Sea Level Section
                html.Div([
                    html.H2(
                        'Sea Level Analysis',
                        style={
                            'textAlign': 'center',
                            'color': '#2c3e50',
                            'marginBottom': '20px',
                            'fontSize': '1.8em'
                        }
                    ),
                    # Scatter plot for sea level
                    dcc.Loading(
                        id="loading-sea-level-scatter",
                        type="default",
                        children=dcc.Graph(
                            id='sea-level-scatter',
                            style={
                                'margin': 'auto',
                                'marginBottom': '20px',
                                'border': '3px solid #2A547E'
                            }
                        )
                    ),
                    # Area chart for sea level
                    dcc.Loading(
                        id="loading-sea-level-area",
                        type="default",
                        children=dcc.Graph(
                            id='sea-level-area',
                            style={
                                'margin': 'auto',
                                'marginBottom': '20px',
                                'border': '3px solid #2A547E'
                            }
                        )
                    ),
                ], style={
                    'margin': '20px',
                    'padding': '25px',
                    'backgroundColor': 'white',
                    'borderRadius': '15px',
                    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
                }),
                
                # Sea Ice Section
                html.Div([
                    html.H2(
                        'Sea Ice Analysis',
                        style={
                            'textAlign': 'center',
                            'color': '#2c3e50',
                            'marginBottom': '20px',
                            'fontSize': '1.8em'
                        }
                    ),
                    # Seasonal Cycle Plot
                    dcc.Loading(
                        id="loading-seasonal",
                        type="default",
                        children=dcc.Graph(
                            id='sea-ice-seasonal',
                            style={
                                'margin': 'auto',
                                'marginBottom': '20px',
                                'border': '3px solid #2A547E'
                            }
                        )
                    ),
                    # Monthly Trends Plot
                    dcc.Loading(
                        id="loading-trends",
                        type="default",
                        children=dcc.Graph(
                            id='sea-ice-trends',
                            style={
                                'margin': 'auto',
                                'marginBottom': '20px',
                                'border': '3px solid #2A547E'
                            }
                        )
                    ),
                    # Sea Ice Extent Plot
                    dcc.Loading(
                        id="loading-extent",
                        type="default",
                        children=dcc.Graph(
                            id='sea-ice-extent',
                            style={
                                'margin': 'auto',
                                'marginBottom': '20px',
                                'border': '3px solid #2A547E'
                            }
                        )
                    ),
                ], style={
                    'margin': '20px',
                    'padding': '25px',
                    'backgroundColor': 'white',
                    'borderRadius': '15px',
                    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
                })
            ],
            style={'margin': '10px', 'display': 'block'},
            id='Sea-Levels'
        )
    ],
    style={
        'background-color': '#000066',
        'padding': '30px',
        'minHeight': '100vh'
    })
