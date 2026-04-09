from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from utils.chart_builder import (
    build_choropleth_map,
    build_lollipop_chart,
    build_prevalence_incidence_chart,
    build_trend_chart,
)
from utils.data_cleaner import clean_dataset
from utils.data_loader import load_clean_data


st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
)


BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATHS = {
    "HIV/AIDS": BASE_DIR / "assets" / "images" / "hiv.png",
    "Hepatitis B": BASE_DIR / "assets" / "images" / "hepatitis_b.png",
    "Syphilis": BASE_DIR / "assets" / "images" / "syphilis.png",
    "HPV": BASE_DIR / "assets" / "images" / "hpv.png",
}

COLOR_METRICS = {
    "New Cases": "New_Cases",
    "Prevalence Rate": "Prevalence_Rate",
}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .main {
                background: linear-gradient(180deg, #f8fafc 0%, #ecfeff 100%);
            }
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
            }
            div[data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.88);
                border: 1px solid #dbeafe;
                padding: 1rem;
                border-radius: 18px;
                box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
            }
            div[data-testid="stMetricLabel"] {
                font-weight: 600;
            }
            .section-title {
                color: #0f172a;
                font-weight: 700;
                letter-spacing: 0.01em;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def filter_dashboard_data(
    dataframe: pd.DataFrame,
    disease: str,
    year_range: tuple[int, int],
    selected_regions: list[str],
) -> pd.DataFrame:
    filtered_df = dataframe[
        (dataframe["Disease"] == disease)
        & (dataframe["Year"].between(year_range[0], year_range[1]))
        & (dataframe["Region"].isin(selected_regions))
    ].copy()
    return filtered_df


def calculate_delta(current_value: float, previous_value: float, as_percent: bool = False) -> str:
    delta = current_value - previous_value
    if as_percent:
        return f"{delta:+.2f}"
    return f"{delta:+,.0f}"


def show_sidebar(dataframe: pd.DataFrame) -> tuple[str, tuple[int, int], list[str], str]:
    st.sidebar.title("Dashboard Filters")
    disease_options = list(dataframe["Disease"].dropna().unique())
    disease = st.sidebar.radio("Select Disease", disease_options, index=0)

    min_year = int(dataframe["Year"].min())
    max_year = int(dataframe["Year"].max())
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )

    region_options = sorted(dataframe["Region"].dropna().unique())
    selected_regions = st.sidebar.multiselect(
        "Select Regions",
        options=region_options,
        default=region_options,
    )

    map_metric_label = st.sidebar.radio(
        "Map Color Metric",
        options=list(COLOR_METRICS.keys()),
        index=0,
    )

    image_path = IMAGE_PATHS[disease]
    st.sidebar.subheader("Disease Snapshot")
    if image_path.exists():
        st.sidebar.image(str(image_path), caption=f"{disease} illustration", use_container_width=True)
    else:
        st.sidebar.caption(f"Placeholder image path: {image_path}")

    return disease, year_range, selected_regions, COLOR_METRICS[map_metric_label]


def render_kpi_cards(filtered_df: pd.DataFrame) -> None:
    latest_year = int(filtered_df["Year"].max())
    previous_year = latest_year - 1

    current_year_df = filtered_df[filtered_df["Year"] == latest_year]
    previous_year_df = filtered_df[filtered_df["Year"] == previous_year]

    total_new_cases = current_year_df["New_Cases"].sum()
    total_deaths = current_year_df["Deaths"].sum()
    avg_prevalence = current_year_df["Prevalence_Rate"].mean()
    avg_incidence = current_year_df["Incidence_Rate"].mean()

    previous_new_cases = previous_year_df["New_Cases"].sum()
    previous_deaths = previous_year_df["Deaths"].sum()
    previous_prevalence = previous_year_df["Prevalence_Rate"].mean()
    previous_incidence = previous_year_df["Incidence_Rate"].mean()

    metric_columns = st.columns(4)
    metric_columns[0].metric(
        "Total New Cases",
        f"{int(total_new_cases):,}",
        calculate_delta(total_new_cases, previous_new_cases),
    )
    metric_columns[1].metric(
        "Total Deaths",
        f"{int(total_deaths):,}",
        calculate_delta(total_deaths, previous_deaths),
    )
    metric_columns[2].metric(
        "Avg Prevalence Rate (%)",
        f"{avg_prevalence:.2f}",
        calculate_delta(avg_prevalence, previous_prevalence, as_percent=True),
    )
    metric_columns[3].metric(
        "Avg Incidence Rate (per 100k)",
        f"{avg_incidence:.2f}",
        calculate_delta(avg_incidence, previous_incidence, as_percent=True),
    )


def main() -> None:
    inject_styles()
    clean_dataset()
    dataframe = load_clean_data()

    st.title("Healthcare Analytics Dashboard")
    st.caption(
        "Interactive healthcare surveillance dashboard tracking HIV/AIDS, Hepatitis B, Syphilis, and HPV across WHO regions from 2000 to 2023."
    )

    disease, year_range, selected_regions, map_metric = show_sidebar(dataframe)
    if not selected_regions:
        st.warning("Select at least one region to view the dashboard.")
        return

    filtered_df = filter_dashboard_data(dataframe, disease, year_range, selected_regions)
    if filtered_df.empty:
        st.warning("No records match the selected filters.")
        return

    st.markdown('<p class="section-title">Key Performance Indicators</p>', unsafe_allow_html=True)
    render_kpi_cards(filtered_df)

    st.divider()
    st.subheader("Trend Analysis")
    st.plotly_chart(build_trend_chart(filtered_df), use_container_width=True)

    chart_column_1, chart_column_2 = st.columns(2)
    with chart_column_1:
        st.subheader("Prevalence and Incidence")
        st.plotly_chart(
            build_prevalence_incidence_chart(filtered_df),
            use_container_width=True,
        )
    with chart_column_2:
        st.subheader("Regional Incidence Comparison")
        st.plotly_chart(build_lollipop_chart(filtered_df), use_container_width=True)

    st.divider()
    st.subheader("Geographic Distribution")
    st.plotly_chart(build_choropleth_map(filtered_df, color_metric=map_metric), use_container_width=True)


if __name__ == "__main__":
    main()
