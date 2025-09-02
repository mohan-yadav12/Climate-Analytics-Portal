import pandas as pd
from functools import lru_cache

@lru_cache(maxsize=1)
def load_air_quality_data():
    """Load, clean, and cache the air quality dataset."""
    try:
        df = pd.read_csv('dataset/global_air_quality_data_10000.csv')
        # Standardize column names
        df.columns = [col.lower().replace(' ', '_').replace('.', '') for col in df.columns]
        df['date'] = pd.to_datetime(df['date'])
    except FileNotFoundError:
        print("Error: The file 'dataset/global_air_quality_data_10000.csv' was not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return pd.DataFrame()
    return df

def get_countries():
    """Return a sorted list of unique countries."""
    df = load_air_quality_data()
    return sorted(df['country'].unique())

def get_cities(country):
    """Return a sorted list of unique cities for a given country."""
    df = load_air_quality_data()
    return sorted(df[df['country'] == country]['city'].unique())

def get_metrics():
    """Return a list of metrics available for visualization, excluding temperature."""
    return ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3', 'humidity', 'wind_speed']

def get_deaths_by_age_data():
    """Return a DataFrame with deaths from outdoor particulate matter air pollution by age group (1990-2021).
    Data is illustrative and based on the Our World in Data chart. Replace with real data if available.
    """
    import numpy as np
    import pandas as pd
    years = np.arange(1990, 2022)
    # Non-linear, realistic trends (values in thousands)
    under5s = 1400 - 8 * (years - 1990) - 0.2 * (years - 1990) ** 2  # Steady decline
    group5_14 = 80 - 0.5 * (years - 1990)  # Slight decline
    group15_49 = 200 + 2 * (years - 1990) - 0.05 * (years - 1990) ** 2  # Slight rise then fall
    group50_69 = 1200 - 3 * (years - 1990) - 0.5 * (years - 1990) ** 2  # Decline
    group70plus = 2200 - 2 * (years - 1990) - 1.5 * (years - 1990) ** 2  # Decline, but still largest
    # Clamp to minimum 0
    under5s = np.clip(under5s, 0, None)
    group5_14 = np.clip(group5_14, 0, None)
    group15_49 = np.clip(group15_49, 0, None)
    group50_69 = np.clip(group50_69, 0, None)
    group70plus = np.clip(group70plus, 0, None)
    data = {
        'Year': years,
        'Under-5s': under5s * 1000,
        '5-14 year olds': group5_14 * 1000,
        '15-49 year olds': group15_49 * 1000,
        '50-69 year olds': group50_69 * 1000,
        '70+ year olds': group70plus * 1000,
    }
    df = pd.DataFrame(data)
    return df

def get_deaths_by_risk_factor_data():
    """Return a DataFrame with deaths by risk factor (World, 2021). Data is illustrative and based on the Our World in Data chart."""
    data = [
        ("High blood pressure", 10_900_000),
        ("Air pollution (outdoor & indoor)", 8_080_000),
        ("Smoking", 6_180_000),
        ("High blood sugar", 5_290_000),
        ("Outdoor particulate matter pollution", 4_720_000),
        ("Obesity", 3_710_000),
        ("High cholesterol", 3_650_000),
        ("Indoor air pollution", 3_110_000),
        ("Diet high in sodium", 1_860_000),
        ("Alcohol use", 1_810_000),
        ("Diet low in fruits", 1_680_000),
        ("Diet low in whole grains", 1_550_000),
        ("Low birthweight", 1_540_000),
        ("Secondhand smoke", 1_290_000),
        ("Unsafe sex", 901_000),
        ("Diet low in vegetables", 861_000),
        ("Unsafe water source", 802_000),
        ("Diet low in nuts and seeds", 658_000),
        ("Low physical activity", 658_000),
        ("Unsafe sanitation", 595_000),
        ("Child wasting", 494_000),
        ("Drug use", 463_000),
        ("Low bone mineral density", 460_000),
        ("No access to handwashing facility", 446_000),
        ("Child stunting", 311_000),
    ]
    import pandas as pd
    df = pd.DataFrame(data, columns=["Risk Factor", "Deaths"])
    return df

def get_death_rate_by_pollution_type():
    """Return a DataFrame with death rate from air pollution by type (country/region, 1990 & 2021) from deathbyair.csv."""
    df = pd.read_csv('dataset/deathbyair.csv')
    # Build a long-form DataFrame for 1990 and 2021
    records = []
    for _, row in df.iterrows():
        for year in [1990, 2021]:
            records.append({
                'Country or region': row['Country or region'],
                'Year': year,
                'Air pollution (total)': row[f'Total_{year}'],
                'Indoor air pollution': row[f'Indoor_{year}'],
                'Outdoor particulate matter': row[f'PM_{year}'],
                'Outdoor ozone pollution': row[f'Ozone_{year}'],
            })
    return pd.DataFrame(records) 