import pandas as pd
from functools import lru_cache
import pycountry_convert as pc
import re

# Mapping for country names that differ between datasets or are aggregations
COUNTRY_NAME_MAP = {
    'European Union (27)': None,
    'World': None,
    'Russian Federation': 'Russia',
    'United Kingdom of Great Britain and Northern Ireland': 'United Kingdom',
    'United States of America': 'United States',
    "Iran (Islamic Republic of)": "Iran",
    "Republic of Korea": "South Korea",
    "Republic of Moldova": "Moldova",
    "The former Yugoslav Republic of Macedonia": "North Macedonia",
    "Viet Nam": "Vietnam",
    "Brunei Darussalam": "Brunei",
}

# A more robust mapping for countries to continents
MANUAL_COUNTRY_TO_CONTINENT = {
    'Afghanistan': 'Asia',
    'Albania': 'Europe',
    'Algeria': 'Africa',
    'Andorra': 'Europe',
    'Angola': 'Africa',
    'Antigua and Barbuda': 'Americas',
    'Argentina': 'Americas',
    'Armenia': 'Asia',
    'Australia': 'Oceania',
    'Austria': 'Europe',
    'Azerbaijan': 'Asia',
    'Bahamas': 'Americas',
    'Bahrain': 'Asia',
    'Bangladesh': 'Asia',
    'Barbados': 'Americas',
    'Belarus': 'Europe',
    'Belgium': 'Europe',
    'Belize': 'Americas',
    'Benin': 'Africa',
    'Bhutan': 'Asia',
    'Bolivia': 'Americas',
    'Bolivia (Plurinational State of)': 'Americas',
    'Bosnia and Herzegovina': 'Europe',
    'Botswana': 'Africa',
    'Brazil': 'Americas',
    'Brunei': 'Asia',
    'Brunei Darussalam': 'Asia',
    'Bulgaria': 'Europe',
    'Burkina Faso': 'Africa',
    'Burundi': 'Africa',
    'Cabo Verde': 'Africa',
    'Cambodia': 'Asia',
    'Cameroon': 'Africa',
    'Canada': 'Americas',
    'Central African Republic': 'Africa',
    'Chad': 'Africa',
    'Chile': 'Americas',
    'China': 'Asia',
    'Colombia': 'Americas',
    'Comoros': 'Africa',
    'Congo': 'Africa',
    'Republic of Congo': 'Africa',
    'Democratic Republic of the Congo': 'Africa',
    'Cook Islands': 'Oceania',
    'Costa Rica': 'Americas',
    "Côte d'Ivoire": 'Africa',
    'Croatia': 'Europe',
    'Cuba': 'Americas',
    'Cyprus': 'Europe',
    'Czechia': 'Europe',
    'Czech Republic': 'Europe',
    'Denmark': 'Europe',
    'Djibouti': 'Africa',
    'Dominica': 'Americas',
    'Dominican Republic': 'Americas',
    'Ecuador': 'Americas',
    'Egypt': 'Africa',
    'El Salvador': 'Americas',
    'Equatorial Guinea': 'Africa',
    'Eritrea': 'Africa',
    'Estonia': 'Europe',
    'Eswatini': 'Africa',
    'Ethiopia': 'Africa',
    'Fiji': 'Oceania',
    'Finland': 'Europe',
    'France': 'Europe',
    'Gabon': 'Africa',
    'Gambia': 'Africa',
    'Georgia': 'Asia',
    'Germany': 'Europe',
    'Ghana': 'Africa',
    'Greece': 'Europe',
    'Grenada': 'Americas',
    'Guatemala': 'Americas',
    'Guinea': 'Africa',
    'Guinea-Bissau': 'Africa',
    'Guyana': 'Americas',
    'Haiti': 'Americas',
    'Honduras': 'Americas',
    'Hungary': 'Europe',
    'Iceland': 'Europe',
    'India': 'Asia',
    'Indonesia': 'Asia',
    'Iran': 'Asia',
    'Iran (Islamic Republic of)': 'Asia',
    'Iraq': 'Asia',
    'Ireland': 'Europe',
    'Israel': 'Asia',
    'Italy': 'Europe',
    'Jamaica': 'Americas',
    'Japan': 'Asia',
    'Jordan': 'Asia',
    'Kazakhstan': 'Asia',
    'Kenya': 'Africa',
    'Kiribati': 'Oceania',
    'Kuwait': 'Asia',
    'Kyrgyzstan': 'Asia',
    'Laos': "Asia",
    "Lao People's Democratic Republic": 'Asia',
    'Latvia': 'Europe',
    'Lebanon': 'Asia',
    'Lesotho': 'Africa',
    'Liberia': 'Africa',
    'Libya': 'Africa',
    'Liechtenstein': 'Europe',
    'Lithuania': 'Europe',
    'Luxembourg': 'Europe',
    'Madagascar': 'Africa',
    'Malawi': 'Africa',
    'Malaysia': 'Asia',
    'Maldives': 'Asia',
    'Mali': 'Africa',
    'Malta': 'Europe',
    'Marshall Islands': 'Oceania',
    'Mauritania': 'Africa',
    'Mauritius': 'Africa',
    'Mexico': 'Americas',
    'Micronesia': 'Oceania',
    'Micronesia (Federated States of)': 'Oceania',
    'Moldova': 'Europe',
    'Republic of Moldova': 'Europe',
    'Mongolia': 'Asia',
    'Montenegro': 'Europe',
    'Morocco': 'Africa',
    'Mozambique': 'Africa',
    'Myanmar': 'Asia',
    'Namibia': 'Africa',
    'Nauru': 'Oceania',
    'Nepal': 'Asia',
    'Netherlands': 'Europe',
    'New Zealand': 'Oceania',
    'Nicaragua': 'Americas',
    'Niger': 'Africa',
    'Nigeria': 'Africa',
    'Niue': 'Oceania',
    'North Korea': 'Asia',
    'North Macedonia': 'Europe',
    'The former Yugoslav Republic of Macedonia': 'Europe',
    'Norway': 'Europe',
    'Oman': 'Asia',
    'Pakistan': 'Asia',
    'Palau': 'Oceania',
    'Panama': 'Americas',
    'Papua New Guinea': 'Oceania',
    'Paraguay': 'Americas',
    'Peru': 'Americas',
    'Philippines': 'Asia',
    'Poland': 'Europe',
    'Portugal': 'Europe',
    'Qatar': 'Asia',
    'Romania': 'Europe',
    'Russia': 'Europe',
    'Russian Federation': 'Europe',
    'Rwanda': 'Africa',
    'Saint Kitts and Nevis': 'Americas',
    'Saint Lucia': 'Americas',
    'Saint Vincent and the Grenadines': 'Americas',
    'Samoa': 'Oceania',
    'Sao Tome and Principe': 'Africa',
    'Saudi Arabia': 'Asia',
    'Senegal': 'Africa',
    'Serbia': 'Europe',
    'Seychelles': 'Africa',
    'Sierra Leone': 'Africa',
    'Singapore': 'Asia',
    'Slovakia': 'Europe',
    'Slovenia': 'Europe',
    'Solomon Islands': 'Oceania',
    'Somalia': 'Africa',
    'South Africa': 'Africa',
    'South Korea': 'Asia',
    'Republic of Korea': 'Asia',
    'South Sudan': 'Africa',
    'Spain': 'Europe',
    'Sri Lanka': 'Asia',
    'Sudan': 'Africa',
    'Suriname': 'Americas',
    'Sweden': 'Europe',
    'Switzerland': 'Europe',
    'Syria': 'Asia',
    'Syrian Arab Republic': 'Asia',
    'Tajikistan': 'Asia',
    'Tanzania': 'Africa',
    'United Republic of Tanzania': 'Africa',
    'Thailand': 'Asia',
    'Timor-Leste': 'Asia',
    'Togo': 'Africa',
    'Tonga': 'Oceania',
    'Trinidad and Tobago': 'Americas',
    'Tunisia': 'Africa',
    'Turkey': 'Asia',
    'Turkmenistan': 'Asia',
    'Tuvalu': 'Oceania',
    'Uganda': 'Africa',
    'Ukraine': 'Europe',
    'United Arab Emirates': 'Asia',
    'United Kingdom': 'Europe',
    'United Kingdom of Great Britain and Northern Ireland': 'Europe',
    'United States': 'Americas',
    'United States of America': 'Americas',
    'Uruguay': 'Americas',
    'Uzbekistan': 'Asia',
    'Vanuatu': 'Oceania',
    'Venezuela': 'Americas',
    'Venezuela (Bolivarian Republic of)': 'Americas',
    'Viet Nam': 'Asia',
    'Vietnam': 'Asia',
    'Yemen': 'Asia',
    'Zambia': 'Africa',
    'Zimbabwe': 'Africa',
}


