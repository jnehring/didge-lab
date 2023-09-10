import pandas as pd
import os
import json
import numpy as np

from didgelab.app import get_config
from didgelab.calc.geo import Geo

get_config()["sim.resolution"] = 1
get_config()["sim.frequencies"] = "even"
get_config()["sim.fmin"] = 1
get_config()["sim.fmax"] = 1000

geo = [[0,32], [800, 60], [2000, 70]]
geo = Geo(geo)

cadsd = geo.get_cadsd()

# cadsd._get_sound_spektrum()
fft1 = cadsd.get_ground_spektrum()

#cadsd._get_sound_spektrum_old()
#fft2 = cadsd.sound_spektra["ground"]



import matplotlib.pyplot as plt

#plt.plot(fft1.keys(), fft1.values())
#plt.plot(fft1["freq"], fft1["ground"])
#plt.plot(fft2.keys(), fft2.values())
#plt.show()

