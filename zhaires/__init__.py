import os

# the current version
__version__ = "0.1.0"

# the directory where we store runs
run_directory = os.getenv("AIRES_RUN_DIR")

# check that the right environment variable is defined
if not run_directory:
    raise ValueError(f"AIRES_RUN_DIR is not defined. Please defined AIRES_RUN_DIR.")

# these modules may depend on run_directory
from .aires import Task
from .loader import load_waveforms
