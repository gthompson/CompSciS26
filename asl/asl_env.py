 # --- Imports & paths ---
from pathlib import Path
from obspy import read_inventory, UTCDateTime
from flovopy.research.mvo.mvo_ids import REGION_DEFAULT, DOME_LOCATION

import platform

# Detect OS and set data root
os_name = platform.system()

if os_name == "Windows":
    DATA_ROOT = Path("Z:/")
elif os_name == "Darwin":  # macOS
    DATA_ROOT = Path("/Volumes/classdata/")
elif os_name == "Linux":
    DATA_ROOT = Path("/mnt/classdata/")
else:
    raise RuntimeError(f"Unsupported OS: {os_name}")

# directories
HOME = Path.home()
#DROPBOXDIR = Path('~').expanduser() / 'Dropbox'
#PROJECTDIR = DROPBOXDIR / "BRIEFCASE" / "SSADenver"
#LOCALPROJECTDIR = HOME / "work" / "PROJECTS" / "SSADenver_local"
PROJECTDIR = Path('~').expanduser() / 'compsci_asl'
PROJECTDIR.mkdir(parents=False, exist_ok=True)
#METADATA_DIR    = PROJECTDIR / "metadata" 

thisDir = Path().resolve()
METADATA_DIR = thisDir / "metadata"

# master files
INVENTORY_XML   = METADATA_DIR / "MV_Seismic_and_GPS_stations.xml"
DEM_DEFAULT     = METADATA_DIR / "MONTSERRAT_DEM_WGS84_MASTER.tif"
GRIDFILE_DEFAULT= METADATA_DIR / "MASTER_GRID_MONTSERRAT.pkl"

# Load inventory
INV = read_inventory(INVENTORY_XML)

# I/O
INPUT_DIR = DATA_ROOT / "ASL_inputs" 
EVENT_DIR = INPUT_DIR  / "biggest_pdc_events"
STATION_CORRECTIONS_DIR = INPUT_DIR / "station_correction_analysis"
#DIST_MODE = "3d"        # include elevation
GLOBAL_CACHE = PROJECTDIR / "asl_global_cache"
OUTPUT_DIR = PROJECTDIR / "ASL_RESULTS"
#OUTPUT_DIR = GLOBAL_CACHE
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

#RUN_TAG = UTCDateTime().strftime("topo_map_test_%Y%m%dT%H%M%S")
#RUNDIR = Path(OUTPUT_DIR) / RUN_TAG
##RUNDIR.mkdir(parents=True, exist_ok=True)