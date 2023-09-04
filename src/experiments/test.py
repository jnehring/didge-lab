from didgelab.calc.sim.cadsd import CADSD
from didgelab.calc.geo import Geo
from didgelab.app import App
from didgelab.initializer import init_console_no_output

from time import time
import numpy as np
import pandas as pd

init_console_no_output()

resolutions = (1,2,4,8,16,32)
num_segments = (2,5,20,50,100)

df = pd.DataFrame(index=resolutions, columns=num_segments)
n_tries = 5
App.get_config()["sim.correction"] = "none"
for r in resolutions:
    App.get_config()["sim.resolution"] = r

    for num in num_segments:
        t=time()
        for i in range(n_tries):
            x = 2000*np.arange(0,1,1/num)
            y = 32+35*np.arange(0,1,1/num)
            geo = list(zip(x,y))
            cadsd = Geo(geo).get_cadsd()
            imp = cadsd.get_impedance_spektrum()
        t = (time()-t)/n_tries
        df[num][r] = t

df = df.round(2)
print(df)

#print(len(imp.freq))
