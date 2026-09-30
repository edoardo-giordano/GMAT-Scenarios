# This script configures the LEOP scenario

import pandas as pd
from src.ground_stations import ground_stations_data

# --- Injection epoch (UTC) ---
year    = 2026
month   = 9
day     = 30
hour    = 00
min     = 00
sec     = 00

epoch = [year, month, day, hour, min, sec]
date_str = str(year) + "-" + str(month) + "-" + str(day) + " " + str(hour) + ":" + str(min) + ":" + str(sec)
T0 = pd.Timestamp(date_str, tz="UTC")

def t0_gmat_str() -> str:

    # Changes T0 in the right format for GMAT
    
    return T0.strftime("%d %b %Y %H:%M:%S.%f")[:-3]   # es. "05 Nov 2026 00:00:00.000"

# --- Ground stations in this scenario ---
station_names = ["Betzdirf", "Fucino", "Perth", "Paumalu"]
stations = {name: ground_stations_data[name] for name in station_names}

# --- Nominal state from Ariane 6 GTO injection ---
nominal_state_GTO = {
    "SMA" : 24396,                                                                          # [km]  semi-major axis
    "ECC" : 0.7283,                                                                         # [ ]   eccentricity
    "INC" : 6,                                                                              # [deg] inclination
    "RAAN": 20,                                                                             # [deg] RAAN
    "AOP" : 178,                                                                            # [deg] argument of periapsis
    "TA"  : 5                                                                               # [deg] true anomaly, assumption: near periapsis
}