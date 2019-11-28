# zhaires.py
A Python wrapper for the AireS and ZHAireS cosmic ray air shower simulation codes.

![GitHub](https://img.shields.io/github/license/rprechelt/zhaires.py?logoColor=brightgreen)
![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue)

ZHAireS.py is a Python wrapper around the AireS and ZHAireS cosmic ray air shower simulation codes. This allows for creating AireS simulations directly from Python, and importing AireS data files back into Python for data analysis.

Note: this package does not include a copy of AireS. You will need to download and install a working copy of AireS separately (so that `Aires` is on your `PATH`) before this package will work.

### Installation

To install `zhaires.py`, you will need `git`, [git-lfs](https://git-lfs.github.com/), and Python >= 3.6. All three should be available in the package manager of any modern OS. It is tested on macOS 10.14, ubuntu 18.04, ubuntu 16.04, Fedora 29, and Fedora 30.

The below instructions are assuming that `python` refers to Python 3.\*. If `python` still refers to a decrepit Python 2.\*, please replace `python` with `python3` and `pip` with `pip3`.

The recommended method of installation is to first clone the package

    $ git clone https://github.com/rprechelt/zhaires.py

and then change into the cloned directory and install using `pip`

    $ cd zhaires.py
	$ pip install --user -e .

You should then make sure that the installation was successful by trying to import `zhaires`

    $ python -c 'import zhaires'

If you wish to develop new features in `zhaires`, you will also need to install some additional dependencies so you can run our unit tests

    $ pip install --user -e .[test]

Once that is completed, you can run the unit tests directory from the `zhaires` directory

    $ python -m pytest tests
