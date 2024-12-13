"""
BioScout Technical Challenge
~~~~~~~~~~~~~~~~~~~~~~~~~~

A package for processing and analyzing weather and sensor data.
"""

from . import utils
from . import models
from . import imagery

__author__ = "Zach Milgate"
__email__ = "zach.milgate@example.com"
__description__ = "BioScout Technical Challenge Implementation"

# List all modules to be exposed
__all__ = [ 
    'models',
    'utils',
    'imagery'
]
