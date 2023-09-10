import numpy as np
import json
import pandas as pd
import matplotlib.pyplot as plt

from didgelab.calc.geo import Geo
from didgelab.calc.sim.cadsd import CADSD
from didgelab.calc.sim.cadsd_old import CADSDOld
from didgelab.initializer import init_console_no_output
from didgelab.app import get_config

init_console_no_output()

def get_closest_index(freqs, f):
    for i in range(len(freqs)):
        m2=np.abs(freqs[i]-f)
        if i==0:
            m1=m2
            continue
        if m2>m1:
            return i-1
        m1=m2

    if f>freqs[-1]:
        return len(freqs)
    else:
        return len(freqs)-1

# warning: frequencies must be evenly spaced
def compute_ground(freqs, impedance, fmin, fmax):

    peaks=[0,0]
    vally=[0,0]

    up = 0
    npeaks = 0
    nvally = 0

    for i in range(get_config()["sim.fmin"]+1, get_config()["sim.fmax"]):
        if impedance[i] > impedance[i-1]:
            if npeaks and not up:
                vally[nvally] = i - 1
                nvally+=1
            up = 1
        else:
            if up:
                peaks[npeaks] = i - 1
                npeaks+=1
            up = 0
        if nvally > 1:
            break

    if peaks[0]<0:
        raise Exception("bad fft")
    
    fundamental_freq = freqs[peaks[0]]

    ground = np.zeros(len(freqs))
    indizes = np.concatenate((np.arange(fmin,fundamental_freq), np.arange(fundamental_freq,fmin-1,-1)))
    window_right = impedance[indizes]

    k = 0.0001
    for i in range(fundamental_freq, fmax, fundamental_freq):

        il = get_closest_index(freqs, i-fundamental_freq+1)
        ir = np.min((len(freqs)-1, il+len(window_right)))

        window_left = impedance[il:ir]
        if ir-il!=len(window_right):
            window_right = window_right[0:ir-il]

        ground[il:ir] += window_right*np.exp(i*k)

    for i in range(len(ground)):
        ground[i] = impedance[i] * ground[i] * 1e-6

    for i in range(len(ground)):
        x=ground[i]*2e-5
        ground[i] = 0 if x<1 else 20*np.log10(x) 
        impedance[i] *= 1e-6

    return ground

geo = [[0,32], [800, 34], [1500, 40], [1800, 70]]
geo = Geo(geo)
cadsd = geo.get_cadsd()

fmin = 1
fmax = 1000

get_config()["sim.fmin"] = fmin
get_config()["sim.fmax"] = fmax
get_config()["sim.grid_size"] = 10
get_config()["sim.fmax"] = fmax
get_config()["sim.grid"] = "log"

freq, impedance = cadsd.compute_raw_impedance()

print(freq)

# ground = compute_ground(freq, impedance, fmin, fmax)

# cadsd_old = CADSDOld(geo)
# spektrum = cadsd_old.get_ground_spektrum()

# plt.plot(freq, impedance, label="impedance")
# plt.plot(freq, ground, label="ground")
# plt.plot(spektrum.keys(), spektrum.values(), label="old ground")
# plt.legend()
# plt.show()
