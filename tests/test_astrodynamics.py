# Test for astrodynamics functions

import pytest
import numpy as np

from src.astrodynamics import *

# --------------------------------- 
#   TLE reader tests 
# --------------------------------- 

def test_readTLE():

    # Test for the TLE_reader function
    # Test for n. of lines and length

    file_TLE = r"./tests/TLE_test.txt"

    lines = TLE_reader(file_TLE)

    assert len(lines) == 3,                     "Expected 3 lines, got {len(lines)}"
    assert lines[1].strip().startswith("1"),    "Line 1 must start with '1'"
    assert lines[2].strip().startswith("2"),    "Line 2 must start with '2'"
    assert len(lines[1]) == 69,                 f"Line 1 must be 69 characters long, got {len(lines[1])}"
    assert len(lines[2]) == 69,                 f"Line 2 must be 69 characters long, got {len(lines[2])}"


def test_TLE_reader_file_not_found():
    
    # Test for a TLE file that does not exist
     
    with pytest.raises(FileNotFoundError):
        TLE_reader("TLE_fake.txt")

# --------------------------------- 
#   IC_epoch tests 
# --------------------------------- 

def test_IC_epoch_physical_sanity():

    # Test that position and velocity have a plausible magnitude 

    line0 = "ISS (ZARYA)"
    line1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9994"
    line2 = "2 25544  51.6400 337.6640 0007610  92.9057  25.0641 15.49560629 12345"
    date = [2026, 1, 1, 12, 0, 0]

    r, v, jd = IC_epoch(line0, line1, line2, date)

    r_mag = (r[0]**2 + r[1]**2 + r[2]**2) ** 0.5                                        # radius magnitude
    v_mag = (v[0]**2 + v[1]**2 + v[2]**2) ** 0.5                                        # velocity magnitude

    # For ISS r ~ 6800 km (6378 + 450~500 km)
    assert 6700 < r_mag < 6900, f"Raggio orbitale non plausibile: {r_mag} km"

    # Orbital velocity in LEO: ~7.5-7.7 km/s
    assert 7.4 < v_mag < 7.8, f"Velocità non plausibile: {v_mag} km/s"

    # Julian Date for 2026
    assert 2461041 < jd < 2461406

def test_IC_epoch_regression():

    # Regression test: manual validated data

    line0 = "ISS (ZARYA)"
    line1 = "1 25544U 98067A   26259.85263506  .00007068  00000+0  13566-3 0  9993"
    line2 = "2 25544  51.6307 206.4210 0004838 147.2470 212.8820 15.49143506585961"
    date = [2026, 9, 19, 12, 0, 0]

    r, v, jd = IC_epoch(line0, line1, line2, date)

    # Reference values
    r_expected = [-6192.30930154, -2481.54782412, 1313.20888458]
    v_expected = [2.87501269, -4.06944814, 5.81668988]

    assert r[0] == pytest.approx(r_expected[0], rel=1e-6)
    assert r[1] == pytest.approx(r_expected[1], rel=1e-6)
    assert r[2] == pytest.approx(r_expected[2], rel=1e-6)

    assert v[0] == pytest.approx(v_expected[0], rel=1e-6)
    assert v[1] == pytest.approx(v_expected[1], rel=1e-6)
    assert v[2] == pytest.approx(v_expected[2], rel=1e-6)