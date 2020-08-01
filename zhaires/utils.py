"""
Various utilities for working with AIRES/ZHAireS.
"""

import os.path as op
from shutil import which


def find_aires(suffix: str = "") -> str:
    """
    Try and find the Aires executable.

    If `suffix` is defined, try and find Aires+`suffix`.

    If the program cannot be found, an exception is thrown.

    Parameters
    ----------
    suffix: str
        The suffix for the Aires executable.

    Returns
    -------
    path: str
        The path to the found executable.

    Raises
    ------
    RuntimeError:
        If the executable cannot be found.

    """

    # try and find it
    executable = which("Aires"+suffix)

    # check that the executable exists
    if executable is None or not op.exists(executable):
        raise RuntimeError(
            f"Unable to find `Aires{suffix}` executable. "
            "Ensure AIRES_DIR/bin is on your PATH or "
            "explicitly provide the path."
        )

    # otherwise, we foun Adires
    return executable
