# Healthcare Analytics Dashboard

A portfolio-ready Streamlit dashboard that explores synthetic global healthcare trends for four major sexually transmitted diseases: HIV/AIDS, Hepatitis B, Syphilis, and HPV. The project highlights yearly trends, regional comparisons, and country-level patterns through interactive Plotly visuals.

## Project Overview

This dashboard was built as Project 4 in Nitin's Data Analyst portfolio. It combines Python, Pandas, Streamlit, and Plotly to simulate how a healthcare analytics team might monitor disease burden across WHO regions from 2000 to 2023.

## Features

- Synthetic global dataset covering 30 countries and all 6 WHO regions
- Sidebar filters for disease, year range, and region selection
- Disease image panel in the sidebar with placeholder paths for custom assets
- KPI cards for new cases, deaths, prevalence rate, and incidence rate
- Smooth trend analysis line chart for new cases and deaths
- Grouped bar chart for prevalence and incidence by region
- Choropleth map for country-level disease patterns
- Horizontal lollipop chart for regional incidence comparison
- Modular utility files for data generation, cleaning, loading, and chart creation

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- Pillow

## Dataset Description

The project uses a realistic synthetic dataset generated programmatically and saved to `data/raw/std_global_data.csv`. The cleaned dataset is stored at `data/cleaned/std_cleaned.csv`.

### Dataset Columns

- `Country`
- `Region`
- `Year`
- `Disease`
- `New_Cases`
- `Deaths`
- `Prevalence_Rate`
- `Incidence_Rate`
- `Population`

## Folder Structure

```text
project-4-healthcare-analytics-dashboard/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── raw/
│   │   └── std_global_data.csv
│   └── cleaned/
│       └── std_cleaned.csv
├── assets/
│   ├── images/
│   │   ├── hiv.png
│   │   ├── hepatitis_b.png
│   │   ├── syphilis.png
│   │   └── hpv.png
│   ├── geojson/
│   └── screenshots/
├── utils/
│   ├── data_loader.py
│   ├── data_cleaner.py
│   └── chart_builder.py
└── .gitignore
```

## How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the dashboard:

```bash
streamlit run app.py
```

3. Open the local Streamlit URL shown in your terminal.

## Screenshots

Add dashboard screenshots here after running the app.

- `assets/screenshots/dashboard-overview.png`
- `assets/screenshots/regional-analysis.png`
- `assets/screenshots/global-map.png`

## Author

Nitin  
GitHub: [https://github.com/nitin4410-naru](https://github.com/nitin4410-naru)
