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
from .loader import load_waveforms, load_properties

def exists(simname: str, directory: str = run_directory) -> bool:
    """
    Return True if `simname` already exists in `directory`.

    Parameters
    ----------
    simname: str
        The name of the simulation.
    directory: str
        The run directory to check.

    Returns
    -------
    exists: bool
        Return True if `simname` already exists.
    """

    # check if the simulation has already been start
    exists = os.path.exists(join(directory, *(simname, 'Zhaires.status')))

    # and we are done
    return exists
