import os
import re
from typing import Mapping

import numpy as np

from .path import get_run_directory

__all__ = ["load_properties", "load_waveforms"]


def load_waveforms(
    sim: str, directory: str = get_run_directory(), write_cache: bool = True
) -> np.ndarray:
    """
    Load the ZHAireS antenna signals from the simulation with name `sim`
    in the directory `directory`.

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

    Returns
    -------
    waveforms: np.ndarray
        A structured array containing the waveforms and antenna information.
    """

    # the filename to save into
    cachefile = os.path.join(directory, *(sim, "waveforms.npy"))

    # if the cachefile exists
    if os.path.exists(cachefile):
        return np.load(cachefile)

    # load in the appropriate file using numpy
    raw = np.loadtxt(os.path.join(directory, *(sim, "timefresnel-root.dat"))).T

    # extract the number of antennas
    nantennas = int(raw[1, -1])  # this is the last entry in the antenna number column.

    # the length of each signal - we overestimate
    length = int(np.ceil(raw.shape[1] / nantennas))

    # create the data to store the waveforms
    data = np.zeros(
        nantennas,
        dtype=[
            ("energy", "float32"),
            ("zenith", "float32"),
            ("azimuth", "float32"),
            ("lat", "float32"),
            ("lon", "float32"),
            ("ground", "float32"),
            ("mag_str", "float32"),
            ("mag_inc", "float32"),
            ("mag_dec", "float32"),
            ("x", "float32"),
            ("y", "float32"),
            ("z", "float32"),
            ("t", "float32", length),
            ("Ex", "float32", length),
            ("Ey", "float32", length),
            ("Ez", "float32", length),
        ],
    )

    # load the properties dict for this simulation
    props = load_properties(sim, directory)

    # loop over the number of antennas
    for iant in np.arange(0, nantennas):

        # get the indices of the values corresponding to this antenna
        antidx = raw[1, :] == (iant + 1)

        # fill in the property information
        for key in [
            "energy",
            "zenith",
            "azimuth",
            "lat",
            "lon",
            "ground",
            "mag_str",
            "mag_inc",
            "mag_dec",
        ]:
            data[iant][key] = props[key]

        # fill in the position and time
        data[iant]["x"] = raw[2, antidx][0]
        data[iant]["y"] = raw[3, antidx][0]
        data[iant]["z"] = raw[4, antidx][0]
        data[iant]["t"] = __pad_or_cut(raw[5, antidx], length)

        # and fill in the field vectors
        data[iant]["Ex"] = __pad_or_cut(raw[11, antidx], length)
        data[iant]["Ey"] = __pad_or_cut(raw[12, antidx], length)
        data[iant]["Ez"] = __pad_or_cut(raw[13, antidx], length)

    # now that we have the array, write the cache if desired
    if write_cache:
        np.save(cachefile, data)

    # and we are done.
    return data


