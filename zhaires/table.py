"""
Generate and load Aires data tables.
"""
import subprocess
import os.path as op
import numpy as np
from .path import get_run_directory
from .utils import find_aires
from xarray.core.dataarray import DataArray


def load_table(sim: str, table: int, directory: str = get_run_directory()) -> DataArray:
    """
    Generate the table with ID `table` for the simulation `sim`
    stored in the given `directory` and load it.

    Parameters
    ----------
    sim: str
        The name of the simulation to generate.
    table: int
        The ID of the table to generate.
    directory: str
        The directory where simulation is stored.

    Returns
    -------
    table: np.ndarray
        The data table as a NumPy structured array.

    Raises
    ------
    ValueError:
        If the table was not successfully generated.
    """

    # construct the filename of the table
    filename = op.abspath(op.join(directory, sim, f"{sim}.t{table}"))

    # check that the table now exists
    if not op.exists(filename):
        raise ValueError(f"Unable to load t{table} for {filename}")

    # load the raw data
    raw = np.loadtxt(filename)

    # load the data table into an XArray
    data = DataArray(
        raw[:, 1:],
        dims=["level", "quantity"],
        coords={
            "level": np.arange(raw.shape[0]),
            "quantity": ["depth", "mean", "rms", "stdev", "min", "max"],
        },
    )

    # and set the units for each quantity
    data.attrs["units"] = {
        "depth": "g/cm^2",
        "length": "m",
        "time": "ns",
        "angle": "deg",
        "energy": "GeV",
    }

    # and we are done
    return data


def generate_table(
    sim: str, table: int, directory: str = get_run_directory()
) -> DataArray:
    """
    Generate the table with ID `table` for the simulation `sim`
    stored in the given `directory` and load it.

    Parameters
    ----------
    sim: str
        The name of the simulation to generate.
    table: int
        The ID of the table to generate.
    directory: str
        The directory where simulation is stored.

    Returns
    -------
    table: np.ndarray
        The data table as a NumPy structured array.

    Raises
    ------
    ValueError:
        If the table was not successfully generated.
    """

    # find the AiresExport command
    exportcmd = find_aires("Export")

    # construct the path to this simulation
    path = op.abspath(op.join(directory, sim))

    # create the subpro
    subprocess.run([exportcmd, path, str(table)])

    # the table was generated successfully - load it and return it to the user
    return load_table(sim, table, directory)
