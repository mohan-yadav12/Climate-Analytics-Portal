# CS661 Course Project

Refer to [Proposal](https://hello.iitk.ac.in/manage/cs661sem32425/assignment_answers/Group12_Project%20Proposal_5715b2a0-f2db-4b6f-a1c4-3e686139ff04.pdf) for details. This repository is for technical implementation.

### Points to remember :

If I see your work is trivial, insufficient, and does not meet the quality bar during the final presentation, you will not get a good grade for the project

* ⁠You will build a visual-analytics interface/software to solve a problem from an application domain.
* ⁠⁠You are expected to have knowledge about your domain of application and the tasks you have picked must reflect that.
* ⁠Your tasks should be meaningful, and you should be able to explain why you are doing something.
* ⁠You should be able to tell a coherent story about your data through your visualization interface. ⁠Random set of plots will not help. You need to justify why you picked certain type of plots.
* ⁠You are expected to show meaningful patterns from your data through your interface.
*⁠ ⁠Since this is a visualization focused course, so even if you do a very sophisticated modeling, your visualization interface still should be the main focus for grading. How you are presenting your results will matter
* You are expected to write a comprehensive report of your work that describes the details of the methodologies and visualization techniques that you have used
* ⁠You should justify your design choices for your interface, such as: Why a bar chart and a not a pie chart!

* ⁠Grading will be done on your overall idea + quality of work, presentation, and report
* ⁠Total marks: 300
* ⁠Overall quality: 100
* ⁠Presentation + Q&A: 100 (individual) 
* Report: 100 (group)


*Presentation Slot booked on 13 th July (Sunday) - 11:40am to 12:00pm*

## Architecture

### Data Management Pipeline

#### Why and How We Load Data into DataFrames

All raw data in this project is loaded into pandas DataFrames because DataFrames provide a powerful, flexible, and efficient structure for tabular data. This allows us to:
- Easily handle large datasets with heterogeneous columns (e.g., country, year, metric values)
- Perform fast filtering, aggregation, reshaping, and joining operations
- Apply robust data cleaning and transformation routines using a consistent API
- Seamlessly integrate with visualization libraries like Plotly

**How it works:**
1. Data is loaded from CSV or JSON files using `pandas.read_csv()` or `pandas.read_json()`, resulting in a DataFrame for each dataset.
2. The DataFrame is the central object for all subsequent processing: cleaning, type conversion, aggregation, outlier removal, normalization, and merging.
3. After processing, the DataFrame is passed directly to plotting functions or used in callback logic for interactive dashboards.

This approach ensures that all data transformations are explicit, reproducible, and easy to debug, while leveraging the full power of the pandas ecosystem for data science and analytics.

- **Data Sources**: All raw data is stored in the `dataset/` directory (CSV, JSON, etc).
- **Domain Modules**: Each domain (air quality, greenhouse gas, deforestation, etc.) has a dedicated `data.py` module in `components/` for:
  - Loading raw data
  - Data cleaning (removing/flagging outliers, handling missing values)
  - Normalization (e.g., min-max, z-score)
  - Outlier management (using IQR or domain-specific rules)
  - Data transformation (reshaping, aggregating, merging datasets)
- **Outlier Detection**: The Interquartile Range (IQR) method is used:
  - For each metric, values outside `[Q1 - 1.5*IQR, Q3 + 1.5*IQR]` are removed.
- **Normalization**: Applied as needed (e.g., for composite scores) to ensure comparability across metrics and countries.
- **Caching**: Cleaned data is cached in memory for fast access by the frontend.

### Visualization Pipeline
- The frontend requests processed data from backend modules.
- Data is passed to Plotly Express/Graph Objects to create interactive charts (bar, line, choropleth, etc.).
- User controls (dropdowns, sliders) trigger callbacks that update the plots in real time.

### Frontend/Backend Architecture
- **Backend**: Python modules in `components/` handle all data logic. No separate server API; Dash runs as a single process.
- **Frontend**: Dash layout and callbacks in each component's `layout.py` and `callbacks.py` files. Plots are rendered in the browser, fully interactive.
- **Interaction**: User actions in the browser trigger Python callbacks, which fetch/transform data and update the UI.

This architecture ensures a clean separation of concerns, robust data cleaning, and a responsive, interactive user experience.

### Detailed Data Processing Steps

All data processing is handled in the `data.py` module of each domain (e.g., `components/air_quality/data.py`). The following steps are performed before any data is visualized:

#### 1. Data Wrangling
- **Loading**: Data is loaded from CSV/JSON files using `pandas.read_csv()` or `pandas.read_json()`.
- **Cleaning**: Missing values are handled using `df.dropna()` or `df.fillna()` depending on the context. Duplicate rows are removed with `df.drop_duplicates()`.
- **Type Conversion**: Columns are cast to appropriate types (e.g., `df['year'] = df['year'].astype(int)`).

#### 2. Data Transformation
- **Aggregation**: Data is grouped and aggregated using `df.groupby()` and aggregation functions like `.mean()`, `.sum()`, etc.
- **Reshaping**: Data is pivoted or melted using `df.pivot()`, `df.melt()`, or `df.pivot_table()` to fit the needs of the visualization.
- **Merging**: Multiple datasets are merged using `pd.merge()` to combine related information (e.g., joining emissions and temperature data on year).

#### 3. Outlier Management (IQR Method)
- For each metric, the Interquartile Range (IQR) is computed:
  ```python
  Q1 = df[column].quantile(0.25)
  Q3 = df[column].quantile(0.75)
  IQR = Q3 - Q1
  mask = (df[column] >= Q1 - 1.5 * IQR) & (df[column] <= Q3 + 1.5 * IQR)
  df = df[mask]
  ```
- This removes or flags outliers, ensuring robust analysis and visualization.

#### 4. Normalization
- When combining metrics with different scales (e.g., for composite air quality scores), normalization is applied:
  ```python
  df['norm_col'] = (df['col'] - df['col'].min()) / (df['col'].max() - df['col'].min())
  ```
- This ensures comparability across countries and metrics.

#### 5. Data Flow to Visualization
- After cleaning and transformation, the processed DataFrame is passed to the plotting functions in each component's `layout.py`.
- Example: In `components/air_quality/layout.py`, the cleaned data is used to build a choropleth map with Plotly Express:
  ```python
  fig = px.choropleth(df, locations='country', color='composite_score', ...)
  ```
- User interactions (dropdowns, sliders) trigger callbacks that may further filter or aggregate the data before updating the plots.

This modular and explicit approach ensures that all visualizations are based on high-quality, well-processed data, and that the codebase is easy to maintain and extend.
