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

infile="output/2022-03-24T03-55-24_default/results/15.pkl"
mutant_pool=pickle.load(open(infile, "rb"))
outfile="test.pkl"
save_mutant_pool(mutant_pool, outfile)

# geo=[[0, 32], [200.65802418107742, 32.50823777552945], [227.64094858401003, 37.202047747456255], [254.62387298694264, 41.539751743735245], [281.6067973898753, 45.17317681216], [308.58972179280784, 47.809883774540154], [335.5726461957405, 49.237151978055834], [362.55557059867306, 49.339589141737974], [389.5384950016057, 48.108909152524284], [416.5214194045383, 45.645050884594035], [443.50434380747095, 42.14851114585772], [470.4872682104035, 37.90447810326771], [497.47019261333617, 33.26002010195141], [797.3836090097527, 34.01965744126459], [903.6208870303122, 36.73389861961078], [1015.8554481910962, 40.57784366275916], [1131.7539388195464, 45.2895890348758], [1143.679519963812, 49.33361975236936]]
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