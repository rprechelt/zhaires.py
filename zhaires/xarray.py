"""
Load waveforms into XArray DataArray's and Datasets.
"""
import os.path as op
from typing import Optional, Any, Tuple

import numpy as np

import xarray as xr
import zhaires.loader as loader
from xarray import Dataset

from .path import get_run_directory


def trim_dataset(sim: Dataset, trim: Tuple[float, float]) -> Dataset:
    """
    Trim the waveforms in a dataset to a region around the peak.

    `trim` is a tuple of times, (before, after), in nanoseconds.
    The waveforms will be trimmed to `before` ns prior to the peak
    and `after` nanoseconds after the absolute valued peak.
    The total length of the trimmed waveforms will be `before+after` ns.

    If there is not enough of the waveforms to fill `before+after`,
    the final waveforms will be zero padded.

    Parameters
    ----------
    sim: XArray Dataset
        The Dataset containing ZHAires waveforms.
    trim: (float, float)
        The time before and after the peak to save.

    Returns
    -------
    Dataset
        The trimmed waveforms.

    """

    # find the location of the peak in each simulation
    ipeak = sim.waveforms.max(dim="pol").argmax(dim="time")

    # construct the minimum and maximum indices
    imin = ipeak - int(round(trim[0] / sim.waveforms.attrs["dt"]))
    imax = ipeak + int(round(trim[1] / sim.waveforms.attrs["dt"]))

    # and make sure they are clipped to the right range
    imin = imin.clip(0, sim.time.size)
    imax = imax.clip(0, sim.time.size)

    # the total number of samples we are extracting
    N = int(round((trim[1] - trim[0]) / sim.waveforms.attrs["dt"]))

    # create a zeroed out array of the right size
    new = sim.isel(time=slice(0, N))


def resample_waveforms(sim: Dataset, fs: float, method: str = "cubic") -> Dataset:
    """
    Resample the waveforms to a given sample rate
    using interpolation.

    This uses interpolation so may have poor accuracy if the new
    sampling rate is vastly different from the input sampling rate.

    Parameters
    ----------
    sim: XArray Dataset
        The Dataset containing the waveforms.
    fs: float
        The sample rate (in units of GSa/s) to resample to.
    method: str, default is "cubic"
        The interpolation method to use.
        ["linear", "slinear", "quadratic", "cubic"]

    Parameters
    ----------
    Dataset
        The waveforms resampled to `fs` GSa/s.
    """

    # get the current sampling rate
    curr_fs = 1.0 / sim.waveforms.attrs["dt"]

    # if the sample rate is the same as the requested sample rate,
    # then we just return
    if np.abs(curr_fs - fs) < 1e-9:
        return sim

    # otherwise, construct the times that we interpolate onto
    new_times = np.arange(0, sim.time.size) * (1.0 / fs)

    # and perform the interpolation
    return sim.interp(time=new_times)


def load_waveforms(
    sim: str,
    directory: str = get_run_directory(),
    write_netcdf: bool = True,
    resample: Optional[float] = None,
    trim: Optional[Tuple[float, float]] = None,
    **kwargs: Any,
) -> Dataset:
    """
    Load the ZHAireS antenna signals from simulation with name `sim`
    in the directory `directory` into a DataArray.

    This assumes that there is only one shower per simulation file.

    if `write_cache` is True, the extracted waveforms are saved
    as a .nc file in the simulation directory. Whenever this simulation
    is loaded, the .nc file will be loaded directly instead of reloading
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
    resample: float, optional
        If not None, resample the waveforms to this sample rate in GSa/s.
    trim: (float, float), optional
        If not None, trim the waveform to (before, after) ns after the peak in the absolute value.
    **kwargs:
        Any additional arguments are passed to 'resample_waveforms'

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

    # compute the sampling period
    dt = raw["t"][0, 1] - raw["t"][0, 0]

    # allocate the memory for the XArray
    data = np.zeros((nant, npol, length))

    # fill in the data
    data[..., 0, :] = raw["Ex"]
    data[..., 1, :] = raw["Ey"]
    data[..., 2, :] = raw["Ez"]

    # create the data array
    waveforms = xr.DataArray(
        data,
        dims=["nant", "pol", "time"],
        coords={
            "nant": np.arange(nant),
            "pol": ["Ex", "Ey", "Ez"],
            "time": np.arange(length) * dt,
        },
    )

    # set the units (and sampling period) for the waveforms
    waveforms.attrs["units"] = "V/m"
    waveforms.attrs["dt"] = dt
    waveforms.time.attrs["units"] = "ns"

    # the antenna locations
    antennas = np.zeros((nant, 4))
    antennas[:, 0] = raw["x"]
    antennas[:, 1] = raw["y"]
    antennas[:, 2] = raw["z"]
    antennas[:, 3] = raw["t"][:, 0]  # the start time for each waveform

    # construct the data array for the locations
    locations = xr.DataArray(
        antennas,
        dims=["nant", "axis"],
        coords={"nant": np.arange(nant), "axis": ["x", "y", "z", "t0"]},
    )

    # set the unit for the locations
    locations.attrs["units"] = "m | ns"

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

        # and set the units for the angle array
        angles.attrs["units"] = "deg | m"

        # and add it to the data array
        dataset = Dataset(
            {"waveforms": waveforms, "locations": locations, "angles": angles}
        )

    else:  # we don't have an antenna angle file
        # construct the dataset without the angles
        dataset = Dataset({"waveforms": waveforms, "locations": locations})

    # and save the simulation name and directory
    dataset.attrs["name"] = sim
    dataset.attrs["directory"] = directory

    # and save the properties into the array
    for k, v in props.items():
        dataset.attrs[k] = v

    # check if we want to resample
    if resample is not None:
        dataset = resample_waveforms(dataset, resample, **kwargs)

    # check if we want to trim the waveforms
    if trim:
        dataset = trim_dataset(dataset, trim)

    # if we want to write the cache, then write it to disk
    if write_netcdf:
        dataset.to_netcdf(path=cachefile, mode="w", format="NETCDF4")

    # and return the created dataset
    return dataset
