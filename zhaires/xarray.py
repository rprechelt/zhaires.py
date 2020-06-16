"""
Load waveforms into XArray DataArray's and Datasets.
"""
import numpy as np
import xarray as xr

import zhaires.loader as loader

from .path import get_run_directory


def load_waveforms(
    sim: str, directory: str = get_run_directory(), write_netcdf: bool = True
) -> xr.Dataset:
    """
    Load the ZHAireS antenna signals from simulation with name `sim`
    in the directory `directory` into a DataArray.

    This assumes that there is only one shower per simulation file.

    if `write_cache` is True, the extracted waveforms are saved
    as a .npy file in the simulation directory. Whenever this simulation
    is loaded, the .npy file will be loaded directly instead of reloading
    and reparsing the giant text file. This is orders of magnitude faster
    when loading large simulations.

    Parameters
    ----------
    sim: str
        The Aires task name for the simulation.
    directory: str
        The directory to search for the simulation.
    write_netcdf: str
        If True, write a NetCDF file to speed up loading future data accesses.

    Returns
    -------
    waveforms: xr.DataArray
        A multi-dimensional data array containing the loaded waveforms.
    """

    # load the waveforms into a a structured NumPy array
    raw = loader.load_waveforms(sim, directory, write_cache=False)

    # load the properties dict for this simulation
    props = loader.load_properties(sim, directory)

    # the number of antennas
    nant = raw.shape[0]

    # number of polarizations
    npol = 3

    # and the length of each waveform
    length = raw["Ex"].shape[-1]

    # allocate the memory for the XArray
    data = np.zeros((nant, npol + 1, length))

    # fill in the data
    data[..., 0, :] = raw["Ex"]
    data[..., 1, :] = raw["Ey"]
    data[..., 2, :] = raw["Ez"]
    data[..., 3, :] = raw["t"]

    # create the data array
    waveforms = xr.DataArray(
        data,
        dims=["nant", "pol", "length"],
        coords={
            "nant": np.arange(nant),
            "pol": ["Ex", "Ey", "Ez", "t"],
            "length": np.arange(length),
        },
    )

    # the antenna locations
    antennas = np.zeros((nant, 3))
    antennas[:, 0] = raw["x"]
    antennas[:, 1] = raw["y"]
    antennas[:, 2] = raw["z"]

    # construct the data array for the locations
    locations = xr.DataArray(
        antennas,
        dims=["nant", "axis"],
        coords={"nant": np.arange(nant), "axis": ["x", "y", "z"]},
    )

    # construct the dataset
    dataset = xr.Dataset({"waveforms": waveforms, "locations": locations})

    # and save the simulation name and directory
    dataset.attrs["name"] = sim
    dataset.attrs["directory"] = directory

    # and save the properties into the array
    for k, v in props.items():
        dataset.attrs[k] = v

    # and return the created dataset
    return dataset