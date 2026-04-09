from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "std_global_data.csv"
CLEANED_DATA_PATH = BASE_DIR / "data" / "cleaned" / "std_cleaned.csv"

YEARS = list(range(2000, 2024))
REGION_COUNTRIES: Dict[str, List[str]] = {
    "African": ["Nigeria", "South Africa", "Kenya", "Ethiopia", "Egypt"],
    "Americas": ["United States", "Canada", "Brazil", "Mexico", "Argentina"],
    "South-East Asia": ["India", "Indonesia", "Thailand", "Bangladesh", "Sri Lanka"],
    "European": ["Germany", "France", "United Kingdom", "Italy", "Spain"],
    "Eastern Mediterranean": ["Saudi Arabia", "Pakistan", "Iran", "Jordan", "Morocco"],
    "Western Pacific": ["China", "Japan", "Australia", "Philippines", "Vietnam"],
}

COUNTRY_POPULATIONS = {
    "Nigeria": 122_000_000,
    "South Africa": 45_000_000,
    "Kenya": 31_000_000,
    "Ethiopia": 66_000_000,
    "Egypt": 68_000_000,
    "United States": 282_000_000,
    "Canada": 31_000_000,
    "Brazil": 175_000_000,
    "Mexico": 99_000_000,
    "Argentina": 37_000_000,
    "India": 1_053_000_000,
    "Indonesia": 214_000_000,
    "Thailand": 62_000_000,
    "Bangladesh": 131_000_000,
    "Sri Lanka": 19_000_000,
    "Germany": 82_000_000,
    "France": 59_000_000,
    "United Kingdom": 59_000_000,
    "Italy": 57_000_000,
    "Spain": 41_000_000,
    "Saudi Arabia": 21_000_000,
    "Pakistan": 138_000_000,
    "Iran": 66_000_000,
    "Jordan": 5_000_000,
    "Morocco": 29_000_000,
    "China": 1_267_000_000,
    "Japan": 127_000_000,
    "Australia": 19_000_000,
    "Philippines": 77_000_000,
    "Vietnam": 79_000_000,
}

DISEASE_CONFIG = {
    "HIV/AIDS": {
        "base_prevalence": 1.1,
        "base_incidence": 92.0,
        "mortality_rate": 0.24,
        "year_trend": -0.012,
        "region_weight": {
            "African": 2.7,
            "Americas": 0.9,
            "South-East Asia": 1.0,
            "European": 0.45,
            "Eastern Mediterranean": 0.55,
            "Western Pacific": 0.7,
        },
    },
    "Hepatitis B": {
        "base_prevalence": 3.2,
        "base_incidence": 118.0,
        "mortality_rate": 0.06,
        "year_trend": -0.007,
        "region_weight": {
            "African": 1.4,
            "Americas": 0.55,
            "South-East Asia": 1.3,
            "European": 0.5,
            "Eastern Mediterranean": 0.85,
            "Western Pacific": 1.55,
        },
    },
    "Syphilis": {
        "base_prevalence": 0.62,
        "base_incidence": 84.0,
        "mortality_rate": 0.02,
        "year_trend": 0.003,
        "region_weight": {
            "African": 1.6,
            "Americas": 1.1,
            "South-East Asia": 0.95,
            "European": 0.65,
            "Eastern Mediterranean": 0.7,
            "Western Pacific": 1.0,
        },
    },
    "HPV": {
        "base_prevalence": 5.1,
        "base_incidence": 156.0,
        "mortality_rate": 0.008,
        "year_trend": -0.004,
        "region_weight": {
            "African": 1.35,
            "Americas": 1.0,
            "South-East Asia": 1.15,
            "European": 0.8,
            "Eastern Mediterranean": 0.72,
            "Western Pacific": 1.08,
        },
    },
}


def generate_synthetic_dataset(output_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Generate a realistic synthetic global STD dataset."""
    rng = np.random.default_rng(42)
    records = []

    for region, countries in REGION_COUNTRIES.items():
        for country_index, country in enumerate(countries):
            base_population = COUNTRY_POPULATIONS[country]
            country_variation = 0.92 + (country_index * 0.035)

            for year in YEARS:
                year_index = year - YEARS[0]
                population_growth = 1 + (0.011 * year_index)
                population = int(base_population * population_growth)

                for disease, config in DISEASE_CONFIG.items():
                    trend_multiplier = max(0.6, 1 + (config["year_trend"] * year_index))
                    regional_weight = config["region_weight"][region]
                    noise = rng.uniform(0.9, 1.12)

                    incidence_rate = (
                        config["base_incidence"]
                        * regional_weight
                        * country_variation
                        * trend_multiplier
                        * noise
                    )
                    incidence_rate = round(max(4.0, incidence_rate), 2)

                    prevalence_rate = (
                        config["base_prevalence"]
                        * regional_weight
                        * country_variation
                        * (1 + rng.uniform(-0.08, 0.08))
                    )
                    prevalence_rate = round(max(0.05, prevalence_rate), 2)

                    new_cases = int((population / 100_000) * incidence_rate)
                    deaths = int(new_cases * config["mortality_rate"] * rng.uniform(0.85, 1.15))

                    records.append(
                        {
                            "Country": country,
                            "Region": region,
                            "Year": year,
                            "Disease": disease,
                            "New_Cases": max(new_cases, 1),
                            "Deaths": max(deaths, 0),
                            "Prevalence_Rate": prevalence_rate,
                            "Incidence_Rate": incidence_rate,
                            "Population": population,
                        }
                    )

    dataframe = pd.DataFrame(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)
    return dataframe


def clean_dataset(
    input_path: Path = RAW_DATA_PATH,
    output_path: Path = CLEANED_DATA_PATH,
) -> pd.DataFrame:
    """Clean the synthetic dataset and persist it to the cleaned directory."""
    if not input_path.exists():
        generate_synthetic_dataset(input_path)

    dataframe = pd.read_csv(input_path)
    dataframe = dataframe.drop_duplicates().copy()

    string_columns = ["Country", "Region", "Disease"]
    for column in string_columns:
        dataframe[column] = dataframe[column].fillna("Unknown").astype(str).str.strip()

    numeric_defaults = {
        "Year": YEARS[0],
        "New_Cases": 0,
        "Deaths": 0,
        "Prevalence_Rate": 0.0,
        "Incidence_Rate": 0.0,
        "Population": 0,
    }

    for column, default_value in numeric_defaults.items():
        dataframe[column] = dataframe[column].fillna(default_value)

    dataframe["Year"] = dataframe["Year"].astype(int)
    dataframe["New_Cases"] = dataframe["New_Cases"].astype(int)
    dataframe["Deaths"] = dataframe["Deaths"].astype(int)
    dataframe["Population"] = dataframe["Population"].astype(int)
    dataframe["Prevalence_Rate"] = dataframe["Prevalence_Rate"].astype(float).round(2)
    dataframe["Incidence_Rate"] = dataframe["Incidence_Rate"].astype(float).round(2)

    dataframe = dataframe.sort_values(
        by=["Disease", "Year", "Region", "Country"], ignore_index=True
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)
    return dataframe


if __name__ == "__main__":
    generate_synthetic_dataset()
    clean_dataset()
