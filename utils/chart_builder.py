from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


COLORS = {
    "cases": "#0d9488",
    "deaths": "#f43f5e",
    "prevalence": "#0284c7",
    "incidence": "#14b8a6",
    "neutral": "#e2e8f0",
    "text": "#0f172a",
}


def _base_layout(figure: go.Figure) -> go.Figure:
    figure.update_layout(
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font={"family": "Arial, sans-serif", "color": COLORS["text"]},
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
    )
    figure.update_xaxes(showgrid=False, zeroline=False)
    figure.update_yaxes(showgrid=False, zeroline=False)
    return figure


def build_trend_chart(filtered_df: pd.DataFrame) -> go.Figure:
    yearly_data = (
        filtered_df.groupby("Year", as_index=False)[["New_Cases", "Deaths"]]
        .sum()
        .sort_values("Year")
    )

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=yearly_data["Year"],
            y=yearly_data["New_Cases"],
            mode="lines+markers",
            name="New Cases",
            line={"color": COLORS["cases"], "width": 4, "shape": "spline", "smoothing": 1.1},
            marker={"size": 7},
            hovertemplate="Year: %{x}<br>New Cases: %{y:,}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=yearly_data["Year"],
            y=yearly_data["Deaths"],
            mode="lines+markers",
            name="Deaths",
            line={"color": COLORS["deaths"], "width": 4, "shape": "spline", "smoothing": 1.1},
            marker={"size": 7},
            hovertemplate="Year: %{x}<br>Deaths: %{y:,}<extra></extra>",
        )
    )
    figure.update_layout(
        title="Trend Analysis: New Cases vs Deaths",
        xaxis_title="Year",
        yaxis_title="Count",
        hovermode="x unified",
    )
    return _base_layout(figure)


def build_prevalence_incidence_chart(filtered_df: pd.DataFrame) -> go.Figure:
    regional_data = (
        filtered_df.groupby("Region", as_index=False)[["Prevalence_Rate", "Incidence_Rate"]]
        .mean()
        .sort_values("Incidence_Rate", ascending=False)
    )

    figure = go.Figure()
    figure.add_trace(
        go.Bar(
            x=regional_data["Region"],
            y=regional_data["Prevalence_Rate"],
            name="Prevalence Rate (%)",
            marker={"color": COLORS["prevalence"], "line": {"width": 0}},
            hovertemplate="Region: %{x}<br>Prevalence: %{y:.2f}%<extra></extra>",
        )
    )
    figure.add_trace(
        go.Bar(
            x=regional_data["Region"],
            y=regional_data["Incidence_Rate"],
            name="Incidence Rate (per 100k)",
            marker={"color": COLORS["incidence"], "line": {"width": 0}},
            hovertemplate="Region: %{x}<br>Incidence: %{y:.2f}<extra></extra>",
        )
    )
    figure.update_layout(
        title="Regional Prevalence and Incidence",
        xaxis_title="Region",
        yaxis_title="Rate",
        barmode="group",
        bargap=0.22,
        bargroupgap=0.08,
    )
    return _base_layout(figure)


def build_choropleth_map(filtered_df: pd.DataFrame, color_metric: str = "New_Cases") -> go.Figure:
    latest_year = int(filtered_df["Year"].max())
    map_data = (
        filtered_df[filtered_df["Year"] == latest_year]
        .groupby(["Country", "Disease"], as_index=False)[["New_Cases", "Prevalence_Rate"]]
        .sum()
    )

    color_scale = "Tealgrn" if color_metric == "New_Cases" else "Blues"
    figure = px.choropleth(
        map_data,
        locations="Country",
        locationmode="country names",
        color=color_metric,
        hover_name="Country",
        hover_data={
            "Disease": True,
            "New_Cases": ":,",
            "Prevalence_Rate": ":.2f",
            color_metric: False,
        },
        color_continuous_scale=color_scale,
        title=f"Global {color_metric.replace('_', ' ')} Map ({latest_year})",
    )
    figure.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth")
    figure.update_layout(coloraxis_colorbar_title=color_metric.replace("_", " "))
    return _base_layout(figure)


def build_lollipop_chart(filtered_df: pd.DataFrame) -> go.Figure:
    regional_data = (
        filtered_df.groupby("Region", as_index=False)["Incidence_Rate"]
        .mean()
        .sort_values("Incidence_Rate", ascending=False)
    )

    figure = go.Figure()
    for _, row in regional_data.iterrows():
        figure.add_trace(
            go.Scatter(
                x=[0, row["Incidence_Rate"]],
                y=[row["Region"], row["Region"]],
                mode="lines",
                line={"color": COLORS["neutral"], "width": 5},
                hoverinfo="skip",
                showlegend=False,
            )
        )

    figure.add_trace(
        go.Scatter(
            x=regional_data["Incidence_Rate"],
            y=regional_data["Region"],
            mode="markers+text",
            marker={
                "size": 14,
                "color": COLORS["deaths"],
                "line": {"color": "white", "width": 2},
            },
            text=[f"{value:.1f}" for value in regional_data["Incidence_Rate"]],
            textposition="middle right",
            name="Incidence Rate",
            hovertemplate="Region: %{y}<br>Incidence Rate: %{x:.2f}<extra></extra>",
        )
    )
    figure.update_layout(
        title="Regional Comparison: Incidence Rate",
        xaxis_title="Incidence Rate (per 100k)",
        yaxis_title="Region",
    )
    return _base_layout(figure)
