from cad.common.app import App
import numpy as np
from cad.calc.geo import geotools
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent
import math
import numpy as np
from cad.calc.geo import Geo
import matplotlib.pyplot as plt
from cad.calc.parameters import FinetuningParameters, MutationParameterSet, MbeyaShape
import random
from cad.cadsd.cadsd import CADSD, cadsd_volume
from cad.cadsd._cadsd import cadsd_Ze, create_segments_from_geo
from cad.ui.visualization import make_didge_report, DidgeVisualizer
import seaborn as sns
import pandas as pd
from cad.calc.parameters import AddBubble, MbeyaShape
from cad.calc.mutation import ExploringMutator

shape=MbeyaShape(n_bubbles=2, add_bubble_prob=0.2)

shape.set_minmax("opening_factor_y", 1.5, 2.0)
shape.set_minmax("d_pre_bell", 0, 10)
shape.set_minmax("bellsize", 3, 20)


# shape.set("opening_factor_y", 2)
# shape.set("d_pre_bell", 0)
# shape.set("bellsize", 10)
# shape.set("bubble_pos_0", 0.2)
# shape.set("bubble_pos_1", 0.7)

DidgeVisualizer.vis_didge(shape.make_geo())
plt.show()