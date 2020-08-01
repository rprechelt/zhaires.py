import os
import subprocess
from typing import Optional, Tuple

from .path import get_run_directory
from .utils import find_aires


class Task(object):
    """
    This class encapsulates a single Aires task.

    It can be created with different Aires binaries and
    can optionally load a file containing default commands.

    If `verbose` is provided, all commands are echoed to stdout.
    """

    # the subprocess for Aire
    process: Optional[subprocess.Popen] = None

    def __init__(
        self,
        program: str = None,
        cmdfile: str = None,
        verbose: bool = False,
        directory: str = get_run_directory(),
    ):
        """
        Create a new Aires task.

        Parameters
        ----------
        program: str
           The path to the Aires binary.
        cmdfile: str
           The path to a file containing default commands to run.
        verbose: bool
           If True, echo all commands before they are run.
        directory: str
           The directory to save the simulation.
           If None, use the current directory.
        """

        # the program that we launch to control Aires
        aires = program if program else find_aires()

        # check that `program` exists if it was provided
        if program:
            if not os.path.exists(program):
                raise ValueError(f"Unable to find `{program}`.")

        # save the verbose flag
        self.verbose = verbose

        # open Aires
        self.process = subprocess.Popen(aires, stdin=subprocess.PIPE)

        # try and load commands from a file
        self.load_from_file(cmdfile)

        # save the directory
        self.directory = directory

        # and set the run directory
        self.file_directory(self.directory, files="All")

        # create a Remark that this simulation was created by pyaires
        self.remark("Task generated using zhaires.py")

    def __exit__(self) -> None:
        """
        Ensure that the aires process is closed upon exit.
        """
        if self.process:
            self.exit()
            self.process.terminate()
            self.process = None

    def __call__(self, cmd: str) -> None:
        """
        Read and process an Aires command in a string.

        Parameters
        ----------
        cmd: str
            The Aires command to process

        Returns
        -------
        None
        """
        self.read_cmd(cmd)

    def load_from_file(self, cmdfile: Optional[str]) -> None:
        """
        Load an Aires command/input file by filename.

        Parameters
        ----------
        cmdfile: str
            The absolute path to an Aires command or input file.

        Returns
        -------
        None
        """

        # check that we actually got given a file
        if cmdfile is not None:
            # try and open the file
            with open(cmdfile, "r") as fp:

                # loop over all the lines in the file
                for line in fp:
                    self.read_cmd(line)

    def read_cmd(self, cmd: str) -> None:
        """
        Read and process an Aires command in a string.

        Parameters
        ----------
        cmd: str
            The Aires command to process

        Returns
        -------
        None
        """

        # check that we have a valid sessions
        if not self.process:
            msg = (
                "Simulation is finished/exited. "
                "Unable to process additional commands."
            )
            raise ValueError(msg)

        # if verbose, print the cmd before we run it
        if self.verbose:
            print(cmd)

        # add a newline if it doesn't already exist
        if cmd[-1] != "\n":
            cmd += "\n"

        # convert it to bytes and write it to stdin
        if self.process is not None:
            self.process.stdin.write(cmd.encode())  # type: ignore

            # and flush stdin to the Aires subprocess
            self.process.stdin.flush()  # type: ignore
        else:
            raise ValueError(f"Attempt to write command with NULL process!")

    def run(self) -> None:
        """
        Start the task.

        Returns
        -------
        None
        """
        if self.process is not None:
            self.process.communicate()  # type: ignore
        else:
            raise ValueError(f"Attempting to start a simulation with a NULL process!")

    def exit(self) -> None:
        """
        Stop and exit the current ZHAires sessions.

        Returns
        -------
        None
        """
        # write the exit command
        self.read_cmd("Exit")

        # and close down the process
        if self.process is not None:
            self.process.terminate()  # type: ignore
        self.process = None

    #####################################################
    # The rest of the file is class properties to allow
    # easy access to common simulation parameters.
    #####################################################
    def task_name(self, name: str) -> None:
        """
        Set the Aires task name (this determines output file names).

        Example: self.task_name('TestSim')
        """
        self.read_cmd(f"TaskName {name}")

    def total_showers(self, nshowers: int) -> None:
        """
        Sets the total number of showers in the task.

        Example: self.total_showers(1)
        """
        self.read_cmd(f"TotalShowers {int(nshowers)}")

    def showers_per_run(self, nshowers: int) -> None:
        """
        Sets the total number of showers per run.

        Example: self.showers_per_run(1)
        """
        self.read_cmd(f"ShowersPerRun {int(nshowers)}")

    def runs_per_process(self, runs: int) -> None:
        """
        Sets the total number of runs per process.

        Example: self.runs_per_process(1)
        """
        self.read_cmd(f"RunsPerProcess {int(runs)}")

    def max_cpu_time_per_run(self, time: float, unit: str = "hr") -> None:
        """
        Set the maximum cpu time per run. This defaults to hours but setting
        `unit` will override.

        Example: self.max_cpu_time_per_run(1)
        """
        self.read_cmd(f"MaxCpuTimePerRun {float(time)} {unit}")

    def primary_particle(self, particle: str) -> None:
        """
        Set the primary particle type.

        Example: self.primary_particle('proton')
        """
        self.read_cmd(f"PrimaryParticle {particle}")

    def primary_energy(self, energy: float, unit: str = "eV") -> None:
        """
        Set the primary particle energy. If not specified,
        the unit is eV however the `unit` kwarg overrides.

        Example: self.primary_energy(1e16)
        Example: self.primary_energy(10, 'PeV')
        """
        self.read_cmd(f"PrimaryEnergy {float(energy)} {unit}")

    def primary_zenith(self, zenith: float) -> None:
        """
        Set the primary particle zenith angle in degrees.

        Example: self.primary_zenith(80)
        """
        self.read_cmd(f"PrimaryZenAngle {float(zenith)} deg")

    def primary_azimuth(self, azimuth: float, geographic: bool = False) -> None:
        """
        Set the primary particle azimuth angle in degrees.
        Defaults to magnetic azimuth angle but if `geographic == True`,
        then `zenith` will be interpreted as a geographic zenith angle.

        Example: self.primary_azimuth(290.)
        Example: self.primary_azimuth(48., geographic=True)
        """
        # pick the suffix string
        suffix = "Geographic" if geographic else ""

        # and then write the command
        self.read_cmd(f"PrimaryAzimAngle {float(azimuth)} deg {suffix}")

    def injection_altitude(self, altitude: float, unit: str = "km") -> None:
        """
        Set the primary particle injection altitude. Defaults to 'km'
        but setting `unit` will override.

        Example: self.injection_altitude(120, 'km')
        """
        self.read_cmd(f"InjectionAltitude {float(altitude)} {unit}")

    def ground_altitude(self, altitude: float, unit: str = "km") -> None:
        """
        Set the ground altitude. Defaults to 'km' but setting
        `unit` will override.

        Example: self.ground_altitude(120, 'km')
        """
        self.read_cmd(f"GroundAltitude {float(altitude)} {unit}")

    def site(self, site: str) -> None:
        """
        Specify a built-in or previously defined site.

        Example: self.site('SouthPole')
        """
        self.read_cmd(f"Site {site}")

    def add_site(
        self, name: str, lat: float, lon: float, alt: float, unit: str = "m"
    ) -> None:
        """
        Create a new observing site given a `name`, `lat`/`lon` in degrees, and
        altitude in `m`. Settings unit overrides the units for altitude.

        Example: self.site('TestSite', 32.5, 84.5, 1200, 'm')
        """
        self.read_cmd(f"AddSite {name} {lat} deg {lon} deg {alt} {unit}")

    def geomagnetic_field(self, strength: float, incl: float, dec: float) -> None:
        """
        Set the geomagnetic field at the event location.

        Parameters
        ----------
        strength: float
            The geomagnetic field in nT.
        inclination:
            The geomagnetic inclination angle in degrees.
        declination: float
            The geomagnetic declination angle in degrees.
        """
        self.read_cmd(f"GeomagneticField {strength} nT {incl} deg {dec} deg")

    def thinning_energy(
        self, energy: float, unit: str = "eV", relative: bool = False
    ) -> None:
        """
        Set the thinning energy in eV. If relative is True, then treat
        `energy` as (thinning_energy/primary_energy).

        Example: self.thinning_energy(1e9)
        Example: self.thinning_energy(1e6, unit='keV')
        Example: self.thinning_energy(1e-6, relative=True)
        """
        # if this is a relative thinning energy
        if relative:
            self.read_cmd(f"ThinningEnergy {float(energy)} Relative")
        else:  # otherwise it is an absolute energy
            self.read_cmd(f"ThinningEnergy {float(energy)} {unit}")

    def thinning_w_factor(self, factor: float) -> None:
        """
        Update the maximum thinning weight factor.

        Example: self.thinning_w_factor(0.06)
        """
        self.read_cmd(f"ThinningWFactor {float(factor)}")

    def date(self, date: float) -> None:
        """
        Set the date of the simulation. Used to calculate the magnetic field
        using the IGRF field model.

        Parameters
        ----------
        date: float
            The year as a fractional float (i.e. 2016.943).

        Returns
        -------
        None
        """
        self.read_cmd(f"Date {date}")

    def per_shower_data(self, data: str) -> None:
        """
        Control the per shower data saved by Aires - allowed values
        are 'Full', 'Brief', or 'None'

        Example: self.per_shower_data('Full')
        Example: self.per_shower_data('Brief')
        Example: self.per_shower_data('None')
        """
        # check it is a valid value
        if data not in ["Full", "Brief", "None"]:
            raise ValueError("`per_shower_data` only accepts 'Full', 'Brief', 'None'.")

        # otherwise pass it to Aires
        self.read_cmd(f"PerShowerData {data}")

    def zhaires(self, enabled: bool = True) -> None:
        """
        Enable (or disable) ZHAires.

        Example: self.zhaires()
        Example: self.zhaires(False)
        """
        # construct the enable disable disable
        status = "On" if enabled else "Off"

        # and pass it to Aires
        self.read_cmd(f"ZHAireS {status}")

    def fresnel_time(self, enabled: bool = True) -> None:
        """
        Enable (or disable) ZHAires time-domain mode.

        Example: self.fresnel_time()
        Example: self.fresnel_time(False)
        """
        # construct the enable disable disable
        status = "On" if enabled else "Off"

        # and pass it to Aires
        self.read_cmd(f"FresnelTime {status}")

    def time_domain_bin(self, time: float, unit: str = "ns") -> None:
        """
        Sets the time-domain bin size in ZHAireS. This defaults
        to 'ns' but setting `unit` will override.

        Example: self.time_domain_bin(0.2)
        Example: self.time_domain_bin(0.5, 'ps')
        """
        # and pass it to Aires
        self.read_cmd(f"TimeDomainBin {float(time)} {unit}")

    def add_antenna(self, x: float, y: float, z: float = 0.0) -> None:
        """
        Creates an antenna at (x, y, z) in m w.r.t coordinate origin.
        If not given, `z` defaults to ground level.

        Example: self.add_antenna(3, 5)
        Example: self.add_antenna(320, 5700, 1200
        """
        # and pass it to Aires
        self.read_cmd(f"AddAntenna {float(x)} {float(y)} {float(z)}")

    def add_line_antenna(
        self,
        start: Tuple[float, float, float],
        end: Tuple[float, float, float],
        nant: int,
    ) -> None:
        """
        Create a line of `nant` between `start` and `end`.

        Example: self.add_line_antenna((0, 0, 0), (100, 1200, 0), 20)
        """
        # the start location string
        startstr = f"{float(start[0])} {float(start[1])} {float(start[2])}"

        # the end location string
        endstr = f"{float(end[0])} {float(end[1])} {float(end[2])}"

        # and pass it to Aires
        self.read_cmd(f"AddAntenna Line {startstr} {endstr} {int(nant)}")

    def add_ring_antenna(
        self, origin: Tuple[float, float, float], radius: float, phi0: float, nant: int
    ) -> None:
        """
        Create a ring of `nant` antennas on a circle of radius `radius` [m]
        centered at `origin` [m] starting at magnetic azimuth `phi0`
        in degrees.

        Example: self.add_ring_antenna((0, 0, 0), (100, 1200, 0), 20)
        """
        # the start location string
        originstr = f"{float(origin[0])} {float(origin[1])} {float(origin[2])}"

        # and construct the command
        cmd = f"{originstr} {float(radius)} {float(phi0)} {int(nant)}"

        # and pass it to Aires
        self.read_cmd(f"AddAntenna Ring {cmd}")

    def delete_antennas(self) -> None:
        """
        Delete all created antennas.

        Example: self.delete_antennas()
        """
        self.read_cmd("AddAntenna None")

    def include_hadrons(self, enabled: bool = True) -> None:
        """
        Include hadrons in ZHAireS radio calculations.

        Example: self.include_hadrons() # turns ONN hadrons
        Example: self.include_hadrons(False) # turns OFF hadrons
        """
        # construct the status string
        status = "On" if enabled else "Off"

        # and pass it to Aires
        self.read_cmd(f"IncludeHadrons {status}")

    def random_seed(self, seed: float) -> None:
        """
        Sets the random seed - this must be between 0 and 1.

        Example: self.random_seed(0.1298004637)
        """
        self.read_cmd(f"RandomSeed {float(seed)}")

    def file_directory(self, directory: str, files: str = "All") -> None:
        """
        Specify the directory for specific simulation files.

        Example: self.file_directory('test/')
        Example: self.file_directory('test/', files = 'All')
        """
        self.read_cmd(f"FileDirectory {files} {directory}")

    def summary(self, enabled: bool = True) -> None:
        """
        Enable or disable the summary file

        Example: self.summary() # turns ON summary file
        Example: self.summary(False) # turns OFF summary file
        """
        # construct the status string
        status = "On" if enabled else "Off"

        # and pass it to Aires
        self.read_cmd(f"Summary {status}")

    def remark(self, remark: str) -> None:
        """
        Add a string 'remark' to the simulation.

        Example: self.remark('Hello world')
        """
        self.read_cmd(f"Remark {remark}")
