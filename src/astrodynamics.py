# =========================
#   Astrodynamics
# =========================

# This file contains the functions for astrodynamics purposes

from skyfield.api import EarthSatellite, load


def TLE_reader(file_TLE:str):

    '''Reads the TLE file and returns a list with
    the three lines.'''

    # Input: path to TLE file
    # Output: list of three lines

    lines = []
    with open(file_TLE, 'r') as file:
        for line in file:
            lines.append(line.strip())
    
    return lines

def IC_epoch(name:str, line1:str, line2:str, date:list):

    '''Takes TLE data and calculates the state (r,v) of the SC
    at the desired date.
    Calculation via skyfield api.'''

    # Input: TLE's line 0, line 1 and line 2; desired date (Y,M,D,h,m,s)
    # Output: position and velocity at date in J2000 RF 

    ts = load.timescale(builtin=True)                                      
    sat = EarthSatellite(line1, line2, name, ts)            # satellite definition

    year, month, day, hour, minute, sec = date
    t = ts.utc(year, month, day, hour, minute, sec)         # epoch time (UTC Julian Date)

    jd = t.ut1                                              # extraction of float (UTC Julian Date)
    
    geocentric = sat.at(t)

    # J2000 RF
    r = geocentric.position.km                              # [km]   position
    v = geocentric.velocity.km_per_s                        # [km/s] velocity

    return r, v, jd