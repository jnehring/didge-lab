
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

from didgelab.calc.geo import Geo
from didgelab.calc.sim.sim import compute_impedance_iteratively, interpolate_spectrum, compute_ground_spektrum #create_segments, compute_ground_spektrum, compute_impedance, level_impedance, get_log_simulation_frequencies, get_max

from didgelab.calc.conv import note_name, note_to_freq

geo = [[0,32], [800, 34], [1500, 40], [1800, 70]]
geo = Geo(geo)
freqs, impedances = compute_impedance_iteratively(geo)
freq_interpolated, impedance_interpolated = interpolate_spectrum(freqs, impedances)
ground = compute_ground_spektrum(freq_interpolated, impedance_interpolated)

plt.plot(freqs, impedances, label="original")
plt.plot(freq_interpolated, impedance_interpolated, label="interpolated")
plt.plot(freq_interpolated, ground, label="ground")
plt.legend()
plt.show()
    

sys.exit(0)

