from dash import dcc, html
import plotly.express as px
import pandas as pd
import numpy as np

from .data import get_countries, get_metrics, load_air_quality_data
# Import the new data function
from .data import get_deaths_by_age_data
# Import the new data function
from .data import get_deaths_by_risk_factor_data
from .data import get_death_rate_by_pollution_type
import plotly.graph_objects as go

# ------------------------------------------------------------------
# Build choropleth of composite air quality (considering all pollutants)
# ------------------------------------------------------------------

aq_df = load_air_quality_data()
# Guard against empty
if not aq_df.empty:
    # Get all pollutants
    pollutants = ['pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
    
    # Calculate mean for each pollutant by country
    country_means = {}
    for pollutant in pollutants:
        means = aq_df.groupby('country')[pollutant].mean()
        # Normalize each pollutant (0-1 scale)
        if not means.empty:
            min_val = means.min()
            max_val = means.max()
            if max_val > min_val:  # Avoid division by zero
                means = (means - min_val) / (max_val - min_val)
            country_means[pollutant] = means
    
    # Create composite score (average of normalized pollutants)
    composite_scores = pd.DataFrame()
    for pollutant in pollutants:
        if pollutant in country_means:
            if composite_scores.empty:
                composite_scores = country_means[pollutant].to_frame('score')
            else:
                composite_scores['score'] += country_means[pollutant]
    
    if not composite_scores.empty:
        composite_scores['score'] /= len(pollutants)
        composite_scores = composite_scores.reset_index()
        
        fig_aq_map = px.choropleth(
            composite_scores,
            locations='country',
            locationmode='country names',
            color='score',
            color_continuous_scale='Blues',  # Now darker = worse air quality
            range_color=(0, 1),
            labels={'score': 'Air Quality Score<br>(Higher = Worse)'},
            title='Composite Air Quality by Country<br>(Considering PM2.5, PM10, SO2, NO2, CO, O3)'
        )
        fig_aq_map.update_layout(
            geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'),
            margin=dict(l=0, r=0, t=50, b=0)
        )
else:
    fig_aq_map = px.choropleth(title='Air quality data not available')


def create_layout():
    countries = get_countries()
    metrics = get_metrics()

    # --- Horizontal bar plot: Deaths by risk factor (World, 2021) ---
    risk_df = get_deaths_by_risk_factor_data()
    risk_df = risk_df.sort_values('Deaths', ascending=True)
    bar_fig = go.Figure(go.Bar(
        x=risk_df['Deaths'],
        y=risk_df['Risk Factor'],
        orientation='h',
        marker_color='#627fa3',
        text=[f"{d/1_000_000:.2f} million" if d >= 1_000_000 else f"{int(d):,}" for d in risk_df['Deaths']],
        textposition='outside',
        insidetextanchor='end',
    ))
    bar_fig.update_layout(
        title='Deaths by risk factor, World, 2021',
        xaxis_title='Annual deaths',
        yaxis_title='',
        paper_bgcolor='white',
        plot_bgcolor='#f8f9fa',
        font_color='black',
        margin=dict(l=40, r=40, t=60, b=40),
        height=800,
        xaxis=dict(tickformat=",d", gridcolor='#e5e5e5'),
    )

    # --- Multi-line plot: Death rate from air pollution by type (country/region, 1990 & 2021) ---
    dr_df = get_death_rate_by_pollution_type()
    line_fig = go.Figure()
    line_colors = {
        'Air pollution (total)': '#a6761d',  # brown
        'Indoor air pollution': '#d95f02',   # red
        'Outdoor particulate matter': '#1b9e77',  # green
        'Outdoor ozone pollution': '#386cb0',  # blue
    }
    # Default to 'World' if present, else first country
    default_country = 'World' if 'World' in dr_df['Country or region'].unique() else dr_df['Country or region'].unique()[0]
    selected_country = default_country
    dr_country = dr_df[dr_df['Country or region'] == selected_country]
    for col in ['Air pollution (total)', 'Indoor air pollution', 'Outdoor particulate matter', 'Outdoor ozone pollution']:
        line_fig.add_trace(go.Scatter(
            x=dr_country['Year'],
            y=dr_country[col],
            mode='lines+markers',
            name=col,
            line=dict(color=line_colors[col], width=3, shape='spline'),
            marker=dict(size=8),
        ))
    line_fig.update_layout(
        title=f'Death rate from air pollution, {selected_country}',
        yaxis_title='Deaths per 100,000 population',
        xaxis_title='Year',
        legend_title='',
        paper_bgcolor='white',
        plot_bgcolor='#f8f9fa',
        font_color='black',
        margin=dict(l=40, r=40, t=60, b=40),
        height=500,
        yaxis=dict(gridcolor='#e5e5e5'),
        xaxis=dict(dtick=1, gridcolor='#e5e5e5', tickmode='array', tickvals=[1990, 2021]),
    )

    return html.Div([
        html.H1("Global Air Quality Analysis", style={'textAlign': 'center', 'color': 'white'}),

        # Choropleth Map section
        html.Div([
            dcc.Graph(id='aq-global-map', figure=fig_aq_map, style={'height': '600px'})
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '15px', 'margin': '20px'}),

        # Controls
        html.Div([
            dcc.Dropdown(
                id='aq-country-dropdown',
                options=[{'label': c, 'value': c} for c in countries],
                value=countries[0] if countries else None,
                placeholder="Select a country",
                style={'width': '200px', 'marginRight': '10px'}
            ),
            dcc.Dropdown(
                id='aq-city-dropdown',
                placeholder="Select a city",
                style={'width': '200px', 'marginRight': '10px'}
            ),
            dcc.Dropdown(
                id='aq-metric-dropdown',
                options=[{'label': m.replace('_', ' ').title(), 'value': m} for m in metrics],
                value=metrics[0],
                clearable=False,
                style={'width': '200px', 'marginRight': '10px'}
            ),
        ], style={'display': 'flex', 'justifyContent': 'center', 'padding': '20px'}),

        # Visualizations
        html.Div([
            dcc.Graph(id='aq-timeseries-plot'),
            dcc.Graph(id='aq-boxplot'),
        ], style={'padding': '20px'}),

        # Bar plot section: Deaths by risk factor (moved to bottom)
        html.Div([
            dcc.Graph(id='aq-deaths-by-risk-bar', figure=bar_fig)
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '15px', 'margin': '20px'}),

    ], style={'backgroundColor': '#363636', 'padding': '30px', 'minHeight': '100vh'}) 