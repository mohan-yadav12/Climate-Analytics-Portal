from dash import Input, Output
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

from .data import load_temps_by_city
from .layout import fig11, fig21, fig31, fig41, fig51, fig61

def register_temperature_callbacks(app):
    @app.callback(Output('choropleth-map11', 'figure'),
                  [Input('choro-dropdown', 'value')])
    def update_choro(value):
        if value == 'fig11':
            return fig11
        elif value == 'fig21':
            return fig21
        elif value == 'fig31':
            return fig31
        elif value == 'fig41':
            return fig41
        elif value == 'fig51':
            return fig51
        elif value == 'fig61':
            return fig61
