from dash import dcc, html
import plotly.graph_objects as go
import plotly.express as px

# Import temperature and sea level data loaders
from components.temperature.data import load_avg_dataset
from components.sea_levels.data import load_sea_level_data
from .data import load_correlation_data
import pandas as pd

def create_correlation_layout():
    data_temp = load_correlation_data()
    years = data_temp['Year']
    temp = data_temp['Average_Land_Temperature (celsius)']
    temp1 = data_temp['Average_LandOcean_Temperature (celsius)']
    emissions = data_temp['Average_Emissions (MtCO₂e)']
    sea = data_temp['Average_Sealevel (mm)']

    fig_corr_merged = go.Figure()
    fig_corr_merged.add_trace(go.Scatter(x=years, y=temp, mode='lines+markers', name='Land Temperature', line=dict(color='red', width=2), marker=dict(color='red', size=8)))
    fig_corr_merged.add_trace(go.Scatter(x=years, y=temp1, mode='lines+markers', name='Land and Ocean Temperature', line=dict(color='orange', width=2), marker=dict(color='orange', size=8)))
    fig_corr_merged.add_trace(go.Scatter(x=years, y=emissions, mode='lines+markers', name='Carbon Emissions', line=dict(color='blue', width=2), marker=dict(color='blue', size=8), yaxis='y2'))
    fig_corr_merged.add_trace(go.Scatter(x=years, y=sea, mode='lines+markers', name='Sea level', line=dict(color='green', width=2), marker=dict(color='green', size=8), yaxis='y3'))

    fig_corr_merged.update_layout(
        font=dict(family='Arial', size=12, color='black'),
        title=dict(text='Correlation between Temperatures, Carbon Emissions and Sea level (1990-2020)', xanchor='center', yanchor='top', x=0.5, y=0.95),
        xaxis=dict(title='Year', tickmode='linear', tick0=1990, dtick=5),
        yaxis=dict(title='Temperature (°C above pre-industrial levels)', range=[8, 18], color='red', title_font=dict(size=16)),
        yaxis2=dict(title='Carbon Emissions (metric tons per capita)', range=[22500, 37000], overlaying='y', side='right', color='blue', title_font=dict(size=16)),
        yaxis3=dict(title='Sea level(mm)', range=[-25, 69], overlaying='y', side='right', position=.94, color='green', title_font=dict(size=16)),
        legend=dict(orientation='h', yanchor='bottom', y=-0.2),
    )


    data_temp_subset = data_temp[['Year', 'Average_Land_Temperature (celsius)', 'Average_Emissions (MtCO₂e)', 'Average_Sealevel (mm)']]
    # Remove the fig_corr2 definition and usage

    data_emissions = data_temp
    # --- Emissions + Temperature Grouped Bar Chart ---

    # --- Global Tree Cover Loss vs Global GHG Emissions (2001-2020) ---
    # Load tree cover loss by region dataset and aggregate globally
    tree_df = pd.read_csv('dataset/TreeCoverLoss_2001-2020_ByRegion.csv')
    tree_world = tree_df.groupby('Year', as_index=False)['TreeCoverLoss_ha'].sum()
    tree_world['TreeCoverLoss_Mha'] = tree_world['TreeCoverLoss_ha'] / 1_000_000  # convert to million hectares

    # Load global GHG emissions (MtCO2e) and convert to GtCO2e
    ghg_df = pd.read_csv('dataset/ALL GHG_historical_emissions.csv')
    world_row = ghg_df[(ghg_df['Country'] == 'World') & (ghg_df['Sector'] == 'Total including LUCF') & (ghg_df['Gas'] == 'All GHG')]
    if not world_row.empty:
        # Melt year columns into rows
        ghg_melt = world_row.melt(id_vars=['Country', 'Data source', 'Sector', 'Gas', 'Unit'], var_name='Year', value_name='Emissions_Mt')
        ghg_melt['Year'] = pd.to_numeric(ghg_melt['Year'], errors='coerce')
        ghg_melt = ghg_melt.dropna(subset=['Year'])
        ghg_melt = ghg_melt[ghg_melt['Year'].between(2001, 2020)]
        ghg_melt['Emissions_Gt'] = ghg_melt['Emissions_Mt'] / 1000.0
    else:
        ghg_melt = pd.DataFrame(columns=['Year', 'Emissions_Gt'])

    # Merge years present in both datasets for consistency
    common_years = sorted(set(tree_world['Year']).intersection(set(ghg_melt['Year'])))
    tree_filtered = tree_world[tree_world['Year'].isin(common_years)]
    ghg_filtered = ghg_melt[ghg_melt['Year'].isin(common_years)]

    fig_defor_em = go.Figure()
    fig_defor_em.add_trace(go.Bar(
        x=tree_filtered['Year'],
        y=tree_filtered['TreeCoverLoss_Mha'],
        name='Tree Cover Loss (Million ha)',
        marker_color='forestgreen',
        opacity=0.7,
        yaxis='y'
    ))
    fig_defor_em.add_trace(go.Scatter(
        x=ghg_filtered['Year'],
        y=ghg_filtered['Emissions_Gt'],
        name='Global GHG Emissions (Gt CO₂e)',
        mode='lines+markers',
        line=dict(color='crimson', width=3),
        marker=dict(color='crimson', size=8),
        yaxis='y2'
    ))
    fig_defor_em.update_layout(
        title='Global Tree Cover Loss vs GHG Emissions (2001-2020)',
        font_family='Arial',
        xaxis=dict(title='Year', tickmode='linear'),
        yaxis=dict(title=dict(text='Tree Cover Loss (Million ha)', font=dict(color='forestgreen')), tickfont=dict(color='forestgreen')),
        yaxis2=dict(title=dict(text='GHG Emissions (Gt CO₂e)', font=dict(color='crimson')), overlaying='y', side='right', tickfont=dict(color='crimson')),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25),
        barmode='group',
        plot_bgcolor='white'
    )

    # ------------------------------------------------------------------
    # NEW: Sea Level vs Global Temperature Time-Series (Extended Period)
    # ------------------------------------------------------------------

    # Load datasets
    df_temp = load_avg_dataset()
    df_sea = load_sea_level_data()

    # Prepare temperature: use Land & Ocean average if available, else land
    temp_col = 'Average_LandOcean_Temperature (celsius)' if 'Average_LandOcean_Temperature (celsius)' in df_temp.columns else 'Average_Land_Temperature (celsius)'
    temp_df = df_temp[['Year', temp_col]].rename(columns={temp_col: 'Temp_C'})

    # Ensure numeric and drop NaNs
    temp_df['Year'] = pd.to_numeric(temp_df['Year'], errors='coerce')
    temp_df = temp_df.dropna()

    sea_df = df_sea[['Year', 'Sea Level']].rename(columns={'Sea Level': 'Sea_Level_mm'})

    # Merge on common years
    merged_ts = pd.merge(temp_df, sea_df, on='Year', how='inner').sort_values('Year')

    # Apply rolling average smoothing (5-year window)
    window_size = 5
    merged_ts['Sea_Level_Smooth'] = merged_ts['Sea_Level_mm'].rolling(window=window_size, center=True).mean()
    merged_ts['Temp_Smooth'] = merged_ts['Temp_C'].rolling(window=window_size, center=True).mean()
    
    # Fill NaN values at edges with original data
    merged_ts['Sea_Level_Smooth'] = merged_ts['Sea_Level_Smooth'].fillna(merged_ts['Sea_Level_mm'])
    merged_ts['Temp_Smooth'] = merged_ts['Temp_Smooth'].fillna(merged_ts['Temp_C'])

    fig_temp_sea = go.Figure()
    fig_temp_sea.add_trace(go.Scatter(
        x=merged_ts['Year'], y=merged_ts['Sea_Level_Smooth'], name='Sea Level (mm)',
        mode='lines', line=dict(color='royalblue', width=2), yaxis='y'
    ))
    fig_temp_sea.add_trace(go.Scatter(
        x=merged_ts['Year'], y=merged_ts['Temp_Smooth'], name='Global Avg Temperature (°C)',
        mode='lines', line=dict(color='firebrick', width=2), yaxis='y2'
    ))
    fig_temp_sea.update_layout(
        title='Global Temperature vs Sea Level Over Time',
        xaxis=dict(title='Year', tickmode='linear', dtick=10),
        yaxis=dict(
            title=dict(
                text='Sea Level (mm relative to 1993-2008 avg)',
                font=dict(color='royalblue')
            ),
            tickfont=dict(color='royalblue')
        ),
        yaxis2=dict(
            title=dict(
                text='Temperature (°C)',
                font=dict(color='firebrick')
            ),
            overlaying='y',
            side='right',
            tickfont=dict(color='firebrick')
        ),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25),
        plot_bgcolor='white',
        font_family='Arial'
    )

    return html.Div(
        children=[
            html.Div(
                children=[
                    html.H1(children='Correlation between Average Land & Ocean Temperature, Carbon Emissions and Sea level (1990-2020)',
                            style={'font-size': '36px', 'color': 'white'}),
                    html.P(children='This dashboard visualizes Average Land temperature, Average Carbon Emission and Average Sea Level in a single plot',
                           style={'font-size': '20px', 'color': 'white', 'margin-top': '0px'})
                ],
                style={'text-align': 'center', 'padding-top': '50px', "display": 'block', "font-family": "PT Sans Narrow"}
            ),
            html.Div(
                children=[
                    dcc.Graph(id='sea_temp_timeseries', figure=fig_temp_sea, style={"margin-bottom": "10px", 'border': '3px solid #2A547E'}),
                    dcc.Graph(id='corr_line_merged', figure=fig_corr_merged, style={"margin-bottom": "10px", 'border': '3px solid #2A547E'}),
                    dcc.Graph(id='deforestation_vs_emissions', figure=fig_defor_em, style={"margin-bottom": "10px", 'border': '3px solid #2A547E'}),
                ],
                style={'margin': '10px', 'display': 'block', 'flex-wrap': 'wrap'}
            )
        ],
        style={'background-color': '#006666'}
    )
