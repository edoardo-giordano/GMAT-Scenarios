## Data analyser for S01 - Mission Analysis

import os
import numpy as np
import pandas as pd
from src.data_analysis import parse_locator_report, compute_gap_statistics

def data_analyser(contact_filepath:str, eclipse_filepath:str):

    '''Contact and eclipse data analyser'''

    # ContactLocator.txt file 
    data_contact = parse_locator_report(contact_filepath)                                   # data is a DataFrame
    stats_contact = compute_gap_statistics(data_contact)
    data_printer(stats_contact)

    # EclipseLocator.txt file
    data_eclipse = parse_locator_report(eclipse_filepath)
    stats_eclipse = compute_gap_statistics(data_eclipse)
    data_printer(stats_eclipse)


def data_printer(stats: pd.DataFrame):
    col_names = ["Observer", "N. events", "First contact", "Mean duration [s]", "Min duration [s]", "Max duration [s]",
                     "Mean gap [s]", "Min gap [s]", "Max gap [s]", "|----Start date", "|----End date", "Delta time [s]", "Tot duration [s]", "Coverage [%]"]
    
    print(f"\n#### Coverage statistics ####")
    
    for idx, row in stats.iterrows():
        obs = row["Observer"]
        
        is_eclipse = isinstance(obs, float)
        if is_eclipse:
            print(f"\n# ---- Eclipse ---- #")
        else:
            print(f"\n# ---- Observer {obs} ---- #")
        
        for col, name in zip(stats.columns, col_names):
            data_toprint = row[col]
            if isinstance(data_toprint, float):
                print(f"{name:<18}: {row[col]:.3f}")
            else:
                print(f"{name:<18}: {row[col]}")
    
    print()


if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(repo_root, "S01_mission_analysis", "output")
    contact_output_path = os.path.join(output_dir, "ContactLocator.txt")
    eclipse_output_path = os.path.join(output_dir, "EclipseLocator.txt")
    data_analyser(contact_output_path, eclipse_output_path)