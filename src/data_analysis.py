# Script for data analysis

import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


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

def plot_gantt(df: pd.DataFrame, plot_title: str, output_dir:str):

    # Gantt plotter

    fig, ax = plt.subplots(figsize=(12, 3))

    for i, (obs, group) in enumerate(df.groupby("Observer", dropna=False)):
        intervals = [
            (mdates.date2num(row.AOS), mdates.date2num(row.LOS) - mdates.date2num(row.AOS))
            for row in group.itertuples()
        ]
        ax.broken_barh(intervals, (i - 0.4, 0.8), facecolors="tab:blue")

    labels = [str(obs) if obs is not None else "N/A" for obs, _ in df.groupby("Observer", dropna=False)]
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %H:%M"))
    ax.set_xlabel("Time (UTC)")
    ax.set_title(plot_title)
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    ax.grid(axis="y", linestyle=":", alpha=0.3)
    ax.set_axisbelow(True)
    plt.tight_layout()
    pic_name = (plot_title.replace(" ","_")).lower() + ".png"
    pic_path = output_dir + "/" + pic_name
    plt.savefig(pic_path)
    plt.show()

def plot_contact_overview(df, output_dir:str, title="Contact analysis"):
    groups = list(df.groupby("Observer", dropna=False))
    n_gs = len(groups)
    colors = plt.cm.tab10.colors

    if n_gs <4:
        colors = [(0, 0.4470, 0.7410), (0.8500, 0.3250, 0.0980), (0.9290, 0.6940, 0.1250)]

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 2 + 1.2 * n_gs), sharex=True,
        gridspec_kw={"height_ratios": [n_gs, 2]}
    )

    y_labels = []

    bar_width_min = 15                                                                  # bar width in min
    offset_step_min = bar_width_min * 1.2                                               # distance between bars (different GS)

    for i, (observer, group) in enumerate(groups):
        group = group.sort_values("AOS").reset_index(drop=True)
        color = colors[i % len(colors)]
        label_name = str(observer) if observer is not None else "N/A"
        y_labels.append(label_name)

        # Gantt
        for _, row in group.iterrows():
            ax1.barh(i, row["LOS"] - row["AOS"],
                     left=row["AOS"],
                     height=0.4,
                     color=color,
                     edgecolor="black", linewidth=0.5)
            ax1.grid(axis="x", linestyle="--", alpha=0.5)
            ax1.grid(axis="y", linestyle=":", alpha=0.3)
            ax1.set_axisbelow(True)

        gaps = (group["AOS"].shift(-1) - group["LOS"]).dropna()
        if not gaps.empty:
            idx_max_gap = gaps.dt.total_seconds().idxmax()
            gap_start = group["LOS"].iloc[idx_max_gap]
            gap_end = group["AOS"].iloc[idx_max_gap + 1]
            gap_h = gaps.dt.total_seconds().max() / 3600

            ax1.barh(i, gap_end - gap_start,
                     left=gap_start,
                     height=0.4,
                     color="tomato",
                     alpha=0.5,
                     label=f"Gap max ({label_name}): {gap_h:.1f} h" if i == 0 else None)

        # Contact duration
        offset = pd.Timedelta(minutes=(i - (n_gs - 1) / 2) * offset_step_min)
        x_dodged = group["AOS"] + offset

        ax2.bar(x_dodged, group["Duration_s"],
                width=bar_width_min / (24 * 60),   # bar width in days
                color=color,
                edgecolor="black", linewidth=0.5,
                alpha=0.9,
                label=label_name)

    ax1.set_yticks(range(n_gs))
    ax1.set_yticklabels(y_labels)
    ax1.set_ylabel("Ground Station")
    ax1.set_title(title)
    ax1.grid(axis="x", linestyle="--", alpha=0.5)
    ax1.set_ylim(-0.5, n_gs - 0.5)

    ax2.set_ylabel("Duration [s]")
    ax2.set_xlabel("Date (UTC)")
    ax2.legend(loc="upper right", ncol=min(n_gs, 4), fontsize=8)
    ax2.grid(axis="x", linestyle="--", alpha=0.5)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
    ax2.xaxis.set_major_locator(mdates.AutoDateLocator())

    pic_name = "contact_overview" + ".png"
    pic_path = output_dir + "/" + pic_name
    plt.savefig(pic_path)

    plt.tight_layout()
    plt.show()