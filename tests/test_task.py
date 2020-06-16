import os
import zhaires


def test_run_task() -> None:
    """
    Check that I can create and run ZHAireS sims.
    """

    # check if we are running under Github Actions
    if os.getenv("RUNNING_ON_GITHUB") is not None:
        return

    # otherwise, try and run the simulation

    # create the simulation
    sim = zhaires.Task(directory="/tmp/")

    # and use some of the functions
    sim.task_name("my_test_task")
    sim.primary_energy(1, "EeV")
    sim.primary_particle("proton")
    sim.primary_zenith(53.44)
    sim.primary_azimuth(0.0)
    sim.zhaires(True)
    sim.fresnel_time(True)
    sim.add_antenna(0, 0, 0)
    sim("RandomSeed 0.128900437")
    sim.thinning_energy(1e-1)
    sim.remark("Task generated in zhaires.py/tests::test_task.py")

    # and run the simulation
    sim.run()
