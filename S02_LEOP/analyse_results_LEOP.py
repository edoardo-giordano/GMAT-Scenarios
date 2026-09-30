# Data analysis for scenario 02 - LEOP

import os
import pandas as pd
from src.data_analysis import *
from S02_LEOP.leop_config import T0, station_names
from tabulate import tabulate

def data_analyser(output_dir:str, contact_filepath:str, eclipse_filepath:str):

    '''First contact and eclipse data analyser'''

    # ContactLocator.txt file 
    data_contact = parse_locator_report(contact_filepath)                                   # data_contact: pd.DataFrame
    contact_stats = first_contact(data_contact, T0, station_names)                          # _ : pd.DataFrame
    
    # EclipseLocator.txt file
    data_eclipse = parse_locator_report(eclipse_filepath)
    
    # Check if the first contact is in eclipse
    contact_stats["is_in_eclipse"] = contact_stats["first_AOS"].apply(lambda x: check_eclipse(x, data_eclipse))

    # Check if the contact window is - even partially - in eclipse 
    contact_stats["eclipse_overlap"] = contact_stats.apply(lambda row: has_eclipse_overlap(row, data_eclipse), axis=1)

    print("\nFirst contact data")
    print_contact_results(contact_stats)

    plot_contact_eclipse_24h(data_contact, data_eclipse, T0, output_dir)

    

def first_contact(df: pd.DataFrame, t0: pd.Timestamp, stations: list[str]) -> pd.DataFrame:
    '''
    First contact per station, measured from the injection epoch t0 (UTC). Columns:
    - First contact, Contact end: date
    - Time to contact: minutes from the start of the simulation and the first contact
    - Duration
    - In progress at t0: wether the contact is already in progress at the epoch
    '''
    rows = []
    for st in stations:
        sub = df[df["Observer"] == st].sort_values("AOS")
        if sub.empty:
            rows.append({"Observer": st, "first_AOS": pd.NaT, "LOS": pd.NaT, "time_to_contact_min": float("nan"),
                         "duration_s": float("nan"), "in_progress_at_t0": False})
            continue
        first = sub.iloc[0]
        rows.append({
            "Observer": st,
            "first_AOS": first["AOS"],
            "LOS": first["LOS"],
            "time_to_contact_min": (first["AOS"] - t0).total_seconds() / 60,
            "duration_s": first["Duration_s"],
            "in_progress_at_t0": first["AOS"] <= t0,
        })
    return pd.DataFrame(rows).sort_values("first_AOS").reset_index(drop=True)

def check_eclipse(aos_time, eclipse_df):

    # Checks if the first contact date is in eclipse

    match = eclipse_df[(eclipse_df["AOS"] <= aos_time) & (aos_time <= eclipse_df["LOS"])]
    return not match.empty

def has_eclipse_overlap(contact, eclipse_df):

    # Checks if the first contact overlaps with an eclipse

    overlap = (contact["first_AOS"] <= eclipse_df["LOS"]) & (contact["LOS"] >= eclipse_df["AOS"])
    return overlap.any()

def print_contact_results(df: pd.DataFrame):

    #### To print the first contact dataframe

    df_print = df.copy()

    # Date format (GG-MM-AAAA HH:MM:SS)
    date_cols = ["first_AOS", "LOS"]
    for col in date_cols:
        if col in df_print.columns and pd.api.types.is_datetime64_any_dtype(df_print[col]):
            df_print[col] = df_print[col].dt.strftime("%d-%b-%Y %H:%M:%S")

    # Column names
    column_mapping = {
        "Observer": "Observer",
        "first_AOS": "First contact (UTC)",
        "LOS": "End contact (UTC)",
        "time_to_contact_min": "Time to contact [min]",
        "duration_s": "Duration [s]",
        "in_progress_at_t0": "In progress at t0",
        "is_in_eclipse": "In eclipse at t0",
        "eclipse_overlap": "Eclipse overlap",
    }
    
    # Rename columns
    df_print = df_print.rename(columns=column_mapping)

    # Print using tabulate
    print("\n" + tabulate(df_print, headers="keys", tablefmt="plain", showindex=False) + "\n")


if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(repo_root, "S02_LEOP", "output")
    contact_output_path = os.path.join(output_dir, "ContactLocator.txt")
    eclipse_output_path = os.path.join(output_dir, "EclipseLocator.txt")
    data_analyser(output_dir, contact_output_path, eclipse_output_path)