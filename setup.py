from setuptools import setup, find_packages
from os import path
from zhaires import __version__

# get the absolute path of this project
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# the standard setup info
setup(
    name='zhaires',
    version=__version__,
    description='A pure Python wrapper for the AireS and ZHAireS cosmic ray air shower simulators.',
    long_description=long_description, 
    long_description_content_type='text/markdown',
    url='https://github.com/rprechelt/zhaires.py',
    author='Remy L. Prechelt',
    author_email='prechelt@hawaii.edu',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='cosmic ray air shower aires zhaires',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']), 
    python_requires='>=3.6*, <4',
    install_requires=['numpy'],
    extras_require={
        'test': ['pytest', 'coverage'],
    },
    project_urls={
        'AIRES': 'https://arxiv.org/abs/astro-ph/9911331',
        'ZHAireS': 'https://arxiv.org/pdf/1107.1189.pdf'
    },
)
