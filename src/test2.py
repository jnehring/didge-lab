from cad.cadsd.cadsd import CADSDResult
from cad.calc.geo import Geo
import matplotlib.pyplot as plt
from cad.calc.didgmo import didgmo_high_res, didgmo_bridge
import time
from cad.calc.parameters import RoundedDidge
from cad.calc.loss import ScaleLoss
import pickle
from cad.calc.visualization import DidgeVisualizer

pool=pickle.load(open("projects/temp/evolve_penta3.pkl", "rb"))
pool=sorted(pool, key=lambda x :x[1])

folder="projects/temp/"
for i in range(len(pool)):
    print(i)
    geo=pool[i][0].make_geo()
    DidgeVisualizer.vis_didge(geo)
    plt.savefig(folder + str(i)+".png")
    plt.cla()
    cadsd=CADSDResult.from_geo(geo)
    cadsd.print_summary()
    print("------------")
#x=input()

#for p in pool:
#    print(p[1])
#    print("-"*20)
#geo=[[0.0, 32], [938.0460250509619, 36.30772939865612], [978.3936102254993, 37.4497986469184], [1059.641456576859, 48.91827996643648], [1112.6692850229392, 48.87975363899729], [1164.9621284185812, 62.573707924639336], [1036.3583997396584, -112.15069374439821], [1076.1846321708429, -65.88867037098234], [1116.0108646020276, -18.357985775965012], [1155.837097033212, 30.224390547821628], [1195.6633294643968, 79.43990870361074], [1235.4895618955813, 128.7363810356204], [1275.315794326766, 177.51602088852604], [1315.1420267579506, 225.23163277104024], [1354.968259189135, 271.4778503038715], [1394.7944916203198, 316.06480308968696], [1434.6207240515043, 359.06367461532454], [1259.7896795029342, 70.012163619489], [1315.022523217202, 77.40540873334558], [1353.2499090368483, 75.96894981933212], [1432.8269233790313, 104.64176562366376], [1508.6359335957436, 103.96678723753345], [1546.8158336741524, 107.06197447066994], [1579.0088711821923, 110.42672447615287], [1612.2942716675134, 131.47540187559406], [1673.9357968316556, 141.57215009400383], [1741.2584499230493, 149.14866143313182], [2009.0, 167.75192976975381]]
#geo=Geo(geo=geo)
#loss=ScaleLoss(scale=[0,3,5,7,10], fundamental=-31, n_peaks=8, octave=True)
#loss.get_loss(geo)
#cadsd=CADSDResult.from_geo(geo)

#geo=[[0.0, 32], [903.4265490017885, 44.74696440831961], [1043.2783924481641, 43.520495439677866], [1167.5572483229255, 56.05287987234595], [1265.8172834833592, 59.372000817740116], [1361.0641095223732, 75.9832280080771], [1424.7784835799014, 79.32653417809952], [1531.5316609725612, 110.29806559536875], [1634.4641691886077, 117.651508890613], [1785.0643420008407, 143.5795381422663], [1907.2298859137284, 196.87608436044138], [2113.0, 198.08650024980747]]
#geo=Geo(geo=geo)

#cadsd=CADSDResult.from_geo(geo)

# t1=time.time()
#fft=get_impedance_spektrum(geo.geo, 1, 1000, 1)
# print("fft1", time.time()-t1)

# t1=time.time()
# fft2=didgmo_bridge(geo)
# print("fft2", time.time()-t1, fft2.fft)

# plt.plot(fft["freq"], fft["impedance"])
# plt.plot(fft2.fft["freq"], fft2.fft["impedance"] + 1e7)
# plt.show()