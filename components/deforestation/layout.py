from dash import dcc, html
import plotly.graph_objects as go
import plotly.express as px
from .data import load_deforestation_data, calculate_regional_stats

# Load and process data
df, time_series_df = load_deforestation_data()
regional_stats = calculate_regional_stats(df)

# ------------------------------------------------------------------
# Build Choropleth Map - % Forest Remaining (2020 vs 2000)
# ------------------------------------------------------------------

# Compute percentage remaining
df['Percent_Remain'] = (df['forests_2020'] / df['forests_2000']) * 100.0

fig_map = px.choropleth(
    df,
    locations='Country and Area',
    locationmode='country names',
    color='Percent_Remain',
    hover_name='Country and Area',
    hover_data={'Percent_Remain': ':.2f', 'forests_2020': ':,', 'forests_2000': ':,'},
    color_continuous_scale='Greens',
    range_color=(df['Percent_Remain'].min(), df['Percent_Remain'].max()),
    labels={'Percent_Remain': '% Forests Left'},
    title='% Forest Cover Remaining (2020 vs 2000)'
)

fig_map.update_layout(
    geo=dict(showframe=False, showcoastlines=False, projection_type='natural earth'),
    margin=dict(l=0, r=0, t=50, b=0),
    coloraxis_colorbar=dict(title='% Remaining')
)

regional_time_series = time_series_df.groupby(['Region', 'Year'])['Forest_Cover'].mean().reset_index()

# Define a consistent color palette for regions
color_palette = px.colors.qualitative.Plotly
region_colors = {region: color_palette[i % len(color_palette)] for i, region in enumerate(regional_stats['Region'])}

# --- Improved Bar Plot ---
fig_bar = go.Figure()

# Add zero line
fig_bar.add_vline(x=0, line_width=2, line_dash="dash", line_color="grey")

# Add bars
fig_bar.add_trace(go.Bar(
    y=regional_stats['Region'],
    x=regional_stats['Total_Loss'],
    orientation='h',
    marker_color=[region_colors[r] for r in regional_stats['Region']],
    text=regional_stats['Total_Loss'].apply(lambda x: f'{x:,.2f} km²'),
    textposition='auto'
))

# Annotations for context
fig_bar.add_annotation(
    x=regional_stats.loc[regional_stats['Region'] == 'South America', 'Total_Loss'].values[0],
    y='South America',
    text="Amazon deforestation",
    showarrow=True, arrowhead=1, ax=-40, ay=-40
)

fig_bar.update_layout(
    title='Total Forest Cover Change by Region (2000–2020)',
    xaxis_title='Total Forest Loss (km²)',
    yaxis_title='Region',
    paper_bgcolor='white',
    plot_bgcolor='#f8f9fa'
)

# --- Deforestation and Net Loss per Decade Data (from image) ---
deforestation_decades = ['1990s', '2000s', '2010s']
deforestation_vals = [-158, -151, -110]  # in Mha
deforestation_text = ['-158 Mha', '-151 Mha', '-110 Mha']

net_change_vals = [-78, -52, -47]  # in Mha
net_change_text = ['-78 Mha', '-52 Mha', '-47 Mha']

fig_decade = go.Figure()

# Deforestation bars (left, dark red)
fig_decade.add_trace(go.Bar(
    x=deforestation_decades,
    y=deforestation_vals,
    name='Deforestation',
    marker_color='rgb(120,40,40)',
    text=deforestation_text,
    textposition='auto',  # changed from 'outside' to 'auto'
    offsetgroup=0,
    width=0.35,
    cliponaxis=False  # allow text to overflow if needed
))

# Net change bars (right, brown)
fig_decade.add_trace(go.Bar(
    x=deforestation_decades,
    y=net_change_vals,
    name='Net Change in Forest Area',
    marker_color='rgb(180,140,90)',
    text=net_change_text,
    textposition='auto',  # changed from 'outside' to 'auto'
    offsetgroup=1,
    width=0.35,
    cliponaxis=False  # allow text to overflow if needed
))

# Add y-axis padding for negative values
fig_decade.update_layout(
    title='Global Deforestation and Net Loss of Forests per Decade',
    barmode='group',
    xaxis_title='',
    yaxis_title='Change (million hectares)',
    legend_title='',
    paper_bgcolor='white',
    plot_bgcolor='#f8f9fa',
    font=dict(size=16),
    margin=dict(l=40, r=40, t=60, b=40),
    yaxis=dict(
        range=[min(deforestation_vals + net_change_vals) - 20, max(deforestation_vals + net_change_vals) + 20]
    )
)