# Gas columns from the "worldwide" dataset
GAS_COLUMN_MAP_WORLDWIDE = {
    'co2_gigagrams': 'CO2',
    'methane_gigagrams': 'CH4',
    'n2o_gigagrams': 'N2O',
    'hfc_gigagrams': 'HFC',
    'pfc_gigagrams': 'PFC',
    'sf6_gigagrams': 'SF6'
}

# Regex to find gas names in the inventory data's category column
GAS_REGEX_MAP_INVENTORY = {
    'CO2': re.compile(r'carbon_dioxide'),
    'CH4': re.compile(r'methane'),
    'N2O': re.compile(r'nitrous_oxide'),
    'HFC': re.compile(r'hfc'),
    'PFC': re.compile(r'pfc'),
    'SF6': re.compile(r'sulfur_hexafluoride'),
    'Total GHG': re.compile(r'greenhouse_gas_ghg_emissions_including|all_gases')
}

def _get_gas_from_category(category):
    for gas, pattern in GAS_REGEX_MAP_INVENTORY.items():
        if pattern.search(category):
            return gas
    if re.search(r'ghg|greenhouse', category, re.IGNORECASE):
        return 'Total GHG'
    return 'Unknown'


@lru_cache(maxsize=None)
def _get_continent(country_name):
    """Converts a country name to a continent name using a manual map."""
    if not isinstance(country_name, str):
        return 'Unknown'

    # Normalize name for lookup
    normalized_name = COUNTRY_NAME_MAP.get(country_name, country_name)
    return MANUAL_COUNTRY_TO_CONTINENT.get(normalized_name, 'Unknown')


