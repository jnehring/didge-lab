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


geo=[[0, 32], [10.0, 32.09352156481183], [37.27272727272727, 32.348580377935], [64.54545454545455, 32.60363919105817], [91.81818181818181, 32.85869800418134], [119.0909090909091, 33.113756817304505], [146.36363636363637, 33.368815630427676], [173.63636363636363, 33.62387444355085], [200.9090909090909, 33.87893325667402], [228.1818181818182, 34.13399206979719], [255.45454545454547, 34.38905088292036], [279.72007108900107, 34.615985875751946], [302.81100673250967, 38.99314649472288], [325.9019423760182, 43.082697644486856], [348.9928780195268, 46.56472238723764], [372.0838136630354, 49.1650054452909], [395.17474930654396, 50.678027630912204], [418.26568495005256, 50.984616693527585], [441.35662059356116, 50.062743530288074], [464.44755623706976, 47.99049663090419], [487.5384918805783, 44.940897396187374], [510.6294275240869, 41.16888387804427], [533.7203631675955, 36.99143635353712], [638.3737065703626, 37.970170797318765], [654.3540191329254, 41.00477519609626], [670.334331695488, 43.82734804783839], [686.3146442580507, 47.273830981085936], [702.2949568206135, 54.38091850770447], [703.9660293891607, 54.74794071050495], [718.2752693831761, 57.89071791949841], [734.2555819457389, 60.16597335351632], [750.2358945083015, 60.342936588563845], [766.2162070708642, 59.49918375025972], [782.196519633427, 57.746272844661746], [798.1768321959896, 55.277166337598004], [814.1571447585522, 52.35280432915201], [962.9955021963772, 57.66334057827139], [1084.9214742378085, 60.55051907612631], [1107.3886546070316, 70.48561779946924], [1129.8558349762548, 79.81609802180441], [1152.3230153454779, 87.80979321972883], [1162.5641366288612, 95.3876591214132], [1174.790195714701, 93.83167184572942], [1197.2573760839239, 97.37657289754344], [1219.724556453147, 97.96348483377668], [1242.19173682237, 95.74798027795975], [1264.6589171915932, 90.90837749207383], [1287.1260975608163, 83.83953032049686], [1309.5932779300394, 75.12311439128767], [1332.0604582992623, 65.4822740856245], [1366.4232521571441, 66.06485176448399], [1407.9320587783213, 66.76858104545006], [1407.9320587783213, 66.76858104545006], [1529.6069305516985, 68.83142449951924], [1607.9320587783213, 88.19220141203027]]
geo=Geo(geo)

# for i in range(len(geo)):
#     if i>0 and geo[i][0]-geo[i-1][0]==0:
#         print("*")
#     print(geo[i])
geo.get_cadsd().get_notes()

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