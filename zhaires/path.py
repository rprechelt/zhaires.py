"""
Find the directory where simulations are stored.
"""
import os
import os.path as op


def get_run_directory() -> str:
    """
    Return the directory where Aires runs are stored.

    If AIRES_RUN_DIR is defined, use that. Otherwise,
    use the current directory

    Returns
    -------
    directory: str
        The directory to store ZHAireS simulations.
    """
    # the directory pointed to by the ENV VAR
    envdir = os.getenv("AIRES_RUN_DIR")

    # if it's defined, use that. Else the CWD.
    return envdir if envdir else "."


def exists(simname: str, directory: str = None) -> bool:
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

    # get the run directory
    run_directory = directory if directory else get_run_directory()

    # check if the simulation has already been start
    exists = op.exists(op.join(run_directory, *(simname, "Zhaires.status")))

    # and we are done
    return exists
