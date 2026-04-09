from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from utils.data_cleaner import CLEANED_DATA_PATH, clean_dataset


@st.cache_data(show_spinner=False)
def load_clean_data(data_path: str | Path = CLEANED_DATA_PATH) -> pd.DataFrame:
    """Load the cleaned dashboard dataset, generating it if needed."""
    resolved_path = Path(data_path)
    if not resolved_path.exists():
        clean_dataset(output_path=resolved_path)
    return pd.read_csv(resolved_path)
