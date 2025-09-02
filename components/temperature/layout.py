from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from .data import (
    load_geojson, load_temperatures_by_country, load_major_city_temps,
    load_temps_by_city, load_continent_map, load_global_temps_by_country,
    load_global_temps_by_country_v2, load_avg_dataset
)

# Load all data
india_states = load_geojson("dataset/states_india.geojson")
us_states = load_geojson("dataset/us-states.json")
can_states = load_geojson("dataset/canada.geojson")
china_states = load_geojson("dataset/China_geo.json")
rus_states = load_geojson("dataset/Russia_geo.json")
brz_states = load_geojson("dataset/brazil_geo.json")

df1 = load_temperatures_by_country("dataset/India_temperatures.csv")
df2 = load_temperatures_by_country("dataset/China_temperatures.csv")
df3 = load_temperatures_by_country("dataset/Canada_temperatures.csv")
df4 = load_temperatures_by_country("dataset/Brazil_temperatures.csv")
df5 = load_temperatures_by_country("dataset/Russia_temperatures.csv")
df6 = load_temperatures_by_country("dataset/US_temperatures.csv")

data_heatmap = load_major_city_temps()
countries = load_temps_by_city()
continent_map = load_continent_map()
df_choro_data = load_global_temps_by_country()
global_temp_country_data = load_global_temps_by_country_v2()
data_timeline_data = load_avg_dataset()

# Process geo data
state_id_map1, state_id_map2, state_id_map3, state_id_map4, state_id_map5, state_id_map6 = {}, {}, {}, {}, {}, {}

for feature in brz_states["features"]:
    feature["id"] = feature["id"]
    state_id_map1[feature["properties"]["name"]] = feature["id"]
for feature in rus_states["features"]:
    feature["id"] = feature["properties"]["ID_1"]
    state_id_map2[feature["properties"]["NAME_1"]] = feature["id"]
for feature in india_states["features"]:
    feature["id"] = feature["properties"]["state_code"]
    state_id_map3[feature["properties"]["st_nm"]] = feature["id"]
for feature in china_states["features"]:
    feature["id"] = feature["properties"]["HASC_1"]
    state_id_map4[feature["properties"]["NAME_1"]] = feature["id"]
for feature in can_states["features"]:
    feature["id"] = feature["properties"]["cartodb_id"]
    state_id_map5[feature["properties"]["name"]] = feature["id"]
for feature in us_states["features"]:
    feature["id"] = feature["id"]
    state_id_map6[feature["properties"]["name"]] = feature["id"]

df1["id"] = df1["State"].apply(lambda x: state_id_map3.get(x))
df2["id"] = df2["State"].apply(lambda x: state_id_map4.get(x))
df3["id"] = df3["State"].apply(lambda x: state_id_map5.get(x))
df4["id"] = df4["State"].apply(lambda x: state_id_map1.get(x))
df5["id"] = df5["State"].apply(lambda x: state_id_map2.get(x))
df6["id"] = df6["State"].apply(lambda x: state_id_map6.get(x))

# Create figures
fig11 = px.choropleth_mapbox(df1, locations="id", geojson=india_states, 
    color="AverageTemperature", 
    color_continuous_scale='Turbo', 
    hover_name="State", 
    hover_data=["AverageTemperature"], 
    title="Average Temperature INDIA", 
    mapbox_style="carto-positron", 
    center={"lat": 20.5937, "lon": 78.9629}, 
    zoom=3.5,
    opacity=0.7,
    height=700
)

fig21 = px.choropleth_mapbox(df2, locations="id", geojson=china_states, 
    color="AverageTemperature", 
    color_continuous_scale='Turbo', 
    hover_name="State", 
    hover_data=["AverageTemperature"], 
    title="Average Temperature CHINA", 
    mapbox_style="carto-positron", 
    center={"lat": 35.8617, "lon": 104.1954}, 
    zoom=2.8,
    opacity=0.7,
    height=700
)

fig31 = px.choropleth_mapbox(df3, locations="id", geojson=can_states, 
    color="AverageTemperature", 
    color_continuous_scale='Turbo', 
    hover_name="State", 
    hover_data=["AverageTemperature"], 
    title="Average Temperature CANADA", 
    mapbox_style="carto-positron", 
    center={"lat": 56.1304, "lon": -106.3468}, 
    zoom=2.5,
    opacity=0.7,
    height=700
)

fig41 = px.choropleth_mapbox(df4, locations="id", geojson=brz_states, 
    color="AverageTemperature", 
    color_continuous_scale='Turbo', 
    hover_name="State", 
    hover_data=["AverageTemperature"], 
    title="Average Temperature BRAZIL", 
    mapbox_style="carto-positron", 
    center={"lat": -14.2350, "lon": -51.9253}, 
    zoom=2.8,
    opacity=0.7,
    height=700
)

fig51 = px.choropleth_mapbox(df5, locations="id", geojson=rus_states, 
    color="AverageTemperature", 
    color_continuous_scale='Turbo', 
    hover_name="State", 
    hover_data=["AverageTemperature"], 
    title="Average Temperature RUSSIA", 
    mapbox_style="carto-positron", 
    center={"lat": 61.5240, "lon": 105.3188}, 
    zoom=2.2,
    opacity=0.7,
    height=700
)

