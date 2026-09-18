# Script to initialise the state of a SC from TLE

from pathlib import Path
from src.astrodynamics import TLE_reader, IC_epoch


def generate_script_from_tle(tle_file, template_path, output_script_path, start_date):
    """
    This function:
    - reads a TLE file (.txt)
    - calculates the initial state (in J2000 RF) in cardinal coordinates
    - produces a GMAT script ready to use, based on a simple mission template

    To be used to set the script that has to be launched in GMAT 
    """
    # Read TLE, find initial state and epoch

    line0, line1, line2 = TLE_reader(tle_file)
    r0, v0, t0 = IC_epoch(line0, line1, line2, start_date)

    mt0_GMAT_str = f"{t0 - 2430000.0:.10f}"                      # Modified JD (epoch 5  January  1941) --> for GMAT

    template = Path(template_path).read_text()

    filename = set_name(line0, mt0_GMAT_str)

    output_script_path = output_script_path + filename


    # Find and replace the placeholder in the gmat template 

    filled = (
        template
        .replace("{{EPOCH}}", mt0_GMAT_str)
        .replace("{{X}}", repr(float(r0[0])))
        .replace("{{Y}}", repr(float(r0[1])))
        .replace("{{Z}}", repr(float(r0[2])))
        .replace("{{VX}}", repr(float(v0[0])))
        .replace("{{VY}}", repr(float(v0[1])))
        .replace("{{VZ}}", repr(float(v0[2])))
    )

    Path(output_script_path).write_text(filled)

    # Print the output 

    sd = start_date

    print(f"\nSatellite name: {line0}")
    print(f"\nSelected epoch (UTCGregorian): {sd[2]}-{sd[1]}-{sd[0]} @ {sd[3]}:{sd[4]}:{sd[5]}")
    print(f"GMAT epoch (UTCModJulian): {mt0_GMAT_str}")
    print(f"\nInitial state (J2000 RF):")
    print(f"  X = {r0[0]: .12f}      [km]\n  Y = {r0[1]: .12f}      [km]\n  Z = {r0[2]: .12f}      [km]\n")
    print(f"  VX = {v0[0]: .12f}      [km/s]\n  VY = {v0[1]: .12f}      [km/s]\n  VZ = {v0[2]: .12f}      [km/s]")
    print(f"\nGenerated script: {output_script_path}")

def set_name(line0:str, epoch:str):
    '''Set the name of the .script file based on TLE's line 0
    Format: name_of_satellite + gmat_epoch (integer) + .script'''

    filename = line0.replace(" ", "")
    filename = filename.replace("(", "_")
    filename = filename.replace(")","_")
    filename = filename.replace("-","_")
    filename = filename + f"{int(float(epoch))}"

    if not all(char.isalnum() or char == "_" for char in filename):
        raise ValueError(f"Invalid file name: {filename}")

    return filename + ".script"


if __name__ == "__main__":
    generate_script_from_tle(
        tle_file="./S01_mission_analysis/TLE_file.txt",
        template_path="./S01_mission_analysis/gmat_files/mission_template.script",
        output_script_path="./S01_mission_analysis/gmat_files/",
        start_date=[2026, 9, 19, 12, 0, 0],
    )