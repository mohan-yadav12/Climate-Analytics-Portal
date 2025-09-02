import pandas as pd

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _clean_numeric(series):
    """Convert a pandas Series of strings to numeric, coercing non-numeric to NaN."""
    return pd.to_numeric(series.astype(str)
                             .str.replace(',', '', regex=False)
                             .str.replace('…', '', regex=False)
                             .str.replace('', '', regex=False)
                             .str.strip(),
                             errors='coerce')


# A *very* small manual region map (keep only what we show in the dashboard).
# Feel free to extend if you want more countries displayed.
REGION_MAP = {
    # South America
    'Brazil': 'South America', 'Colombia': 'South America', 'Peru': 'South America',
    'Venezuela (Bolivarian Republic of)': 'South America',
    # North America
    'United States of America': 'North America', 'Canada': 'North America', 'Mexico': 'North America',
    # Asia
    'China': 'Asia', 'India': 'Asia', 'Indonesia': 'Asia', 'Malaysia': 'Asia', 'Japan': 'Asia',
    # Europe
    'Russian Federation': 'Europe', 'Germany': 'Europe', 'France': 'Europe',
    'United Kingdom of Great Britain and Northern Ireland': 'Europe',
    # Oceania
    'Australia': 'Oceania', 'New Zealand': 'Oceania',
    # Africa
    'Nigeria': 'Africa', 'Democratic Republic of the Congo': 'Africa',
    'South Africa': 'Africa', 'Kenya': 'Africa'
}


# ---------------------------------------------------------------------------
# Public API expected by the layout – DO NOT change function names/signatures
# ---------------------------------------------------------------------------


def load_deforestation_data():
    """Load and preprocess forest-area data for deforestation analysis.

    The new dataset `Forest_Area.csv` contains forest-area snapshots for
    1990-2020.  We only use the 2000 and 2020 columns to keep the
    existing figures untouched while providing more reliable numbers.
    """

    raw = pd.read_csv('dataset/Forest_Area.csv')

    # Drop the aggregated WORLD row and any empty country rows
    raw = raw[raw['Country and Area'].notna() & (raw['Country and Area'] != 'WORLD')]

    # Keep only the columns we need
    cols_of_interest = [
        'Country and Area',
        'Forest Area, 2000',
        'Forest Area, 2020'
    ]
    df = raw[cols_of_interest].copy()

    # Clean numeric columns (some cells contain unicode ellipsis)
    df['forests_2000'] = _clean_numeric(df['Forest Area, 2000'])
    df['forests_2020'] = _clean_numeric(df['Forest Area, 2020'])

    # Drop rows with missing numbers
    df = df.dropna(subset=['forests_2000', 'forests_2020'])

    # Calculate absolute forest-area change (negative = loss)
    df['Forest_Loss'] = df['forests_2020'] - df['forests_2000']

    # Minimal region mapping – rows w/o a region are discarded (keeps visuals tidy)
    df['Region'] = df['Country and Area'].map(REGION_MAP)
    df = df[df['Region'].notna()]

    # ------------------------------------------------------------------
    # Build a time-series dataframe for the line plot
    # We include 2000 and 2020 only to preserve the visual structure; if
    # you want richer detail, extend `years`.
    # ------------------------------------------------------------------

    time_series_rows = []
    years = [2000, 2020]
    for _, row in df.iterrows():
        for yr in years:
            col = f'forests_{yr}' if yr != 2000 else 'forests_2000'
            # 2000 already loaded; for 2020 we have forests_2020
            val = row['forests_2020'] if yr == 2020 else row['forests_2000']
            time_series_rows.append({
                'Year': yr,
                'Forest_Cover': val,
                'Country': row['Country and Area'],
                'Region': row['Region']
            })

    time_series_df = pd.DataFrame(time_series_rows)

    return df, time_series_df

def calculate_regional_stats(df):
    """Calculate regional deforestation statistics."""
    # Group by region and calculate statistics
    regional_stats = df.groupby('Region').agg({
        'Forest_Loss': ['sum', 'mean', 'std'],
        'forests_2020': 'mean'  # Current forest cover
    }).round(2)
    
    # Flatten column names
    regional_stats.columns = ['Total_Loss', 'Average_Loss', 'Loss_Std', 'Current_Forest_Cover']
    regional_stats = regional_stats.reset_index()
    
    # Sort by Total_Loss
    regional_stats = regional_stats.sort_values('Total_Loss', ascending=True)
    
    return regional_stats

def get_top_countries(df, n=10):
    """Get top N countries with most forest loss/gain."""
    df_sorted = df.sort_values('Forest_Loss')
    
    # Get top N losses and gains
    top_losses = df_sorted.head(n)
    top_gains = df_sorted.tail(n)
    
    # Combine and sort by Forest_Loss
    top_changes = pd.concat([top_losses, top_gains])
    top_changes = top_changes.sort_values('Forest_Loss')
    
    return top_changes 