from cad.calc.geo import geotools
from cad.cadsd.cadsd import CADSDResult
from cad.calc.geo import Geo
from cad.ui.visualization import FFTVisualiser
import matplotlib.pyplot as plt

geo=[[0, 32], [800, 32], [900, 38], [970, 42], [1050, 40], [1180, 48], [1350, 60], [1390, 68], [1500, 72]]

geo=Geo(geo=geo)
cadsd=CADSDResult.from_geo(geo)

FFTVisualiser.vis_fft_and_target(cadsd.fft)
plt.show()