fig61 = px.choropleth_mapbox(df6, locations="id", geojson=us_states, 
    color="AverageTemperature", 
    color_continuous_scale='Turbo', 
    hover_name="State", 
    hover_data=["AverageTemperature"], 
    title="Average Temperature USA", 
    mapbox_style="carto-positron", 
    center={"lat": 37.0902, "lon": -95.7129}, 
    zoom=3,
    opacity=0.7,
    height=700
)

# Update dimensions and styling for all country maps
for fig in [fig11, fig21, fig31, fig41, fig51, fig61]:
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_x=0.5,
        title_y=0.95,
        title_font_size=20,
        mapbox=dict(
            style="carto-positron",
            zoom=fig.layout.mapbox.zoom,  # Keep individual zoom levels
            center=fig.layout.mapbox.center  # Keep individual centers
        ),
        coloraxis_colorbar=dict(
            title=dict(
                text="Temperature (°C)",
                side="right"
            ),
            ticks="outside",
            ticklen=5
        )
    )

fig_heat = px.density_map(data_heatmap.sort_values('dt'), lat='Latitude_Float', lon='Longitude_Float', z='AverageTemperature', hover_data=["City"], radius=8, zoom=1, map_style="carto-positron", animation_frame='dt', opacity=0.5, title='Average Temperature Heatmap by Cities')

df_choro = df_choro_data.dropna()
df_choro['date'] = pd.to_datetime(df_choro['dt'])
df_choro['Year'] = df_choro['date'].dt.year
df_choro = df_choro.groupby(['Country', 'Year'])['AverageTemperature'].mean().reset_index()
fig_choro = px.choropleth(df_choro.sort_values('Year'), locations='Country', locationmode='country names', color='AverageTemperature', color_continuous_scale='Turbo', animation_frame='Year', title='Choropleth Map - Average Temperatures by Country')

# Update the choropleth map dimensions and styling
fig_choro.update_layout(
    height=600,
    margin=dict(l=20, r=20, t=40, b=20),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    title_x=0.5,
    title_y=0.95,
    title_font_size=20,
    geo=dict(
        showframe=True,
        showcoastlines=True,
        projection_type='equirectangular',
        showland=True,
        showcountries=True,
        landcolor='rgb(243, 243, 243)',
        countrycolor='rgb(204, 204, 204)'
    )
)

# Update the heatmap dimensions and styling
fig_heat.update_layout(
    height=600,
    margin=dict(l=20, r=20, t=40, b=20),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    title_x=0.5,
    title_y=0.95,
    title_font_size=20
)

fig_timeline = px.line(data_timeline_data, x='Year', y='Average_Land_Temperature (celsius)', title='Earth Temperature Timeline')

# Fix SettingWithCopyWarning by creating a copy and using loc
global_temp_country_clear = global_temp_country_data.copy()
mask = ~global_temp_country_clear['Country'].isin(['Denmark', 'Antarctica', 'France', 'Europe', 'Netherlands', 'United Kingdom', 'Africa', 'South America'])
global_temp_country_clear = global_temp_country_clear[mask].copy()
global_temp_country_clear.loc[:, 'Country'] = global_temp_country_clear['Country'].replace({
    'Denmark (Europe)': 'Denmark',
    'France (Europe)': 'France',
    'Netherlands (Europe)': 'Netherlands',
    'United Kingdom (Europe)': 'United Kingdom'
})

countries_unique = np.unique(global_temp_country_clear['Country'])
mean_temp = [global_temp_country_clear[global_temp_country_clear['Country'] == country]['AverageTemperature'].mean() for country in countries_unique]
data_globe = [dict(type='choropleth', locations=countries_unique, z=mean_temp, locationmode='country names', text=countries_unique, marker=dict(line=dict(color='rgb(0,0,0)', width=1)), colorbar=dict(autotick=True, tickprefix='', title='# Average\nTemperature,\n°C'))]
layout_globe = dict(title='Average land temperature in countries', geo=dict(showframe=False, showocean=True, oceancolor='rgb(0,255,255)', projection=dict(type='orthographic', rotation=dict(lon=60, lat=10)), lonaxis=dict(showgrid=False, gridcolor='rgb(102, 102, 102)'), lataxis=dict(showgrid=True, gridcolor='rgb(102, 102, 102)')))

# Update the globe dimensions and styling
layout_globe.update(
    height=600,
    margin=dict(l=20, r=20, t=40, b=20),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    title_x=0.5,
    title_y=0.95,
    title_font_size=20,
    geo=dict(
        showframe=True,
        showcoastlines=True,
        projection=dict(
            type='orthographic',
            rotation=dict(lon=60, lat=10)
        ),
        showland=True,
        showcountries=True,
        landcolor='rgb(243, 243, 243)',
        countrycolor='rgb(204, 204, 204)',
        oceancolor='rgb(230, 250, 255)'
    )
)
fig_globe = dict(data=data_globe, layout=layout_globe)

