from dash import callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from .data import load_air_quality_data, get_cities

@callback(
    Output('aq-city-dropdown', 'options'),
    Output('aq-city-dropdown', 'value'),
    Input('aq-country-dropdown', 'value')
)
def set_cities_options(selected_country):
    if not selected_country:
        return [], None
    cities = get_cities(selected_country)
    options = [{'label': c, 'value': c} for c in cities]
    value = cities[0] if cities else None
    return options, value

@callback(
    Output('aq-timeseries-plot', 'figure'),
    Output('aq-boxplot', 'figure'),
    Input('aq-city-dropdown', 'value'),
    Input('aq-metric-dropdown', 'value')
)
def update_air_quality_graphs(city, metric):
    if not city or not metric:
        empty_fig = go.Figure(layout={'paper_bgcolor': '#4482C1', 'plot_bgcolor': '#4482C1'})
        return empty_fig, empty_fig

    df = load_air_quality_data()
    city_df = df[df['city'] == city].sort_values(by='date')
    metric_label = f"{metric.replace('_', ' ').title()} (µg/m³)" if 'pm' in metric or 'co' in metric else metric.replace('_', ' ').title()

    # Enhanced Time Series
    city_df['smoothed'] = city_df[metric].rolling(window=30, center=True, min_periods=1).mean()
    city_df['std'] = city_df[metric].rolling(window=30, center=True, min_periods=1).std()
    
    ts_fig = go.Figure()
    ts_fig.add_trace(go.Scatter(x=city_df['date'], y=city_df['smoothed'] + city_df['std'], mode='lines', line=dict(width=0), showlegend=False))
    ts_fig.add_trace(go.Scatter(x=city_df['date'], y=city_df['smoothed'] - city_df['std'], mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(0,114,178,0.2)', name='±1 Std Dev'))
    ts_fig.add_trace(go.Scatter(x=city_df['date'], y=city_df['smoothed'], mode='lines', line=dict(color='#0072B2', width=3), name='30-Day Rolling Mean'))
    
    min_point = city_df.loc[city_df[metric].idxmin()]
    max_point = city_df.loc[city_df[metric].idxmax()]
    ts_fig.add_trace(go.Scatter(x=[min_point['date'], max_point['date']], y=[min_point[metric], max_point[metric]], mode='markers+text', marker=dict(size=8, color='red'), text=['Min', 'Max'], textposition='top center', showlegend=False))
    
    ts_fig.update_layout(title=f'{metric_label} Over Time in {city}', yaxis_title=metric_label)

    # Violin Plot for Distribution
    violin_fig = px.violin(city_df, y=metric, box=True, points="all", title=f'Distribution of {metric_label} in {city}')
    
    for fig in [ts_fig, violin_fig]:
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="#f8f9fa", font_color="black")

    return ts_fig, violin_fig 