@lru_cache(maxsize=1)
def load_historical_data() -> pd.DataFrame:
    """Loads and processes the historical total GHG emissions data from 'ALL GHG_historical_emissions.csv'."""
    df = pd.read_csv("dataset/ALL GHG_historical_emissions.csv")
    df = df.melt(id_vars=['Country', 'Data source', 'Sector', 'Gas', 'Unit'], var_name='Year', value_name='Value')
    df = df.rename(columns={'Country': 'country', 'Gas': 'gas', 'Value': 'value', 'Year': 'year'})
    df['country'] = df['country'].replace(COUNTRY_NAME_MAP).dropna()
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['value'] = pd.to_numeric(df['value'].astype(str).str.replace(',', ''), errors='coerce')
    df.loc[df['Unit'] == 'MtCO₂e', 'value'] *= 1000 # Convert Mt to Gg
    df['gas'] = 'Total GHG'
    return df[['country', 'year', 'gas', 'value']].dropna()

@lru_cache(maxsize=1)
def load_worldwide_data() -> pd.DataFrame:
    """Loads and processes per-gas emissions from 'Greenhouse Gas Emissions worldwide.csv'."""
    df = pd.read_csv("dataset/Greenhouse Gas Emissions worldwide.csv")
    df = df.rename(columns={'Country or Area': 'country', 'Year': 'year'})
    df = pd.melt(df, id_vars=['country', 'year'], value_vars=GAS_COLUMN_MAP_WORLDWIDE.keys(), var_name='gas', value_name='value')
    df['gas'] = df['gas'].map(GAS_COLUMN_MAP_WORLDWIDE)
    df['country'] = df['country'].replace(COUNTRY_NAME_MAP)
    df = df.dropna(subset=['country', 'gas'])
    return df[['country', 'year', 'gas', 'value']].dropna()