# --- Drivers of Tropical Forest Degradation (from image) ---
deg_regions = ['Tropical (total)', 'Asia', 'Latin America', 'Africa']
deg_data = {
    'Timber & logging': [58, 82, 70, 21],
    'Fuelwood & charcoal': [27, 15, 10, 62],
    'Wildfires': [10, 2, 15, 7],
    'Livestock grazing on forest': [5, 1, 5, 10]
}
deg_colors = {
    'Timber & logging': '#8c4c2b',
    'Fuelwood & charcoal': '#7c7c7c',
    'Wildfires': '#e38d5c',
    'Livestock grazing on forest': '#5b7f5b'
}
fig_deg = go.Figure()

bottom = [0] * len(deg_regions)
for driver, vals in deg_data.items():
    fig_deg.add_trace(go.Bar(
        x=deg_regions,
        y=vals,
        name=driver,
        marker_color=deg_colors[driver],
        text=[f'{v}%' for v in vals],
        textposition='none',
    ))

fig_deg.update_layout(
    barmode='stack',
    title='Drivers of Tropical Forest Degradation',
    xaxis_title='',
    yaxis_title='Share of Degradation (%)',
    legend_title='',
    paper_bgcolor='white',
    plot_bgcolor='#f8f9fa',
    font=dict(size=16),
    margin=dict(l=40, r=40, t=60, b=40),
    yaxis=dict(range=[0, 100], ticksuffix='%')
)

# --- Global Deforestation by Region (from image) ---
defor_regions = [
    'Global', 'Latin America', 'Southeast Asia', 'Africa', 'North America', 'Russia, China, South Asia', 'Oceania', 'Europe'
]
defor_vals = [5.78, 3.4, 1.6, 0.08, 0.14, 0.09, 0.06, 0.0]  # in Mha
defor_text = ['5.78 Mha', '3.4 Mha', '1.6 Mha', '0.08 Mha', '0.14 Mha', '0.09 Mha', '0.06 Mha', '0 Mha']

fig_defor_region = go.Figure()
fig_defor_region.add_trace(go.Bar(
    x=defor_regions,
    y=defor_vals,
    marker_color='rgb(120,40,60)',
    text=defor_text,
    textposition='auto',  # changed from 'outside' to 'auto'
    width=0.6,
    cliponaxis=False  # allow text to overflow if needed
))

# Remove all extra annotation overlays for a clean look
fig_defor_region.update_layout(
    title='Nearly All Global Deforestation Occurs in the Tropics',
    xaxis_title='',
    yaxis_title='Annual Deforestation (Mha)',
    paper_bgcolor='white',
    plot_bgcolor='#f8f9fa',
    font=dict(size=16),
    margin=dict(l=40, r=40, t=80, b=40),
    yaxis=dict(
        range=[0, max(defor_vals) + 1]  # add padding to top
    )
)

# --- Main Layout ---
def create_deforestation_layout():
    return html.Div([
        html.H1("Global Deforestation Analysis", style={'textAlign': 'center', 'color': 'white'}),

        # Choropleth Map Section
        html.Div([
            html.H3("Global Forests Remaining (2020 vs 2000)", style={'textAlign': 'center'}),
            dcc.Graph(id='deforestation-choropleth', figure=fig_map, style={'height': '600px'})
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '15px', 'margin': '20px'}),

        # Bar Plot Section
            html.Div([
            html.H3("Forest Cover Change by Region", style={'textAlign': 'center'}),
            dcc.Graph(id='deforestation-bar-plot', figure=fig_bar)
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '15px', 'margin': '20px'}),

        # Deforestation and Net Loss per Decade Section
        html.Div([
            html.H3("Global Deforestation and Net Loss of Forests per Decade", style={'textAlign': 'center'}),
            dcc.Graph(id='deforestation-decade-plot', figure=fig_decade)
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '15px', 'margin': '20px'}),

        # Global Deforestation by Region Section
        html.Div([
            html.H3("Nearly All Global Deforestation Occurs in the Tropics", style={'textAlign': 'center'}),
            dcc.Graph(id='deforestation-region-plot', figure=fig_defor_region)
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '15px', 'margin': '20px'}),

        # Drivers of Tropical Forest Degradation Section (moved to bottom)
        html.Div([
            html.H3("Drivers of Tropical Forest Degradation", style={'textAlign': 'center'}),
            dcc.Graph(id='deforestation-degradation-plot', figure=fig_deg)
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '15px', 'margin': '20px'})

    ], style={'backgroundColor': '#004d00', 'padding': '30px', 'minHeight': '100vh'}) 