def load_properties(
    sim: str, directory: str = get_run_directory()
) -> Mapping[str, float]:
    """
    Load the various properties of the simulation into a dictionary.

    Parameters
    ----------
    sim: str
        The name of the simulation to load.
    directory: str
        The directory to load the simulation from.

    Returns
    -------
    properties: Dict
        The various properties of the simulation loaded from the ZHAireS file.
    """

    # create the dictionary to store the various properties
    props = {}

    # a function to parse the ZHAireS energy
    def parse_energy(energy: float, unit: str) -> float:
        """
        Parse an energy of the form "* *eV" into EeV.
        """
        if unit == "PeV":
            exponent = 15
        elif unit == "EeV":
            exponent = 18
        elif unit == "ZeV":
            exponent = 21

        return energy * np.power(10.0, exponent - 18)

    # open the file
    with open(os.path.join(directory, *(sim, f"{sim}.sry"))) as f:

        # loop through the lines in a file
        for line in f:

            # match for the primary energy
            energy_match = re.search(
                r"\s*Primary energy: (\d+.\d+) ([a-zA-Z]{3})", line
            )

            # if we got a match
            if energy_match:
                props["energy"] = parse_energy(
                    float(energy_match.group(1)), energy_match.group(2)
                )

            # match for the primary particle
            particle_match = re.search(r"\s*Primary particle: ([a-zA-Z]*)", line)

            # if we got a match
            if particle_match:
                props["particle"] = particle_match.group(1).lower()  # type: ignore

            # and match for primary zenith
            zenith_match = re.search(r"\s*Primary zenith angle:\s*(\d+.\d+)", line)

            # check for the zenith match
            if zenith_match:
                props["zenith"] = float(zenith_match.group(1))

            # and match for primary azimuth
            azimuth_match = re.search(r"\s*Primary azimuth angle:\s*(-?\d+.\d+)", line)

            # check for the azimuth match
            if azimuth_match:
                props["azimuth"] = float(azimuth_match.group(1))

            # and match for primary azimuth
            lat_lon_match = re.search(
                r"\s*\(Lat:\s*(-?\d+.\d+)\s*deg.\s*Long:\s*(-?\d+.\d+)", line
            )

            # check for the azimuth match
            if lat_lon_match:
                props["lat"] = float(lat_lon_match.group(1))
                props["lon"] = float(lat_lon_match.group(2))

            # and match for primary ground
            ground_match = re.search(r"\s*Ground altitude:\s*(\d+.\d+)", line)

            # check for the ground match
            if ground_match:
                props["ground"] = float(ground_match.group(1))

            # and match for primary injection
            injection_match = re.search(r"\s*Injection altitude:\s*(\d+.\d+)", line)

            # check for the injection match
            if injection_match:
                props["injection"] = float(injection_match.group(1))

            # and extract the magnetic intensity
            intensity_match = re.search(r"Intensity:\s*(\d+.\d+) uT", line)

            # check for an intensity match
            if intensity_match:
                props["mag_str"] = float(intensity_match.group(1))

            # and extract the magnetic mag_inc
            mag_inc_match = re.search(r"\s*I:\s*(-?\d+.\d+) deg", line)

            # check for an mag_inc match
            if mag_inc_match:
                props["mag_inc"] = float(mag_inc_match.group(1))

            # and extract the magnetic mag_dec
            mag_dec_match = re.search(r"D:\s*(\d+.\d+) deg", line)

            # check for an mag_dec match
            if mag_dec_match:
                props["mag_dec"] = float(mag_dec_match.group(1))

            # and extract the time bin size
            dt_match = re.search(r"\s*Time bin size:\s*(-?\d+.\d+)ns", line)

            # and check for a time_bin_size match
            if dt_match:
                props["dt"] = float(dt_match.group(1))

            # and extract the index of refraction at sea level
            rindex_match = re.search(
                r"\s*Refraction index at sea level:(-?\d+.\d+)", line
            )

            # and check for a refractive index match
            if rindex_match:
                props["rindex"] = float(rindex_match.group(1))

            # and extract the thinning
            thinning_match = re.search(r"\s*Thinning energy:\s*(\d+.\d+E-?\d+)", line)

            # and check for a thinning match
            if thinning_match:
                props["thinning"] = float(thinning_match.group(1))

            # and extract the Xmax
            xmax_match = re.search(r"\s*Sl. depth of max. \(g/cm2\):\s*(\d+.\d+)", line)

            # and check for an xmax match
            if xmax_match:
                props["xmax"] = float(xmax_match.group(1))

    # and return the properties dict
    return props


def __pad_or_cut(arr: np.ndarray, length: np.ndarray) -> np.ndarray:
    """
    Given an array `arr` and a desired length `length`, either
    pad the array with zeros or cut it so that `arr` has the
    right length.

    Parameters
    ----------
    arr: np.ndarray
        The input array.
    length: int
        The desired length of the array.

    Returns
    -------
    cut: np.ndarray
        The array `arr` cut/padded to be of length `length`.
    """
    if arr.size < length:
        return np.pad(arr, (0, length - arr.size), mode="constant")
    else:
        return arr[0:length]
