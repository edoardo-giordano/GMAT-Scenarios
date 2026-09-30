# Script generator for S02 - LEOP

import os
from pathlib import Path
from src.script_tools import *
from src.astrodynamics import jd_from_date
from S02_LEOP.leop_config import epoch, stations, nominal_state_GTO

# GS dictionary
# note: lat in [-90, 90] deg
#       lon in [0, 360] deg
# ground_stations = {
#     # "Burum":     {"lat": 53.271, "lon": 6.212,  "alt": 0.001, "min_elevation": 5},
#     "Betzdirf": {"lat": 49.688, "lon": 6.350, "alt": 0.320, "min_elevation": 5},
#     "Fucino":   {"lat": 41.9766, "lon": 13.6029, "alt": 0.650, "min_elevation": 5},
#     "Perth": {"lat": -31.802, "lon": 115.885, "alt": 0.022, "min_elevation": 5},
#     "Paumalu": {"lat": 21.670, "lon": 201.967, "alt": 0.16, "min_elevation": 5}
# }

# Nominal state for a GTO (Ariane 6)
# RAAN is chosen
# TA is assumed low, injection near periapsis

# nominal_state_GTO = {
#     "SMA" : 24396,                                                                          # [km]  semi-major axis
#     "ECC" : 0.7283,                                                                         # [ ]   eccentricity
#     "INC" : 6,                                                                              # [deg] inclination
#     "RAAN": 20,                                                                             # [deg] RAAN
#     "AOP" : 178,                                                                            # [deg] argument of periapsis
#     "TA"  : 5                                                                               # [deg] true anomaly
# }

def gen_script(state0, start_date, ground_stations, template_path, output_script_path):
    '''This function generates a GMAT script ready to be run in the GUI'''


    #### ---- Epoch

    t0 = jd_from_date(start_date)
    mt0_GMAT_str = f"{t0 - 2430000.0:.10f}"                      # Modified JD (epoch 5  January  1941) --> for GMAT

    #### ----- Set the output path
    
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(repo_root, "S02_LEOP", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    contact_output_path = os.path.join(output_dir, "ContactLocator.txt")
    eclipse_output_path = os.path.join(output_dir, "EclipseLocator.txt")

    # Set the file name

    filename = "GTO_" + str(int(float(mt0_GMAT_str))) + ".script"
    output_script_path = output_script_path + filename

    #### ----- Find and replace the placeholder in the gmat template 

    template = Path(template_path).read_text()
    
    gs_block, observers_list = build_all_ground_stations(ground_stations)
    observers_list_GT = observers_list.rstrip("}") + ", MySat}"
    
    filled = (
        template
        .replace("{{EPOCH}}", mt0_GMAT_str)
        .replace("{{SMA}}", repr(float(state0["SMA"])))
        .replace("{{ECC}}", repr(float(state0["ECC"])))
        .replace("{{INC}}", repr(float(state0["INC"])))
        .replace("{{RAAN}}", repr(float(state0["RAAN"])))
        .replace("{{AOP}}", repr(float(state0["AOP"])))
        .replace("{{TA}}", repr(float(state0["TA"])))
        .replace("{{ECLIPSE_OUTPUT}}", repr(eclipse_output_path))
        .replace("{{CONTACT_OUTPUT}}", repr(contact_output_path))
        .replace("{{GROUND_STATIONS}}", gs_block)
        .replace("{{OBSERVERS_LIST}}", observers_list)
        .replace("{{OBSERVERS_LIST_GT}}", observers_list_GT)
    )
    
    Path(output_script_path).write_text(filled)

    
if __name__ == "__main__":
    gen_script(
        state0 = nominal_state_GTO,
        start_date=epoch,
        ground_stations=stations,
        template_path=r"./S02_LEOP/gmat_files/leop_template.script",
        output_script_path="./S02_LEOP/gmat_files/generated/"
    )