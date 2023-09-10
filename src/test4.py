
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

from didgelab.calc.geo import Geo
from didgelab.calc.sim.cadsd import CADSD
from didgelab.calc.sim.cadsd_old import CADSDOld
from didgelab.initializer import init_console_no_output
from didgelab.app import get_config

from didgelab.calc.conv import note_name, note_to_freq

init_console_no_output()

get_config()["sim.fmin"] = 1
get_config()["sim.fmax"] = 1000
get_config()["sim.grid_size"] = 50
get_config()["sim.grid"] = "log"

print(get_config())

freqs = np.concatenate((
    np.arange(1,50,5),
    np.arange(50, 100, 1),
    CADSD.get_simulation_frequencies(fmin=101, grid_size=30, grid="log")
))



print(len(freqs))
sys.exit(0)
geo = [[0,32], [800, 34], [1500, 40], [1800, 70]]
geo = Geo(geo)

for i in range(-40, -27):
    print(i, note_name(i), note_to_freq(i))

print(len(CADSD.get_simulation_frequencies()))

print(geo.get_cadsd().get_simulation_frequencies())
