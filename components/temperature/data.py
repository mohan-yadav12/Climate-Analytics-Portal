import pandas as pd
import json
import numpy as np

def load_geojson(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def load_temperatures_by_country(file_path):
    return pd.read_csv(file_path)

def load_major_city_temps():
    df = pd.read_csv('dataset/UpdatedMajorCity_temperatures.csv')
    df['Date'] = pd.to_datetime(df['dt'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    return df

def load_temps_by_city():
    return pd.read_csv("dataset/GlobalLandTemperaturesByCity.csv")

def load_continent_map():
    continent_map = pd.read_csv("dataset/continents2.csv.xls")
    continent_map.rename(columns={'name': 'Country', 'region': 'Region'}, inplace=True)
    return continent_map

def load_global_temps_by_country():
    return pd.read_csv('dataset/GlobalLandTemperaturesByCountry.csv')

def load_global_temps_by_country_v2():
    return pd.read_csv('dataset/GlobalLandTemperaturesByCountry-2.csv')

def load_avg_dataset():
    return pd.read_csv('dataset/avg_dataset.csv')