@lru_cache(maxsize=1)
def load_carbon_data() -> pd.DataFrame:
    """Loads and processes CO2 data from 'carbon_emissions.csv'."""
    df = pd.read_csv("dataset/carbon_emissions.csv", usecols=lambda c: c not in ['Latitude', 'Longitude'])
    df = df.melt(id_vars=['Country', 'Data source', 'Sector', 'Gas', 'Unit'], var_name='Year', value_name='Value')
    df = df.rename(columns={'Country': 'country', 'Gas': 'gas', 'Value': 'value', 'Year': 'year'})
    df = df[df['gas'] == 'CO2'] # Ensure only CO2 data is processed
    df['country'] = df['country'].replace(COUNTRY_NAME_MAP).dropna()
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df.loc[df['Unit'] == 'MtCO₂e', 'value'] *= 1000  # Convert Mt to Gg
    return df[['country', 'year', 'gas', 'value']].dropna()

@lru_cache(maxsize=1)
def load_inventory_data() -> pd.DataFrame:
    """Loads and processes data from 'greenhouse_gas_inventory_data_data.csv'."""
    df = pd.read_csv("dataset/greenhouse_gas_inventory_data_data.csv")
    df = df.rename(columns={'country_or_area': 'country', 'year': 'year', 'value': 'value', 'category': 'category'})
    df['gas'] = df['category'].apply(_get_gas_from_category)
    df = df.dropna(subset=['gas'])
    df['country'] = df['country'].replace(COUNTRY_NAME_MAP)
    df.loc[df['category'].str.contains('kilotonne'), 'value'] *= 1 # Convert kt to Gg
    return df[['country', 'year', 'gas', 'value']].dropna()

@lru_cache(maxsize=1)
def load_clean_data() -> pd.DataFrame:
    """Loads, merges, and cleans all available GHG emissions data, prioritizing sources."""
    df_hist = load_historical_data()
    df_world = load_worldwide_data()
    df_inv = load_inventory_data()
    df_carbon = load_carbon_data()

    # Prioritize: historical (Total GHG), worldwide, inventory, carbon
    df_combined = pd.concat([df_hist, df_world, df_inv, df_carbon], ignore_index=True)
    df_combined.drop_duplicates(subset=['country', 'year', 'gas'], keep='first', inplace=True)
    
    df_combined = df_combined.dropna(subset=['country', 'year', 'gas', 'value'])
    df_combined['year'] = df_combined['year'].astype(int)
    
    return df_combined

def get_continent_emissions(gas: str, year: int) -> pd.DataFrame:
    """Calculate total emissions per continent for a given gas and year, merging Oceania and Unknown as 'Rest of the World'."""
    df = load_clean_data()
    # Add continent information for the calculation
    df['continent'] = df['country'].apply(_get_continent)
    df_year = df[(df['year'] == year) & (df['gas'] == gas)]
    continent_emissions = df_year.groupby('continent')['value'].sum().reset_index()
    # Merge Oceania and Unknown as 'Rest of the World'
    mask = continent_emissions['continent'].isin(['Oceania', 'Unknown'])
    rest_sum = continent_emissions.loc[mask, 'value'].sum()
    continent_emissions = continent_emissions[~mask]
    if rest_sum > 0:
        continent_emissions = pd.concat([
            continent_emissions,
            pd.DataFrame({'continent': ['Rest of the World'], 'value': [rest_sum]})
        ], ignore_index=True)
    return continent_emissions

def available_gases():
    """Returns a list of available gases from the dataset."""
    return sorted(load_clean_data()['gas'].unique())

def latest_year(gas: str = None) -> int:
    """Returns the most recent year in the dataset, optionally for a specific gas."""
    df = load_clean_data()
    if gas:
        gas_df = df[df['gas'] == gas]
        if not gas_df.empty:
            return gas_df['year'].max()
    return df['year'].max()

def get_top_bottom_countries(gas: str, n: int = 5):
    """Gets the top and bottom N emitting countries for the latest year for that gas."""
    df = load_clean_data()
    gas_df = df[df['gas'] == gas]
    
    if gas_df.empty:
        return pd.DataFrame(), pd.DataFrame()
        
    latest = gas_df['year'].max()
    gas_df_latest = gas_df[gas_df['year'] == latest]
    
    top_countries = gas_df_latest.nlargest(n, 'value')
    bottom_countries = gas_df_latest[gas_df_latest['value'] > 0].nsmallest(n, 'value')
    
    return top_countries, bottom_countries

def get_all_countries():
    """Returns a sorted list of all unique countries."""
    return sorted(load_clean_data()['country'].unique()) 