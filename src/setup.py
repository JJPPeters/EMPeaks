from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

import os

# setup peak pairs stuff
current_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(current_path+"/Processing/PeakPairs")
os.system("python setup_peak_pairs.py build_ext -i clean")
os.chdir(current_path)