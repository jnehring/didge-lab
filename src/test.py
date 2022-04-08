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
from cad.calc.parameters import MatemaShape
from cad.evo.evolve_kizimkazi import KizimkaziLoss
from cad.calc.util.mutant_pool_store import save_mutant_pool


geo=[[0, 32], [155.79953130903596, 33.32460005042448], [170.8215820902333, 34.57015359728445], [185.84363287143066, 35.73333642718836], [188.02276911222978, 34.36070487122439], [200.865683652628, 36.729252000950865], [215.88773443382536, 37.48597305327159], [230.9097852150227, 37.95049760209339], [245.93183599622006, 38.0932084300103], [260.95388677741744, 37.910461343077316], [275.97593755861476, 37.42507722234471], [290.9979883398121, 36.6846820597922], [306.02003912100946, 35.758014159738096], [321.04208990220684, 34.72948426031741], [677.1111664129595, 37.75676626006363], [693.0931280782052, 37.89264412214574], [1032.838261679418, 38.127141941390526], [1037.950801799321, 38.16232709707329], [1047.5674373130644, 45.74398174063208], [1057.1840728268076, 52.74174572304605], [1066.800708340551, 58.590986714302645], [1076.4173438542941, 62.81834538317274], [1085.1021545387168, 64.86128292570918], [1102.2177058010807, 72.83071736487521], [1107.1839004947822, 72.5314022111478], [1116.917962028583, 88.51995825156418], [1126.6520235623839, 97.24109472261027], [1136.3860850961846, 99.69924683845124], [1146.1201466299854, 102.65589701744919], [1155.854208163786, 105.00287908678668], [1165.588269697587, 114.63551440281357], [1175.3223312313878, 120.4698589236792], [1185.0563927651885, 121.76240145143306], [1194.7904542989895, 115.55622418022816], [1204.5245158327903, 103.96570673648144], [1214.2585773665912, 86.47408439877769], [1222.0265646376272, 87.97187076662885], [1239.142115899991, 86.57585876274737], [1256.257667162355, 81.13992480322048], [1273.3732184247185, 72.98682975996836], [1291.7208627594616, 72.70044169938473], [1310.7252900779908, 70.68457210237827], [1329.72971739652, 67.42934503620285], [1348.7341447150493, 62.34825432624749], [1354.222332825919, 60.78330867411263], [1354.222332825919, 60.78330867411263], [1367.7385720335785, 56.929180616922274], [1376.4796681835483, 59.23194567342132], [1402.6337558056646, 70.72233881641586], [1554.222332825919, 76.42769260802197]]
geo=Geo(geo)

# for i in range(len(geo)):
#     if i>0 and geo[i][0]-geo[i-1][0]==0:
#         print("*")
#     print(geo[i])
print(geo.get_cadsd().get_notes())

# geo=Geo(geo)
# fundamental=-31
# fundamental_freq=note_to_freq(fundamental)

# length=1168.6795199638118

# wavelength_fundamental=freq_to_wavelength(fundamental_freq)
# wavelength_2nd_harmonic=freq_to_wavelength(fundamental_freq*3)
# wavelength_4nd_harmonic=freq_to_wavelength(fundamental_freq*5)

# max_fundamental=math.sin(length*2*np.pi/wavelength_fundamental)
# max_2nd_harmonic=math.sin(length*2*np.pi/wavelength_2nd_harmonic)
# max_4nd_harmonic=math.sin(length*2*np.pi/wavelength_4nd_harmonic)
# print(f"fundamental\t{max_fundamental}\t{fundamental_freq}")
# print(f"2nd harmonic\t{max_2nd_harmonic}\t{fundamental_freq*3}")
# print(f"4th harmonic\t{max_4nd_harmonic}\t{fundamental_freq*5}")

# # fundamental at 73.42 Hz
# # 2nd harmonic at 220.25 Hz
# # 4th harmonic at 367.08 Hz

# target_peaks=[fundamental_freq*3, fundamental_freq*5]

# length-=25
# weights={
#     "octave_loss": 0
# }
# loss=KizimkaziLoss(fundamental=fundamental, singer_peaks=target_peaks, add_octave=False, n_notes=2, weights=weights)    

# l=loss.get_loss(geo)
# print(json.dumps(l, indent=4))