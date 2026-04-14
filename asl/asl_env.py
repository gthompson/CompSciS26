 # --- Imports & paths ---
from pathlib import Path
from obspy import read_inventory, UTCDateTime
from flovopy.research.mvo.mvo_ids import REGION_DEFAULT, DOME_LOCATION

# directories
HOME = Path.home()
DROPBOXDIR = Path('~').expanduser() / 'Dropbox'
PROJECTDIR = DROPBOXDIR / "BRIEFCASE" / "SSADenver"
LOCALPROJECTDIR = HOME / "work" / "PROJECTS" / "SSADenver_local"
METADATA_DIR    = PROJECTDIR / "metadata" 
STATION_CORRECTIONS_DIR = PROJECTDIR / "station_correction_analysis"

# master files
INVENTORY_XML   = METADATA_DIR / "MV_Seismic_and_GPS_stations.xml"
DEM_DEFAULT     = METADATA_DIR / "MONTSERRAT_DEM_WGS84_MASTER.tif"
GRIDFILE_DEFAULT= METADATA_DIR / "MASTER_GRID_MONTSERRAT.pkl"

# Load inventory
INV = read_inventory(INVENTORY_XML)

# I/O
INPUT_DIR = PROJECTDIR / "ASL_inputs" / "biggest_pdc_events"
DIST_MODE = "3d"        # include elevation
GLOBAL_CACHE = PROJECTDIR / "asl_global_cache"
RUN_TAG = UTCDateTime().strftime("topo_map_test_%Y%m%dT%H%M%S")
OUTPUT_DIR      = LOCALPROJECTDIR / "ASL_RESULTS"
OUTPUT_DIR = GLOBAL_CACHE
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTDIR = Path(OUTPUT_DIR) / RUN_TAG
OUTDIR.mkdir(parents=True, exist_ok=True)