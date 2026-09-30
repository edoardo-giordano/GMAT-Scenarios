# Scenario 2 - LEOP

First contact data analyser.

## Objective

Given a real nominal state (e.g. from Ariane 6 launcher):
- Define a GMAT script with the selected initial state, epoch and ground stations
- Perform data analysis concerning the first contact


## How to reproduce

1. **Set the GS, epoch and nominal state**: in `leop_config.py`, considering the ground stations in `../src/ground_stations.py`.
2. **Generate the GMAT script**:
   ```bash
   python -m S02_LEOP.gen_leop_script
   ```
   The script is written to `gmat_files/generated/`, with absolute output paths pointing to this project's `output/` folder. Generated scripts contain machine-specific paths and are not committed. 
3. **Run the script in GMAT** (GUI): open the generated `.script` and run. GMAT writes `ContactLocator.txt` and `EclipseLocator.txt` in `output/`.
4. **Analyse the results**:
   ```bash
   python -m S02_LEOP.analyse_results_LEOP.py
   ```