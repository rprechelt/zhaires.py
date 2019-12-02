# zhaires.py
A Python wrapper for the AireS and ZHAireS cosmic ray air shower simulation codes.

[![Actions Status](https://github.com/rprechelt/zhaires.py/workflows/tests/badge.svg)](https://github.com/rprechelt/zhaires.py/actions)
![GitHub](https://img.shields.io/github/license/rprechelt/zhaires.py?logoColor=brightgreen)
![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue)

ZHAireS.py is a Python wrapper around the AireS and ZHAireS cosmic ray air shower simulation codes. This allows for creating AireS simulations directly from Python, and importing AireS data files back into Python for data analysis.

Note: this package does not include a copy of AireS. You will need to download and install a working copy of AireS separately (so that `Aires` is on your `PATH`) before this package will work.

### Usage

`zhaires.py` wraps `Aires` to allow creating air showers from Python. If `Aires` is installed on your path, creating an Aires task is as simple as

    >>> import zhaires
    >>> sim = zhaires.Task()

        >>>> This is AIRES version 2.8.4a (12/Dec/2006)
        >>>> (Compiled by <user>@<hostname>, date: 13/Nov/2019) *
        >>>> USER: <user>, HOST: <hostname>, DATE: 28/Nov/2019
        >>>>

        Nov 2011: Add. ZHAireS radio emission
        > 28/Nov/2019 14:15:01. Reading data from standard input unit
        
If `Aires` is not on your path, you can explicitly provide the path to the `Aires` executable

    >>> sim = zhaires.Task(program="/path/to/my/installed/bin/Aires")
    
If you would like to load a predefined set of commands from an Aires command file, the path to this file can be provided to `cmdfile`

    >>> sim = zhaires.Task(cmdfile="my_commands.inp")

Once you have created an Aires task using one of the above methods, you can then use the `zhaires.py` utility functions to setup the shower as desired (see `zhaires.py/zhaires/aires.py` for a list of all available methods).

    >>> sim.task_name("my_aires_task")
    >>> sim.primary_energy(1, "EeV")
    >>> sim.primary_particle("proton")
    >>> sim.primary_zenith(53.44)
    >>> sim.primary_azimuth(0.)

You can also specify ZHAireS specific settings if you have **compiled Aires with ZHAireS enabled**.

    >>> sim.zhaires(True) # this enables ZHAireS
    >>> sim.fresnel_time(True) # this enabled time-domain ZHAireS
    >>> sim.add_antenna(0, 0, 0) # units of meters
    
`zhaires.py` provides many commands but if you wish to run a custom Aires command, this can be done using the function call syntax

    >>> sim("RandomSeed 0.128900437")
    
Once you have finished configuring your simulation, it can be started as

    >>> sim.run()
    
#### Loading ZHAireS Waveforms

We also provide methods to load ZHAireS waveforms from showers that were run with ZHAireS enabled

    >>> waveforms = zhaires.load_waveforms("my_aires_task")
    
`waveforms` is a structured Numpy array containing the properties of the shower, each antenna, and the associated electric fields. You can see the available properties with

    >>> waveforms.dtype
    
For example, to plot the y-component of the electric field of the first antenna defined in the shower, you might use (if `matplotlib` is installed)

    >>> import matplotlib.pyplot as plt
    >>> plt.plot(waveforms[0]['t'], waveforms[0]['Ey'])

It may take up to 60 seconds to load simulations with a large numbers of antennas. However, by default, `zhaires.py` creates a binary `.npy` cache file in the simulation directory that will make all future loads of this shower instantaneous (typically < 50ms). To disable writing the cache file (not recommended), use

    >>> waveforms = zhaires.load_waveforms("my_aires_task', write_cache = False)

### Installation

Before installing `zhaires.py`, you will need to set the `AIRES_RUN_DIR` environment variable telling `zhaires.py` where to store the Aires/ZHAireS output files. Each simulated shower is created in its own directory under `AIRES_RUN_DIR` with the name of the Aires task.

    $ export AIRES_RUN_DIR=<path to directory with decent storage capacity>
    
This should be added to your `.{bash,zsh,fish,tcsh,c}rc` file if you plan on regularly using `zhaires.py`.

To install `zhaires.py`, you will need `git`, Python >= 3.6, and any Fortran compiler. All three should be available in the package manager of any modern OS. It is tested on macOS 10.14, ubuntu 18.04, ubuntu 16.04, Fedora 29, and Fedora 30.

The below instructions are assuming that `python` refers to Python 3.\*. If `python` still refers to a decrepit Python 2.\*, please replace `python` with `python3` and `pip` with `pip3`.

If you only want to use `zhaires.py` and not develop additional features, it can be installed directly with `pip`.

    $ pip install git+https://github.com/rprechelt/zhaires.py
    
If you wish to develop `zhaires.py`, we recommend that you first clone the package to a suitable working directory

    $ git clone https://github.com/rprechelt/zhaires.py

and then change into the cloned directory and install using `pip`

    $ cd zhaires.py
    $ pip install --user -e .
    
#### Testing Your New Installation

You should then make sure that the installation was successful by trying to import `zhaires`

    $ python -c 'import zhaires'

If you wish to develop new features in `zhaires.py`, you will also need to install some additional dependencies so you can run our unit tests

    $ pip install --user -e .[test]

Once that is completed, you can run the unit tests directory from the `zhaires.py` directory

    $ python -m pytest tests
