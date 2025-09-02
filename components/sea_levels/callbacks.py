from dash.dependencies import Input, Output, State
from dash import callback, html
import plotly.graph_objects as go
import plotly.express as px
import logging
from .data import load_sea_level_data, load_sea_ice_data, calculate_seasonal_cycle, calculate_monthly_trends
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def create_empty_figure(title="No data available"):
    """Create an empty figure with a message."""
    fig = go.Figure()
    fig.add_annotation(
        text=title,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=20)
    )
    fig.update_layout(
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False)
    )
    return fig

@callback(
    [
        Output('sea-level-scatter', 'figure'),
        Output('sea-level-area', 'figure'),
        Output('sea-ice-seasonal', 'figure'),
        Output('sea-ice-trends', 'figure'),
        Output('sea-ice-extent', 'figure')
    ],
    [Input('Sea-Levels', 'children')]
)
def update_sea_level_figures(_):
    """Update all sea level and sea ice figures."""
    try:
        logger.info("Starting to update sea level figures")
        
        # Load data
        df_sea_level = load_sea_level_data()
        df_sea_ice = load_sea_ice_data()
    except Exception as e:
        print(f"Error loading sea level data: {e}")
        return [create_empty_figure(title="Error loading data") for _ in range(5)]

    if df_sea_level.empty or df_sea_ice.empty:
        return [create_empty_figure() for _ in range(5)]
        
    # Create figures
    fig_scatter = px.scatter(df_sea_level, x='Year', y='Sea Level', title='Sea Level Change Over Time')
    fig_area = px.area(df_sea_level, x='Year', y='Sea Level', title='Cumulative Sea Level Change')
    
    seasonal_data = calculate_seasonal_cycle(df_sea_ice)
    
    fig_seasonal = go.Figure()

    # Add standard deviation bands
    fig_seasonal.add_trace(go.Scatter(
        x=seasonal_data['DayOfYear'],
        y=seasonal_data['Mean_Extent'] + seasonal_data['Std_Extent'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        name='Upper Bound'
    ))
    fig_seasonal.add_trace(go.Scatter(
        x=seasonal_data['DayOfYear'],
        y=seasonal_data['Mean_Extent'] - seasonal_data['Std_Extent'],
        mode='lines',
        line=dict(width=0),
        fillcolor='rgba(0, 114, 178, 0.2)',
        fill='tonexty',
        showlegend=False,
        name='Lower Bound'
    ))

    # Add smoothed mean line
    fig_seasonal.add_trace(go.Scatter(
        x=seasonal_data['DayOfYear'],
        y=seasonal_data['Smoothed_Mean_Extent'],
        mode='lines',
        line=dict(color='#0072B2', width=3),
        name='7-Day Rolling Mean'
    ))
    
    # Find and label min/max points
    min_day = seasonal_data.loc[seasonal_data['Mean_Extent'].idxmin()]
    max_day = seasonal_data.loc[seasonal_data['Mean_Extent'].idxmax()]
    
    fig_seasonal.add_trace(go.Scatter(
        x=[min_day['DayOfYear'], max_day['DayOfYear']],
        y=[min_day['Mean_Extent'], max_day['Mean_Extent']],
        mode='markers+text',
        marker=dict(color='red', size=8),
        text=[f"Min: Day {int(min_day['DayOfYear'])}", f"Max: Day {int(max_day['DayOfYear'])}"],
        textposition="top center",
        showlegend=False
    ))

    # Update layout
    fig_seasonal.update_layout(
        title='Average Sea Ice Extent by Day of Year',
        yaxis_title='Sea-ice extent (million km²)',
        xaxis_title='Day of Year',
        hovermode='x unified'
    )
    
    monthly_avg_data, trends_df = calculate_monthly_trends(df_sea_ice)
    
    # Create heatmap for monthly sea ice extent
    pivot_data = monthly_avg_data.pivot(index='Month', columns='Year', values='Extent')
    fig_trends = px.imshow(
        pivot_data,
        labels=dict(x="Year", y="Month", color="Sea Ice Extent (million km²)"),
        title='Monthly Sea Ice Extent Heatmap',
        color_continuous_scale=px.colors.sequential.Plasma
    )
    
    # Enhanced Daily Sea Ice Extent Plot
    # 1. Smoothing and variability
    df_sea_ice['Extent_smoothed'] = df_sea_ice['Extent'].rolling(window=30, center=True, min_periods=1).mean()
    df_sea_ice['Extent_std'] = df_sea_ice['Extent'].rolling(window=30, center=True, min_periods=1).std()

    # 2. Trend Line Calculation
    trend_data = df_sea_ice.dropna(subset=['Extent'])
    # Convert Date to fractional years for regression
    years = trend_data['Date'].dt.year + (trend_data['Date'].dt.dayofyear - 1) / 365.25
    z = np.polyfit(years, trend_data['Extent'], 1)
    p = np.poly1d(z)
    df_sea_ice['trend'] = p(df_sea_ice['Date'].dt.year + (df_sea_ice['Date'].dt.dayofyear - 1) / 365.25)
    slope_per_decade = z[0] * 10

    # 3. Annual Min/Max
    annual_mins = df_sea_ice.loc[df_sea_ice.groupby(df_sea_ice['Date'].dt.year)['Extent'].idxmin()]
    annual_maxs = df_sea_ice.loc[df_sea_ice.groupby(df_sea_ice['Date'].dt.year)['Extent'].idxmax()]

    # 4. Create the plot with graph_objects
    fig_extent = go.Figure()

    # Add shaded variability band
    fig_extent.add_trace(go.Scatter(
        x=df_sea_ice['Date'], y=df_sea_ice['Extent_smoothed'] + df_sea_ice['Extent_std'],
        mode='lines', line=dict(width=0), showlegend=False, name='Upper Bound'
    ))
    fig_extent.add_trace(go.Scatter(
        x=df_sea_ice['Date'], y=df_sea_ice['Extent_smoothed'] - df_sea_ice['Extent_std'],
        mode='lines', line=dict(width=0), fillcolor='rgba(0, 114, 178, 0.2)', fill='tonexty',
        showlegend=True, name='±1 Std. Dev.'
    ))
    # Add smoothed line
    fig_extent.add_trace(go.Scatter(
        x=df_sea_ice['Date'], y=df_sea_ice['Extent_smoothed'],
        mode='lines', line=dict(color='#0072B2', width=2), name='30-Day Rolling Mean'
    ))
    # Add trend line
    fig_extent.add_trace(go.Scatter(
        x=df_sea_ice['Date'], y=df_sea_ice['trend'],
        mode='lines', line=dict(color='red', dash='dash', width=2), name='Long-term Trend'
    ))
    # Add annual min/max markers
    fig_extent.add_trace(go.Scatter(
        x=annual_mins['Date'], y=annual_mins['Extent'], mode='markers',
        marker=dict(color='blue', size=5, symbol='diamond'), name='Annual Minimum'
    ))
    fig_extent.add_trace(go.Scatter(
        x=annual_maxs['Date'], y=annual_maxs['Extent'], mode='markers',
        marker=dict(color='red', size=5, symbol='circle'), name='Annual Maximum'
    ))

    # 5. Update layout and add annotation
    fig_extent.update_layout(
        title='Trends in Sea Ice Extent Over Years',
        yaxis_title='Sea Ice Extent (million km²)',
        xaxis_title='Year', hovermode='x unified', legend=dict(x=0.01, y=0.99)
    )
    # Fix negative zero for trend annotation
    trend_val = slope_per_decade
    if np.isclose(trend_val, 0, atol=1e-2):
        trend_val = 0.00
    fig_extent.add_annotation(
        x=0.99, y=0.99, xref='paper', yref='paper',
        text=f'Trend: {trend_val:.2f} million km²/decade',
        showarrow=False, font=dict(size=12, color="red"), align="right"
    )

    return fig_scatter, fig_area, fig_seasonal, fig_trends, fig_extent
