from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd

from .data import (
    available_gases,
    get_all_countries,
    latest_year,
    load_clean_data,
    get_continent_emissions,
)


def create_layout():
    gases = available_gases()
    countries = get_all_countries()
    df = load_clean_data()

    min_year, max_year = int(df['year'].min()), int(df['year'].max())

    # --- Continent GHG emissions stacked bar chart for latest year ---
    # Determine latest common year across all selected gases
    df_years = load_clean_data()
    common_years = set(df_years['year'].unique())
    for g in gases:
        common_years &= set(df_years[df_years['gas'] == g]['year'].unique())
    if common_years:
        latest_yr = max(common_years)
    else:
        latest_yr = latest_year()  # Fallback if no common year
    gases = ['CO2', 'CH4', 'N2O', 'HFC', 'PFC', 'SF6']  # All available GHGs
    
    # Get emissions data for each gas and continent
    continent_data = []
    for gas in gases:
        cont_df = get_continent_emissions(gas, latest_yr)
        if not cont_df.empty:
            cont_df['gas'] = gas
            continent_data.append(cont_df)
    
    # Combine all gas data
    all_cont_df = pd.concat(continent_data, ignore_index=True)
    
    # Sort continents by total emissions
    continent_totals = all_cont_df.groupby('continent')['value'].sum().sort_values(ascending=True)
    continents_ordered = continent_totals.index.tolist()
    
    # Create stacked bar chart
    fig_continent_total = go.Figure()
    
    # Color scheme for different gases (matching the reference style)
    colors = {
        'CO2': '#CB4154',  
        'CH4': '#FF69B4',  # Pink for methane (like oil in reference)
        'N2O': '#4B0082',  # Deep purple for N2O (like gas in reference)
        'HFC': '#20B2AA',  # Light sea green (like nuclear in reference)
        'PFC': '#4169E1',  # Royal blue (like hydropower in reference)
        'SF6': '#228B22',  # Forest green (like renewables in reference)
    }
    
    # Add bars for each gas
    for gas in gases:
        gas_data = all_cont_df[all_cont_df['gas'] == gas]
        if not gas_data.empty:
            # Ensure data is in the correct continent order
            gas_data = gas_data.set_index('continent').reindex(continents_ordered).reset_index()
            
            # Format text to show both value and gas type
            text = [f"{x:,.0f}" if x > 1000 else "" for x in gas_data['value']]
            
            fig_continent_total.add_trace(
                go.Bar(
                    name=gas,
                    y=gas_data['continent'],
                    x=gas_data['value'],
                    orientation='h',
                    marker_color=colors[gas],
                    text=text,
                    textposition='inside',
                    insidetextanchor='middle',
                    textfont=dict(color='white', size=12),
                )
            )

    # Add total values at the end of each bar
    for continent in continents_ordered:
        total = all_cont_df[all_cont_df['continent'] == continent]['value'].sum()
        fig_continent_total.add_annotation(
            x=total,
            y=continent,
            text=f"{total:,.0f}",
            showarrow=False,
            xanchor='left',
            xshift=10,
            font=dict(size=12)
        )

    fig_continent_total.update_layout(
        title=dict(
            text=f'Continental Greenhouse Gas Emissions by Type',
            font=dict(size=24, color='black')
        ),
        plot_bgcolor='white',
        barmode='stack',
        xaxis=dict(
            title=dict(text='Emissions (Gigagrams CO₂e)', font=dict(size=14)),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            showline=True,
            linewidth=1,
            linecolor='black',
            zeroline=False,
        ),
        yaxis=dict(
            title='',
            showgrid=False,
            categoryorder='array',
            categoryarray=continents_ordered,
            showline=True,
            linewidth=1,
            linecolor='black',
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='white',
            bordercolor='black',
            borderwidth=1,
            title=''
        ),
        margin=dict(l=20, r=20, t=80, b=20),
        font=dict(color='black'),
        showlegend=True,
    )

    return html.Div([
        html.H1('Global Greenhouse Gas Emissions', style={'textAlign': 'center', 'color': 'white'}),
        dcc.Graph(
            id='ghg-continent-total',
            figure=fig_continent_total,
            style={"margin-bottom": "20px", "margin-top": "20px", 'border': '3px solid #2A547E'}
        ),

        html.Div([
            html.Label('Select Gas:', style={'color': 'white', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='ghg-gas-dropdown',
                options=[{'label': g, 'value': g} for g in gases],
                value=gases[0],
                clearable=False,
                style={'width': '300px'}
            )
        ], style={'marginBottom': '20px', 'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}),

        # --- Racing Bar Chart Section ---
        html.H1(id='racing-bar-title', children='Top 10 Emitting Countries - Growth', style={'font-size': '20px', 'color': 'white', 'padding-left': '10px'}),
        dcc.Graph(id='ghg-racing-bar', style={"margin-bottom": "10px", 'border': '3px solid #2A547E'}),
        dcc.Interval(id='ghg-interval-component', interval=600, n_intervals=0),
        html.Div(
            children=[
                dcc.Graph(id='ghg-top-5-bar', style={"margin-bottom": "10px", 'border': '3px solid #2A547E'}),
                dcc.Graph(id='ghg-bottom-5-bar', style={"margin-bottom": "10px", 'border': '3px solid #2A547E'}),
            ],
            style={"display": "flex", "flex-direction": "row", "justify-content": "space-between", "width": "100%"}
        ),

        # --- Pie Chart with Year Slider Section ---
        html.Div([
            html.H3("Continent Emissions", style={'textAlign': 'center', 'color': 'black'}),
            dcc.Graph(id='ghg-continent-pie-chart', style={"margin-bottom": "10px", 'border': '3px solid #2A547E'}),
            dcc.Slider(
                id='ghg-year-slider-pie',
                min=min_year,
                max=max_year,
                value=max_year,
                marks={str(year): str(year) for year in range(min_year, max_year + 1, 5)},
                step=1,
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='mouseup',
                included=True,
            ),
        ], style={'background': 'white', 'padding': '20px', 'border-radius': '10px', 'margin': '30px auto', 'width': '90%', 'box-shadow': '0 2px 8px rgba(0,0,0,0.08)'}),

        # --- Scatter Plot Section ---
        html.Div([
            html.Label("Select countries to display for scatter plot:", style={'color': 'white'}),
            dcc.Dropdown(
                id="ghg-country-dropdown",
                options=[{"label": country, "value": country} for country in countries],
                value=countries[:2] if countries else [],
                multi=True,
                style={'width': '700px'}
            ),
            dcc.Graph(id="ghg-scatterplot", style={"margin-bottom": "10px", 'border': '3px solid #2A547E', 'width': '100%'}),
        ], style={'marginBottom': '20px', 'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'width': '95%', 'margin': 'auto'}),
    ], style={'backgroundColor': '#3B2F70', 'padding': '30px', 'minHeight': '100vh'}) 