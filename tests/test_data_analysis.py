# Tests for ./src/data_analysis.py script

import os
import pandas as pd
import pytest

from src.data_analysis import parse_locator_report, compute_gap_statistics

fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")


def fixture_path(name: str) -> str:
    return os.path.join(fixtures_dir, name)


# --------------------------------------------------------
# Test per parse_locator_report
# --------------------------------------------------------

def test_parse_contact_real_shape_and_dtypes():

    # Test for shape and data types of the report files
    # Report file: contact_real.txt
    
    df = parse_locator_report(fixture_path("contact_real.txt"))

    assert df.shape == (10, 4)
    assert set(df["Observer"].unique()) == {"Redu"}
    assert df["Duration_s"].dtype == float
    assert pd.api.types.is_datetime64_any_dtype(df["AOS"])
    assert pd.api.types.is_datetime64_any_dtype(df["LOS"])


def test_parse_eclipse_real_shape():

    # Test for the eclipse report file (shape)
    
    df = parse_locator_report(fixture_path("eclipse_real.txt"))
    assert df.shape == (79, 4)
    
    # Observer field has to be None for every row
    
    assert df["Observer"].isna().all()


def test_parse_zero_events_returns_empty_dataframe():

    # Test for empty report 
    # It shall return an empty DataFrame

    df = parse_locator_report(fixture_path("empty_report.txt"))

    assert df.empty
    assert list(df.columns) == ["Observer", "AOS", "LOS", "Duration_s"]


def test_parse_multi_gs_assigns_correct_observer():

    # Test for multi-GS report
    # Every row shall be associated to the right GS

    df = parse_locator_report(fixture_path("multi_gs_contact.txt"))

    assert df.shape == (4, 4)
    assert list(df["Observer"]) == ["Redu", "Redu", "Fucino", "Fucino"]


# --------------------------------------------------------
# Test per compute_gap_statistics
# --------------------------------------------------------

def test_gap_statistics_empty_input():

    # Test for empty DataFrame
    # With an empty DF it shall return an empty DF
    
    empty_df = pd.DataFrame(columns=["Observer", "AOS", "LOS", "Duration_s"])
    result = compute_gap_statistics(empty_df)

    assert result.empty


def test_gap_statistics_single_observer_known_values():
    """
    We set a known DatFrame to check if the function works

    Event 1: 10:00:00 - 10:05:00
    Event 2: 10:15:00 - 10:20:00   -> gap with event 1 = 600s  (10 min)
    Event 3: 11:00:00 - 11:05:00   -> gap with event 2 = 2400s (40 min)
    """

    df = pd.DataFrame({
        "Observer": ["Redu"] * 3,
        "AOS": pd.to_datetime([
            "2026-09-19 10:00:00", "2026-09-19 10:15:00", "2026-09-19 11:00:00"
        ]),
        "LOS": pd.to_datetime([
            "2026-09-19 10:05:00", "2026-09-19 10:20:00", "2026-09-19 11:05:00"
        ]),
        "Duration_s": [300.0, 300.0, 300.0],
    })

    result = compute_gap_statistics(df)
    row = result.iloc[0]

    assert row["n_events"] == 3
    assert row["gap_min_s"] == pytest.approx(600.0)
    assert row["gap_max_s"] == pytest.approx(2400.0)
    assert row["gap_mean_s"] == pytest.approx((600.0 + 2400.0) / 2)


def test_gap_statistics_multi_observer_gap_dates_not_mixed():
    """
    Data has to be referred to the right GS

    Fixture (multi_gs_interleaved.txt):
      Redu:   06:00-06:05  e  20:00-20:05   -> only gap: 14h (50700s)
      Fucino: 08:00-08:05  e  09:00-09:05   -> only gap: 55 min (3300s)
    """
    df = parse_locator_report(fixture_path("multi_gs_contact.txt"))
    result = compute_gap_statistics(df).set_index("Observer")

    # Redu's gap shall start and end with Redu's data
    redu_gap_start = result.loc["Redu", "gap_max_date"]
    redu_gap_end = result.loc["Redu", "gap_min_date"]
    
    assert redu_gap_start == pd.Timestamp("2026-09-19 06:05:00")
    assert redu_gap_end == pd.Timestamp("2026-09-19 20:00:00")

    # Fucino's gap shall start and end with Fucino's data
    fucino_gap_start = result.loc["Fucino", "gap_max_date"]
    fucino_gap_end = result.loc["Fucino", "gap_min_date"]

    assert fucino_gap_start == pd.Timestamp("2026-09-19 08:05:00")
    assert fucino_gap_end == pd.Timestamp("2026-09-19 09:00:00")