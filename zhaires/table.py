"""
Generate and load Aires data tables.
"""
import os.path as op
import re
import subprocess

import numpy as np

from xarray.core.dataarray import DataArray

from .path import get_run_directory
from .utils import find_aires

__all__ = ["load_table", "generate_table"]


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

    # read the whole filena
    table_type = parse_table_type(filename)

    # load the raw data
    raw = np.loadtxt(filename)

    # parse the table type
    if table_type == "long":
        data = parse_longitudinal(raw)
    elif table_type == "lateral":
        data = parse_lateral(raw)
    elif table_type == "energy":
        data = parse_energy(raw)
    elif table_type == "ground":
        data = parse_ground(raw)
    else:
        raise ValueError(f"Unknown table type: {table_type}")

    # and set the units for each quantity
    data.attrs["units"] = {
        "depth": "g/cm^2",
        "length": "m",
        "time": "ns",
        "angle": "deg",
        "energy": "GeV",
    }

    # and return the constructed table
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
    exportcmd = find_aires(suffix="export")

    # construct the path to this simulation
    path = op.abspath(op.join(directory, sim))

    # create the subpro
    subprocess.run([exportcmd, path, str(table)])

    # the table was generated successfully - load it and return it to the user
    return load_table(sim, table, directory)


def parse_table_type(filename: str) -> str:
    """
    Parse the table type from a file.

    Parameters
    ----------
    filename: str
        The filename of a table.

    Returns
    -------
    table_type: str
        The type of this table.
    """

    # open the filename
    with open(filename, "r") as f:
        contents = f.read()[0:600]  # read the whole file and take 600

        # now match the contents of the line against regex

        if re.search(r"TABLE 5", contents):
            return "ground"
        if re.search(r"Longitudinal development: Energy", contents):
            return "energy"
        elif re.search(r"Longitudinal development:", contents):
            return "long"
        elif re.search(r"Lateral distribution:", contents):
            return "lateral"
        elif re.search(r"Unweighted lateral distribution:", contents):
            return "lateral"
        elif re.search(r"Energy distribution", contents):
            return "energy"
        elif re.search(r"Energy distribution", contents):
            return "energy"
        else:
            raise ValueError("Unknown table type.")


def parse_lateral(data: np.ndarray) -> DataArray:
    """
    Parse raw data into energy table.

    Parameters
    ----------
    data: np.ndarray
        The raw data for a energy table.

    Returns
    -------
    table: DataArray
        The created xarray.DataArray
    """
    # load the data table into an XArray
    table = DataArray(
        data[:, 1:],
        dims=["level", "quantity"],
        coords={
            "level": np.arange(data.shape[0]),
            "quantity": ["R", "mean", "rms", "stdev", "min", "max"],
        },
    )

    # and we are done
    return table


def parse_ground(data: np.ndarray) -> DataArray:
    """
    Parse raw data into ground table.

    Parameters
    ----------
    data: np.ndarray
        The raw data for a energy table.

    Returns
    -------
    table: DataArray
        The created xarray.DataArray
    """
    # load the data table into an XArray
    table = DataArray(
        data[1:],
        dims=["quantity"],
        coords={"quantity": ["number", "energy", "entries"]},
    )

    # and we are done
    return table


def parse_energy(data: np.ndarray) -> DataArray:
    """
    Parse raw data into energy table.

    Parameters
    ----------
    data: np.ndarray
        The raw data for a energy table.

    Returns
    -------
    table: DataArray
        The created xarray.DataArray
    """
    # load the data table into an XArray
    table = DataArray(
        data[:, 1:],
        dims=["level", "quantity"],
        coords={
            "level": np.arange(data.shape[0]),
            "quantity": ["energy", "mean", "rms", "stdev", "min", "max"],
        },
    )

    # and we are done
    return table


def parse_longitudinal(data: np.ndarray) -> DataArray:
    """
    Parse raw data into a longitudinal table.

    Parameters
    ----------
    data: np.ndarray
        The raw data for a longitudinal table.

    Returns
    -------
    table: DataArray
        The created xarray.DataArray
    """
    # load the data table into an XArray
    table = DataArray(
        data[:, 1:],
        dims=["level", "quantity"],
        coords={
            "level": np.arange(data.shape[0]),
            "quantity": ["depth", "mean", "rms", "stdev", "min", "max"],
        },
    )

    # and we are done
    return table
