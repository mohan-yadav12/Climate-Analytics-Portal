from dash import dcc, html
import dash_bootstrap_components as dbc
import base64

with open("dataset/earth_image1.png", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

def create_header():
    return html.Div([
        html.Div(
            [
                html.Img(src=f"data:image/jpg;base64,{encoded_image}", style={"height": "300px", "display": "block", "margin": "auto"}),
                html.H1("VISUALIZING EARTH CLIMATE", style={"text-align": "center", "font-family": "PT Sans Narrow", 'font-size': '60px', 'font-weight': 'bold'}),
            ],
            style={"padding-top": "10px", 'padding-bottom': '10px', "background-color": "black", "color": "white", 'box-shadow': '5px 5px 5px grey', "border-radius": "15px"}
        ),
        
        dbc.Container([
            dbc.Row([
                dbc.Col(create_viz_card("Greenhouse Gases", "Explore greenhouse gas emissions data.", "ghg"), width=4),
                dbc.Col(create_viz_card("Air Quality", "Explore global air quality metrics.", "air-quality"), width=4),
                dbc.Col(create_viz_card("Deforestation", "Visualize deforestation data and its impact.", "deforestation"), width=4),
            ], className="mb-4 mt-4"),
            dbc.Row([
                dbc.Col(create_viz_card("Temperature", "Analyze historical temperature data and trends.", "temperature"), width=4),
                dbc.Col(create_viz_card("Sea Levels", "Investigate sea level rise over the years.", "sea"), width=4),
                dbc.Col(create_viz_card("Correlations", "Discover correlations between different climate indicators.", "correlation"), width=4),
            ], justify="center", className="mb-4"),
        ], fluid=True),
    ], style={"background-color": "#CDDEEE", "padding": "10px"})


def create_viz_card(title, description, value):
    card = dbc.Card(
        [
            dbc.CardHeader(
                html.H5(title, className="card-title"),
                style={'background-color': '#e6fffa', 'color': 'black'}
            ),
            dbc.CardBody(
                [
                    html.P(description, className="card-text"),
                ],
                style={'background-color': 'white', 'color': 'black'}
            ),
        ],
        style={"height": "100%"}
    )
    return dcc.Link(
        children=[card],
        href=f"/{value}",
        style={'text-decoration': 'none'}
    )
