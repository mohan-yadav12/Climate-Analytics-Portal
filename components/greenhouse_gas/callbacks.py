from dash import callback, Input, Output, State, no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from .data import load_clean_data, get_top_bottom_countries, get_continent_emissions
from functools import lru_cache

df_cached = load_clean_data()

# Callback for the scatter plot
@callback(
    Output('ghg-scatterplot', 'figure'),
    [Input('ghg-country-dropdown', 'value'),
     Input('ghg-gas-dropdown', 'value')]
)
def update_scatterplot(countries, gas):
    if not countries or not gas:
        return go.Figure()

    filtered_df = df_cached[(df_cached['country'].isin(countries)) & (df_cached['gas'] == gas)]
    # Group by country and year to ensure only one line per country
    grouped_df = filtered_df.groupby(['country', 'year'], as_index=False)['value'].sum()

    fig = px.line(
        grouped_df,
        x="year",
        y="value",
        color="country",
        title=f"Line Chart - Average {gas} Emissions by Country",
        labels={'value': f'{gas} Emissions', 'year': 'Year'},
        hover_data=["country"]
    )
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Courier New, monospace", size=18, color="black"),
        xaxis=dict(showgrid=True, gridcolor='lightgrey'),
        yaxis=dict(showgrid=True, gridcolor='lightgrey')
    )
    return fig

# Callback for bar and line charts
@callback(
    Output('ghg-top-5-bar', 'figure'),
    Output('ghg-bottom-5-bar', 'figure'),
    Input('ghg-gas-dropdown', 'value')
)
def update_bar_line_charts(gas):
    if not gas:
        return go.Figure(), go.Figure()

    gas_df = df_cached[df_cached['gas'] == gas]
    if gas_df.empty:
        return go.Figure(), go.Figure()

    top_countries, bottom_countries = get_top_bottom_countries(gas, n=5)

    # Top 5 charts
    if not top_countries.empty:
        top5_df = gas_df[gas_df['country'].isin(top_countries['country'])]
        fig_top_5_bar = px.bar(top5_df, x='country', y='value', color='year', barmode='group',
                               labels={'country': 'Country', 'value': f'{gas} Emissions', 'year': 'Year'},
                               title=f'Bar Chart - Top 5 Countries in {gas} Emissions')
        fig_top_5_line = px.line(top5_df, x="year", y="value", color="country",
                                 title=f"Line Chart - Top 5 Countries in {gas} Emissions")
    else:
        fig_top_5_bar, fig_top_5_line = go.Figure(), go.Figure()

    # Bottom 5 charts
    if not bottom_countries.empty:
        bottom5_df = gas_df[gas_df['country'].isin(bottom_countries['country'])]
        fig_bottom_5_bar = px.bar(bottom5_df, x='country', y='value', color='year', barmode='group',
                                  labels={'country': 'Country', 'value': f'{gas} Emissions', 'year': 'Year'},
                                  title=f'Bar Chart - Bottom 5 Countries in {gas} Emissions')
        fig_bottom_5_line = px.line(bottom5_df, x="year", y="value", color="country",
                                    title=f"Line Chart - Bottom 5 Countries in {gas} Emissions")
    else:
        fig_bottom_5_bar, fig_bottom_5_line = go.Figure(), go.Figure()

    for fig in [fig_top_5_bar, fig_top_5_line, fig_bottom_5_bar, fig_bottom_5_line]:
        fig.update_layout(
            height=400, 
            yaxis_title=f"{gas} Emissions",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Courier New, monospace", size=12, color="black")
        )

    return fig_top_5_bar, fig_bottom_5_bar

@callback(
    Output('ghg-continent-pie-chart', 'figure'),
    [Input('ghg-gas-dropdown', 'value'),
     Input('ghg-year-slider-pie', 'value')]
)
def update_continent_pie_chart(gas, year):
    if not gas or not year:
        return go.Figure()

    continent_emissions = get_continent_emissions(gas, year)
    
    if continent_emissions.empty:
        return go.Figure(layout={'title': f'No data for {gas} in {year}'})

    fig = px.pie(
        continent_emissions,
        names='continent',
        values='value',
        title=f'Continent-wise {gas} Emissions in {year}',
        hole=0.3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font={'color': 'black'}
    )
    return fig

