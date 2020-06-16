"""
Load waveforms into XArray DataArray's and Datasets.
"""
import os.path as op

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

    # the path to the cache file
    cachefile = op.join(directory, *(sim, f"{sim}.nc"))

    # if the cache file exists, load it.
    if op.exists(cachefile):
        return xr.open_dataset(cachefile)

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

    # the filename for the antenna files (if they exist)
    antfile = op.join(directory, *(sim, "antenna_angles.dat"))

    # if it exists, load it
    if op.exists(antfile):
        # load the raw data
        raw_angles = np.loadtxt(antfile)

        # and construct the data array
        angles = xr.DataArray(
            raw_angles[:, (3, 4, 5)],
            dims=["nant", "coord"],
            coords={"nant": np.arange(nant), "coord": ["theta", "phi", "D"]},
        )

        # and add it to the data array
        dataset = xr.Dataset(
            {"waveforms": waveforms, "locations": locations, "angles": angles}
        )

    else:  # we don't have an antenna angle file
        # construct the dataset without the angles
        dataset = xr.Dataset({"waveforms": waveforms, "locations": locations})

    # and save the simulation name and directory
    dataset.attrs["name"] = sim
    dataset.attrs["directory"] = directory

    # and save the properties into the array
    for k, v in props.items():
        dataset.attrs[k] = v

    # if we want to write the cache, then write it to disk
    if write_netcdf:
        dataset.to_netcdf(path=cachefile, mode="w", format="NETCDF4")

    # and return the created dataset
    return dataset
