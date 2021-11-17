from cad.cadsd.cadsd import CADSDResult
from cad.calc.geo import Geo
import matplotlib.pyplot as plt
from cad.calc.didgmo import didgmo_high_res, didgmo_bridge
import time

geo=[[0.0, 32], [903.4265490017885, 44.74696440831961], [1043.2783924481641, 43.520495439677866], [1167.5572483229255, 56.05287987234595], [1265.8172834833592, 59.372000817740116], [1361.0641095223732, 75.9832280080771], [1424.7784835799014, 79.32653417809952], [1531.5316609725612, 110.29806559536875], [1634.4641691886077, 117.651508890613], [1785.0643420008407, 143.5795381422663], [1907.2298859137284, 196.87608436044138], [2113.0, 198.08650024980747]]
geo=Geo(geo=geo)

cadsd=CADSDResult.from_geo(geo)

# t1=time.time()
#fft=get_impedance_spektrum(geo.geo, 1, 1000, 1)
# print("fft1", time.time()-t1)

# t1=time.time()
# fft2=didgmo_bridge(geo)
# print("fft2", time.time()-t1, fft2.fft)

# plt.plot(fft["freq"], fft["impedance"])
# plt.plot(fft2.fft["freq"], fft2.fft["impedance"] + 1e7)
# plt.show()