@callback(
    Output('ghg-year-slider-pie', 'min'),
    Output('ghg-year-slider-pie', 'max'),
    Output('ghg-year-slider-pie', 'value'),
    Output('ghg-year-slider-pie', 'marks'),
    Input('ghg-gas-dropdown', 'value')
)
def update_pie_slider(gas):
    if not gas:
        return 2000, 2018, 2018, {}
    
    gas_df = df_cached[df_cached['gas'] == gas]
    if gas_df.empty:
        return 2000, 2018, 2018, {}
        
    min_year = int(gas_df['year'].min())
    max_year = int(gas_df['year'].max())
    marks = {str(year): str(year) for year in range(min_year, max_year + 1, 5)}
    
    return min_year, max_year, max_year, marks

@callback(
    Output('ghg-country-dropdown', 'value'),
    Input('ghg-gas-dropdown', 'value')
)
def update_country_dropdown_defaults(gas):
    if not gas:
        return []
    
    top_countries, _ = get_top_bottom_countries(gas, n=2)
    if not top_countries.empty:
        return top_countries['country'].tolist()
    
    # Fallback if no top countries are found
    all_countries = get_all_countries()
    return all_countries[:2] if all_countries else []

@lru_cache(maxsize=8) # cache for each gas
def get_racing_bar_figure(gas):
    gas_df = df_cached[df_cached['gas'] == gas]
    years = sorted(gas_df['year'].unique())
    if not years:
        return None
        
    df_total = gas_df.groupby(['country', 'year'])['value'].sum().reset_index()
    max_val = df_total['value'].max() * 1.2

    initial_year = years[0]
    initial_data = df_total[df_total.year == initial_year].nlargest(10, 'value').sort_values('value')
    
    fig = go.Figure(
        data=[go.Bar(
            x=initial_data['value'], y=initial_data['country'], orientation='h',
            text=initial_data['value'].apply(lambda x: f'{x:,.0f}'),
            textposition='inside',
            insidetextanchor='end',
            textfont={'color': 'white'}
        )],
        layout=go.Layout(
            xaxis=dict(range=[0, max_val], showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(showticklabels=True, showgrid=False, zeroline=False),
            title_text=f'Top 10 {gas} Emitters - {initial_year}',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': 'black'}
        )
    )

    frames = []
    for year in years:
        df_year = df_total[df_total['year'] == year].nlargest(10, 'value').sort_values('value')
        frame = go.Frame(
            data=[go.Bar(
                x=df_year['value'], y=df_year['country'], orientation='h',
                text=df_year['value'].apply(lambda x: f' {x:,.0f}'),
                textposition='inside',
                insidetextanchor='end',
                textfont={'color': 'white'}
            )],
            name=str(year),
            layout=go.Layout(
                title_text=f'Top 10 {gas} Emitters - {year}',
                xaxis=dict(range=[0, max_val])
            )
        )
        frames.append(frame)
    
    fig.frames = frames

    fig.update_layout(
        updatemenus=[dict(
            type="buttons",
            direction="left",
            x=1.05,
            xanchor="left",
            y=1,
            yanchor="top",
            buttons=[
                dict(label="Play",
                     method="animate",
                     args=[None, {"frame": {"duration": 500, "redraw": True},
                                  "fromcurrent": True, "transition": {"duration": 300, "easing": "linear"}}]),
                dict(label="Pause",
                     method="animate",
                     args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate",
                                    "transition": {"duration": 0}}])
            ],
        )],
        xaxis_title="",
        yaxis_title="",
        height=600,
    )
    fig.update_yaxes(automargin=True)
    
    return fig

# Callback for racing bar chart
@callback(
    Output('ghg-racing-bar', 'figure'),
    Output('racing-bar-title', 'children'),
    Input('ghg-gas-dropdown', 'value')
)
def update_racing_bar_chart(gas):
    if not gas:
        return go.Figure(), "Top 10 Emitting Countries - Growth"

    fig = get_racing_bar_figure(gas)
    if fig is None:
        return go.Figure(layout={'title': f'No data for {gas}'}), f"Top 10 {gas} Emitting Countries - Growth"

    return fig, no_update 