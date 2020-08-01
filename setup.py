from os import path
from setuptools import setup

# the zhaires version
__version__ = "0.2.1"

# get the absolute path of this project
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# the standard setup info
setup(
    name="zhaires",
    version=__version__,
    description="A pure Python wrapper for the AireS and ZHAireS cosmic ray air shower simulators.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rprechelt/zhaires.py",
    author="Remy L. Prechelt",
    author_email="prechelt@hawaii.edu",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords=["cosmic", "ray", "air", "shower", "aires", "zhaires"],
    packages=["zhaires"],
    python_requires=">=3.6*, <4",
    install_requires=["numpy", "xarray"],
    extras_require={
        "test": [
            "pytest",
            "black",
            "mypy",
            "coverage",
            "pytest-cov",
            "flake8",
            "isort",
            "matplotlib",
        ],
    },
    scripts=[],
    project_urls={
        "AIRES": "https://arxiv.org/abs/astro-ph/9911331",
        "ZHAireS": "https://arxiv.org/pdf/1107.1189.pdf",
    },
    package_data={"zhaires": ["py.typed"]},
    include_package_data=True,
    zip_safe=False,
)
