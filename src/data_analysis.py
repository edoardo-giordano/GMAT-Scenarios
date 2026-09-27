import re
import pandas as pd


def parse_locator_report(filepath: str) -> pd.DataFrame:
    '''
    Reads a GMAT report (ContactLocator or EclipseLocator .txt) and
    returns a DataFrame with Observer, AOS, LOS, Duration [s] as columns

    This works for a single and multi GS contact analysis
    '''
    #### ---- Use of regex

    # Data format
    date_pattern = r"\d{2} \w{3} \d{4} \d{2}:\d{2}:\d{2}\.\d+"

    # Valid row: {date} {date} {number}
    # if the row doesn't match it is not considered
    # if there are more columns they are not considered
    row_re = re.compile(
        rf"({date_pattern})\s{{2,}}({date_pattern})\s{{2,}}([\d.]+)"
    )

    # Observer row and format
    observer_re = re.compile(r"Observer:\s*(.+)")

    rows = []
    current_observer = None                                                     # takes into account the current GS

    # Read the file and selects the rows
    with open(filepath, "r") as f:
        for line in f:

            # Search for observer
            obs_match = observer_re.search(line)
            if obs_match:
                current_observer = obs_match.group(1).strip()
                continue

            # Search for valid row
            row_match = row_re.search(line)

            if row_match:

                aos_str, los_str, duration_str = row_match.groups()             # groups the 3 data
                rows.append({
                    "Observer": current_observer,
                    "AOS": aos_str,
                    "LOS": los_str,
                    "Duration_s": float(duration_str),
                })

    # Pandas DataFrame
    fmt = "%d %b %Y %H:%M:%S.%f"                                                        # date format
    df = pd.DataFrame(rows, columns=["Observer", "AOS", "LOS", "Duration_s"])

    if not df.empty:
        df["AOS"] = pd.to_datetime(df["AOS"], format=fmt)
        df["LOS"] = pd.to_datetime(df["LOS"], format=fmt)
        df["Duration_s"] = df["Duration_s"].astype(float)

    return df.reset_index(drop=True)

def compute_gap_statistics(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Computes statistics data about duration and gap for every Observer in the DataFrame.
    For EclipseLocator the Observer is treated as a single groupe ("None")
    '''
    if df.empty:
        return pd.DataFrame()

    results = []
    for observer, group in df.groupby("Observer", dropna=False):
        group = group.sort_values("AOS").reset_index(drop=True)

        gaps = (group["AOS"].shift(-1) - group["LOS"]).dt.total_seconds()       # gap between an event and the next one
        gaps = gaps.dropna()                                                    # for the last event

        idx_max = gaps.idxmax()
        gap_start = group["LOS"].iloc[idx_max]
        gap_end = group["AOS"].iloc[idx_max + 1]

        first_aos = group["AOS"].iloc[0]
        last_aos = group["AOS"].iloc[-1]
        time_diff_seconds = (last_aos - first_aos).total_seconds()                  # gap between first and last 

        results.append({
            "Observer": observer,
            "n_events": len(group),
            "first_contact": first_aos,                                                         # date of the first contact
            "duration_mean_s": group["Duration_s"].mean(),                                      # mean duration [s]
            "duration_min_s": group["Duration_s"].min(),                                        # min duration [s]
            "duration_max_s": group["Duration_s"].max(),                                        # max duration [s]
            "gap_mean_s": gaps.mean() if not gaps.empty else None,                              # mean gap [s]
            "gap_min_s": gaps.min() if not gaps.empty else None,                                # min gap [s]
            "gap_max_s": gaps.max() if not gaps.empty else None,                                # max gap [s]
            "gap_max_date": gap_start,                                                          # starting date for max gap
            "gap_min_date": gap_end,                                                            # ending date
            "delta_time": time_diff_seconds,                                                    # time from first to last contact [s]
            "total_duration_s": group["Duration_s"].sum(),                                      # total coverage duration [s]
            "coverage_pct_24h": group["Duration_s"].sum() / time_diff_seconds * 100,            # coverage percentage [%]
        })

    return pd.DataFrame(results)