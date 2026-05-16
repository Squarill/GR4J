from pathlib import Path as pt

class Paths():
    ROOT = pt(__file__).parent
    DATASET = ROOT / "Dataset"
    NetCDF = DATASET / "NetCDF"