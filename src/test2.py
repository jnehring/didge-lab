import math
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy.interpolate import make_interp_spline, BSpline
from scipy import interpolate
from cad.calc.geo import Geo
from cad.cadsd.cadsd import CADSD
from scipy.signal import argrelextrema
<<<<<<< HEAD
from cad.calc.conv import note_to_freq
=======
from cad.calc.conv import note_to_freq, freq_to_note_and_cent, note_name
from cad.calc.loss import ImpedanceVolumeLoss
>>>>>>> dfe020b1803347391c8cd13a8b9bc7038831bb2d
from cad.evo.evolve_matema import MatemaLoss

geo=[[0, 32], [508.55926973865826, 36.75412105528995], [535.8319970113855, 38.54519171869711], [563.1047242841128, 40.16421550786348], [590.37745155684, 41.53301420056619], [617.6501788295674, 42.546736931397106], [644.9229061022946, 43.12885317320621], [672.1956333750219, 43.23751579086999], [689.2790575881348, 45.705207224384836], [699.4683606477491, 42.86913716358916], [726.7410879204765, 42.87700423840201], [754.0138151932038, 55.264235295156254], [781.286542465931, 64.75674643402766], [804.5133867607514, 62.214372998737055], [808.5592697386583, 70.35468645883958], [815.9489774728522, 72.29647174294925], [838.641896803255, 75.48782232878993], [861.3348161336578, 75.64329266703169], [884.0277354640606, 72.74408647759765], [906.7206547944635, 67.01938679343101], [929.4135741248663, 58.92876296765823], [952.1064934552691, 49.12579311750067], [974.799412785672, 38.40577991058426], [976.9415307270377, 40.81912786567178], [1011.4757454814816, 46.154325372089524], [1067.9704226683518, 58.089858244097286], [1097.2926777316702, 38.8275300921523], [1156.8437103335589, 43.23311097881199], [1220.484809502307, 47.941274680661195], [1242.5128463283668, 46.8275300921523], [1248.650626119842, 33.78816795075081], [1250.19921496285, 27.80084944039468], [1251.668077656768, 22.121776627636827], [1252.1372302337743, 20.307889151194157], [1271.8888653019255, 66.8275300921523]]
geo=Geo(geo)
loss=MatemaLoss()
loss.get_loss(geo)

<<<<<<< HEAD
loss=MatemaLoss()
print(loss.get_loss(geo))
=======
# print(geo.get_cadsd().get_notes())


# ground_peak=ImpedanceVolumeLoss(min_freq=note_to_freq(-32), max_freq=note_to_freq(-30), num_peaks=1)
# print(ground_peak.get_loss(geo))

# singer_peak=ImpedanceVolumeLoss(min_freq=300, num_peaks=1)
# print(singer_peak.get_loss(geo))

# ground=geo.get_cadsd().get_all_spektra_df()
# peaks=ground.iloc[argrelextrema(ground.impedance.values, np.greater_equal)[0]].copy()

# freq=note_to_freq(-31)
# for i in range(0, 5):
#     print(i, freq)
#     freq*=2
# print(peaks)
>>>>>>> dfe020b1803347391c8cd13a8b9bc7038831bb2d
