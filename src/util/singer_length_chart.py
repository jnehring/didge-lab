from cad.common.app import App
import numpy as np
from cad.calc.geo import geotools
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent, freq_to_wavelength
import math
import numpy as np
from cad.calc.geo import Geo
import matplotlib.pyplot as plt
from cad.calc.parameters import FinetuningParameters, MutationParameterSet, MbeyaShape, MatemaShape
import random
from cad.cadsd.cadsd import CADSD, cadsd_volume
from cad.cadsd._cadsd import cadsd_Ze, create_segments_from_geo
from cad.ui.visualization import make_didge_report, DidgeVisualizer
import seaborn as sns
import pandas as pd
from cad.calc.parameters import AddBubble, MbeyaShape
from cad.calc.mutation import ExploringMutator
from make_didge_report import didge_report
import os
from cad.calc.loss import LossFunction, TootTuningHelper, single_note_loss, diameter_loss
import pickle
import json
from cad.evo.evolve_matema import MatemaLoss

fundamental_freq=note_to_freq(-31)
n_overtone=5
f_overtone=fundamental_freq*(n_overtone+1)
f_overtone=440

tones=sorted([1,2,3])
tones=[1,2,3]
tones=sorted([1,5,6,3])

def freq_plot():
    data=[]
    for i in tones:
        for x in np.arange(500, 610, 0.1):
            name="fundamental" if i==1 else f"overtone {i-1}"
            freq=fundamental_freq*i
            note,cent=freq_to_note_and_cent(freq)
            note=note_name(note)
            name += f", {note}, {freq:.2f} Hz"
            data.append([x, np.sin(i*x*2*np.pi/f), name])

    df=pd.DataFrame(data, columns=["frequency", "amplitude", "tone"])
    sns.lineplot(data=df, x="frequency", y="amplitude", hue="tone")

def bore_plot():
    data=[]
    for i in tones:
        name="fundamental" if i==1 else f"overtone {i-1}"
        freq=fundamental_freq*i
        note,cent=freq_to_note_and_cent(freq)
        note=note_name(note)
        name += f", {note}, {freq:.2f} Hz"

        wavelength=freq_to_wavelength(freq)

        #for x in np.arange(1300, 1800, 0.1):
        for x in np.arange(0, 2000, 1):
            data.append([x, abs(np.sin(x*2*np.pi/wavelength)), name])

    df=pd.DataFrame(data, columns=["distance from mouth piece [mm]", "amplitude", "tone"])
    sns.lineplot(data=df, x="distance from mouth piece [mm]", y="amplitude", hue="tone")

wavelength_overtone=freq_to_wavelength(f_overtone)
print(f"overtone {n_overtone} at {f_overtone:.2f} Hz, wavelength {wavelength_overtone}")
print("maxima")
for i in range(3):
    print(i, (i+1/4)*wavelength_overtone)
# print("1st maximum of fundamental")
# print(freq_to_wavelength(f)/4)
# for i in range(1,2):
#     f1=f*i
#     wavelength=freq_to_wavelength(f)
#     print(wavelength)
#     for j in [1,3]:
#         print(i, f1+f*j/4, wavelength*i+j/4)

# # print wavelength
# for i in [1,5,9]:

sns.set(rc={'figure.figsize':(16,6)})

plt.grid()
plt.legend(loc='lower right')
plt.savefig("singer.jpg")
plt.show()