# Fix SettingWithCopyWarning for df DataFrame
df = load_major_city_temps()
df = pd.merge(left=df, right=continent_map[['Country', 'Region']], on='Country', how='left')
mask = (df['Year'] > 1994) & (df['Year'] < 2020) & (df['AverageTemperature'] > -70)
df = df[mask].copy()
fig_lines = px.line(df.groupby(['Region', 'Year'])['AverageTemperature'].mean().reset_index(), x='Year', y='AverageTemperature', color='Region', title='Average temperatures of Continents over the years 1994 to 2019', hover_data={'Year': False, 'AverageTemperature': ':.2f'}, labels={'AverageTemperature': 'Avg Temp'})

# Update line plot
fig_lines.update_layout(
    height=450,
    margin=dict(l=20, r=20, t=40, b=20),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgb(245, 245, 245)',
    title_x=0.5,
    title_y=0.95,
    title_font_size=20,
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgb(228, 228, 228)'),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgb(228, 228, 228)')
)

# Remove the temperature difference bar chart and related data

fig_choro = px.choropleth(
    df_choro.sort_values('Year'),
    locations='Country',
    locationmode='country names',
    color='AverageTemperature',
    color_continuous_scale='Turbo',
    animation_frame='Year',
    title='Choropleth Map - Average Temperatures by Country'
)

# Update the choropleth map dimensions and styling
fig_choro.update_layout(
    height=600,
    margin=dict(l=20, r=20, t=40, b=20),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    title_x=0.5,
    title_y=0.95,
    title_font_size=20,
    geo=dict(
        showframe=True,
        showcoastlines=True,
        projection_type='equirectangular',
        showland=True,
        showcountries=True,
        landcolor='rgb(243, 243, 243)',
        countrycolor='rgb(204, 204, 204)'
    )
)

def create_temperature_layout():
    # Get unique countries and years for dropdowns
    df = load_temps_by_city()
    df['dt'] = pd.to_datetime(df['dt'])
    df['Year'] = df['dt'].dt.year
    countries = sorted(df['Country'].unique())
    years = sorted(df['Year'].unique())
    
    return html.Div(
        children=[
            html.H1('Temperature Visualization', style={'textAlign': 'center', 'color': 'white', 'marginBottom': '30px', 'fontSize': '2.5em', 'fontWeight': 'bold'}),
            
            # Global Temperature Overview Section
            html.Div([
                html.H3('Global Temperature Overview', style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50', 'fontSize': '1.8em'}),
                dcc.Graph(
                    id="Choro",
                    figure=fig_choro,
                    style={'margin': 'auto'}
                ),
            ], style={'margin': '20px', 'padding': '25px', 'backgroundColor': 'white', 'borderRadius': '15px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),

            # Temperature Timeline Section
            html.Div([
                html.H3('Temperature Timeline', style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50', 'fontSize': '1.8em'}),
                dcc.Graph(
                    id="timeline",
                    figure=fig_timeline,
                    style={'margin': 'auto'}
                ),
            ], style={'margin': '20px', 'padding': '25px', 'backgroundColor': 'white', 'borderRadius': '15px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),
            
            # Global Temperature Distribution Section
            html.Div([
                html.H3('Global Temperature Distribution', style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50', 'fontSize': '1.8em'}),
                dcc.Graph(
                    id="Globe",
                    figure=fig_globe,
                    style={'margin': 'auto'}
                ),
            ], style={'margin': '20px', 'padding': '25px', 'backgroundColor': 'white', 'borderRadius': '15px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),
            
            # Country-wise Temperature Analysis Section
            html.Div([
                html.H3('Country-wise Temperature Analysis', style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50', 'fontSize': '1.8em'}),
                html.Div([
                    dcc.Dropdown(
                        id='choro-dropdown',
                        options=[
                            {'label': 'INDIA', 'value': 'fig11'},
                            {'label': 'CHINA', 'value': 'fig21'},
                            {'label': 'CANADA', 'value': 'fig31'},
                            {'label': 'BRAZIL', 'value': 'fig41'},
                            {'label': 'RUSSIA', 'value': 'fig51'},
                            {'label': 'USA', 'value': 'fig61'}
                        ],
                        value='fig11',
                        style={
                            'width': '50%',
                            'margin': '20px auto',
                            'display': 'block',
                            'fontSize': '16px'
                        }
                    ),
                    dcc.Graph(
                        id="choropleth-map11",
                        style={'margin': 'auto'}
                    ),
                ], style={'width': '100%'}),
            ], style={'margin': '20px', 'padding': '25px', 'backgroundColor': 'white', 'borderRadius': '15px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),
            
            # Continental Temperature Trends Section
            html.Div([
                html.H3('Continental Temperature Trends', style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50', 'fontSize': '1.8em'}),
                dcc.Graph(
                    id="lines",
                    figure=fig_lines,
                    style={'margin': 'auto'}
                ),
            ], style={'margin': '20px', 'padding': '25px', 'backgroundColor': 'white', 'borderRadius': '15px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),
            
        ],
        style={
            'background-color': '#660000',
            'padding': '30px',
            'maxWidth': '100%',
            'margin': 'auto',
            'minHeight': '100vh'
        }
    )
