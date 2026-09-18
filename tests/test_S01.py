# Tests for scenario S01 - Mission Analysis

import pytest
import numpy as np

from src.astrodynamics import *
from S01_mission_analysis.initial_state_from_TLE import *

# ------------------------------------------------------------
# Tests for set_filename
# ------------------------------------------------------------

def test_setfilename():

    # Basic test for the function

    line0 = "STARLINK-3325 (SPACEX)"
    gmat_epoch = '33100.7000'

    filename_expected = "STARLINK_3325_SPACEX_33100.script"
    filename = set_name(line0, gmat_epoch)

    assert filename == filename_expected

@pytest.mark.parametrize("bad_char", ["&", "!", "#", "/", "@"])
def test_invalidfilename(bad_char):

    # Parametrized test for invalid file names

    line0 = f"EUTELSAT {bad_char} ESA 5500"
    gmat_epoch = '33110.0000'

    with pytest.raises(ValueError):
        set_name(line0, gmat_epoch)