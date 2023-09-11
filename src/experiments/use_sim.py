import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import argrelextrema

from didgelab.calc.geo import Geo
from didgelab.calc.sim.sim import compute_impedance_iteratively, interpolate_spectrum, compute_ground_spektrum, get_notes
from didgelab.calc.conv import note_name, note_to_freq, freq_to_note_and_cent

geo = [[0,32], [800, 34], [1500, 40], [1800, 70]]
geo = Geo(geo)
freqs, impedances = compute_impedance_iteratively(geo)
freq_interpolated, impedance_interpolated = interpolate_spectrum(freqs, impedances)
ground = compute_ground_spektrum(freq_interpolated, impedance_interpolated)

peaks = get_notes(freqs, impedances)
print(peaks)

plt.plot(freqs, impedances, label="original")
plt.plot(freq_interpolated, impedance_interpolated, label="interpolated")
plt.plot(freq_interpolated, ground, label="ground")
plt.legend()
plt.show()
    

