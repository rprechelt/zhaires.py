# zhaires.py
A Python wrapper for the AireS and ZHAireS cosmic ray air shower simulation codes.

[![Actions Status](https://github.com/rprechelt/zhaires.py/workflows/tests/badge.svg)](https://github.com/rprechelt/zhaires.py/actions)
![GitHub](https://img.shields.io/github/license/rprechelt/zhaires.py?logoColor=brightgreen)
![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue)

ZHAireS.py is a Python wrapper around the AireS and ZHAireS cosmic ray air shower simulation codes. This allows for creating AireS simulations directly from Python, and importing AireS data files back into Python for data analysis.

Note: this package does not include a copy of AireS. You will need to download and install a working copy of AireS separately (so that `Aires` is on your `PATH`) before this package will work.

### Installation

Before installing `zhaires.py`, you will need to set the `AIRES_RUN_DIR` environment variable telling `zhaires.py` where to store the Aires/ZHAireS output files. Each simulated shower is created in its own directory under `AIRES_RUN_DIR` with the name of the Aires task.

    $ export AIRES_RUN_DIR=<path to directory with decent storage capacity>
	
This should be added to your `.{bash,zsh,fish,tcsh,c}rc` file if you plan on regularly using `zhaires.py`.

To install `zhaires.py`, you will need `git` and Python >= 3.6. All three should be available in the package manager of any modern OS. It is tested on macOS 10.14, ubuntu 18.04, ubuntu 16.04, Fedora 29, and Fedora 30.

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
