# GMAT-Scenarios

Flight dynamics scenarios simulated with NASA's [GMAT](https://software.nasa.gov/software/GSC-17177-1), with Python used for initial-state generation and data analysis.

Each scenario is self-contained: a GMAT script, the analysis code and a README with assumptions, results and discussion.

## Scenarios

| # | Scenario | Topic | Status |
|---|---|---|---|
| 01 | [Mission analysis](S01_mission_analysis) | TLE propagation, ground station contacts and eclipses | Done |
| 02 | LEOP | First contact after injection, orbit determination | Planned |
| 03 | Orbit raising | GTO to GEO | Planned |
| 04 | Station keeping | GEO/LEO maintenance | Planned |
| 05 | Rendezvous | Phasing and proximity operations | Planned |


## Repository layout

```
src/        shared code (astrodynamics, data analysis)
tests/      unit tests (pytest)
01_mission_analysis/
...
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
pytest tests/ -v
```

GMAT is required to run the scripts (tested with GMAT R2026a). Generated scripts contain machine-specific absolute paths, so they are not versioned: each scenario README explains how to regenerate them.
