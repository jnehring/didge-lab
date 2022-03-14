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

f=note_to_freq(-31)
tones=sorted([1,5,6,3,10,12])

def freq_plot():
    data=[]
    for i in tones:
        for x in np.arange(500, 610, 0.1):
            name="fundamental" if i==1 else f"overtone {i-1}"
            freq=f*i
            note,cent=freq_to_note_and_cent(freq)
            note=note_name(note)
            name += f", {note}, {freq:.2f} Hz"
            data.append([x, np.sin(i*x*2*np.pi/f), name])

    df=pd.DataFrame(data, columns=["frequency", "amplitude", "tone"])
    sns.lineplot(data=df, x="frequency", y="amplitude", hue="tone")

def bore_plot():
    data=[]
    for i in tones:
        for x in np.arange(1300, 1800, 0.1):
            name="fundamental" if i==1 else f"overtone {i-1}"
            freq=f*i
            note,cent=freq_to_note_and_cent(freq)
            note=note_name(note)
            name += f", {note}, {freq:.2f} Hz"

            wavelength=freq_to_wavelength(freq)
            data.append([x, np.sin(i*x*2*np.pi/wavelength), name])

    df=pd.DataFrame(data, columns=["distance from mouth piece [mm]", "amplitude", "tone"])
    sns.lineplot(data=df, x="distance from mouth piece [mm]", y="amplitude", hue="tone")

bore_plot()

f_overtone=f*5
note, cent=freq_to_note_and_cent(f_overtone)
print(f_overtone, freq_to_wavelength(f_overtone), note_name(note))

# # print maxima of fundamental
# print("maxima of fundamental")
# for i in range(1,8):
#     f1=f*i
#     wavelength=freq_to_wavelength(f)
#     print(wavelength)
#     for j in [1,3]:
#         print(i, f1+f*j/4, wavelength*i+j/4)

# # print wavelength
# for i in [1,5,9]:

sns.set(rc={'figure.figsize':(16,6)})

plt.grid()
plt.savefig("singer.jpg")
plt.show()

# shape=MatemaShape(n_bubbles=2, add_bubble_prob=0.4)
# shape.read_csv("test.csv")
# shape.make_geo()

# infile="output/2022-03-03T12-03-10_default/results/5.pkl"

# mutant=pickle.load(open(infile, "rb"))

# print(mutant.get(9).geo.get_cadsd().get_notes())
# mutant.get(0).parameterset.to_pandas().to_csv("test.csv")

# print(mutant.get(8).parameterset)

# for i in range(10):
#    print(i, mutant.get(i).geo.geo[-1][0])

# shape=MatemaShape(n_bubbles=2, add_bubble_prob=0.4)
# shape.read_csv("test.csv")

# ol=1847.567267735626
# shape.set_minmax("length", ol, ol)

# em=ExploringMutator()
# for i in range(20):
#     mutant=shape.copy()
#     em.mutate(mutant)
#     print(mutant.make_geo().geo[-1])