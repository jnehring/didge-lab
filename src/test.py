import numpy as np
import json
import os
import matplotlib.pyplot as plt

from didgelab.calc.sim.cadsd import CADSD
from didgelab.app import get_app
from didgelab.initializer import init_console_no_output
from didgelab.calc.geo import Geo


init_console_no_output()

get_app().get_config()["sim.correction"] = "none"
get_app().get_config()["sim.grid"] = "even"
get_app().get_config()["sim.grid_size"] = 1
get_app().get_config()

da_path = "/Users/jane03/workspaces/music/didge/didge-archive"
didge_archive = json.load(open(os.path.join(da_path, "didge-archive.json")))
didge_archive = list(filter(lambda x:x["shape"] == "straight", didge_archive))
didge = didge_archive[1]

geo = Geo(json.load(open(os.path.join(da_path, didge["geometry"]))))
cadsd = CADSD(geo)

freq, impedance = cadsd.compute_raw_impedance()
ground = cadsd.compute_ground_spektrum(freq, impedance)

impedance /= impedance.max()
ground /= ground.max()

plt.plot(freq, impedance, label="Impedance")
plt.plot(freq, ground, label="Ground")
plt.legend()

plt.show()