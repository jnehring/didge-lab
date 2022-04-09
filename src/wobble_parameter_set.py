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


class WobbleShape(MutationParameterSet):

    def __init__(self):
        MutationParameterSet.__init__(self)

        self.d0=32
        self.resolution=20 # a segment every 20 cm

        self.add_param("length", 1300, 1900)
        self.add_param("bell_size", self.d0, 90)
        self.add_param("bell_width", 100, 300)
        
        self.num_widens=10
        self.widen_prob=0.5
        self.add_param("num_widens", 0, self.num_widens)
        for i in range(self.num_widens):
            self.add_param(f"{i}_widen_x", 0.1, 1)
            self.add_param(f"{i}_widen_y", 0.9, 1.2)
            self.add_param(f"{i}_widen_on", 0, 1)
        self.last_num_widens=self.get_value("num_widens")
        
        self.num_bubbles=5
        self.bubble_prob=0.5
        self.add_param("num_bubbles", 0, self.num_bubbles)
        for i in range(self.num_bubbles):
            self.add_param(f"{i}_bubble_startx", 0, 1)
            self.add_param(f"{i}_bubble_endx", 0, 1)
            self.add_param(f"{i}_bubble_height", -1, 3)
            #self.add_param(f"{i}_bubble_cutx", 0.1, 1)
            self.add_param(f"{i}_bubble_on", 0, 1)

        self.last_num_bubbles=self.get_value("num_bubbles")

    def add_shape_to_geo(self, startx, endx, x, y, shape):
        l_didge=shape[-1][0]
        l_shape=x[-1]-x[0]
        
        new_shape=[]
        norm=(endx-startx)

        geo=Geo(shape)
        for i in range(len(x)):
            xpos=startx + (x[i]/l_shape)*norm
            ypos=geotools.diameter_at_x(geo, xpos)*y[i]
            new_shape.append([xpos, ypos])
        
        old_shape=[]
        for s in shape:
            if s[0]<startx or s[0]>endx:
                old_shape.append(s)
        new_shape.extend(old_shape)
        new_shape=self.sort_segments(new_shape)
        return new_shape

    def sort_segments(self, shape):
        return sorted(shape, key=lambda x : x[0])

    def add_bubble(self, shape, startx, endx, height):
        cut_x=1

        startx=startx*shape[-1][0]
        endx=endx*shape[-1][0]

        if startx>endx:
            a=startx
            startx=endx
            endx=a

        l=np.pi*cut_x
        x=np.arange(0, l, l/self.resolution)
        y=np.sin(x)*height

        return self.add_shape_to_geo(startx, endx, x, y, shape)

    def add_bell(self, shape, bell_width):
        l=shape[-1][0]

        x=np.arange(0, bell_width, bell_width/self.resolution)
        y=[a/bell_width for a in x]

        shape=self.add_shape_to_geo(l-bell_width, l, x, y, shape)
        return shape

    def widen(self, shape, x, y_factor):
        x=shape[-1][0]*x
        y=geotools.diameter_at_x(shape, x)
        y_diff=y**y_factor-y

        print("y_diff", y_diff, x)

        add_point=True
        i=0
        len_shape=len(shape)
        while i <len_shape:

            if shape[i][0]==x:
                shape[i]+=y_diff
                add_point=False

            if shape[i][0]>=x:
                if add_point:
                    shape.append([x,y])
                    shape=self.sort_segments(shape)
                    i-=1
                    len_shape+=1

                shape[i][1]+=y_diff

            i+=1
        return shape

    def make_geo(self):

        didge_length=self.get_value("length")
        shape=[[0, 0], [didge_length,1]]
        
        for i in range(self.num_bubbles):
            if self.get_value(f"{i}_bubble_on") < self.bubble_prob:
                startx=self.get_value(f"{i}_bubble_startx")
                endx=self.get_value(f"{i}_bubble_endx")
                height=self.get_value(f"{i}_bubble_height")
                #cutx=self.get_value(f"{i}_bubble_cutx")
                height=3
                shape=self.add_bubble(shape, startx, endx, height)
                # print("add_bubble", startx, endx, height, cutx)

        print("before")

        for i in range(len(shape)):
            print(shape[i])

        for i in range(self.num_widens):
            if self.get_value(f"{i}_widen_on") < self.widen_prob:
                x=self.get_value(f"{i}_widen_x")
                y=self.get_value(f"{i}_widen_y")
                shape=self.widen(shape, x, y)

        for i in range(len(shape)):
            print(shape[i])

        bell_width=self.get_value("bell_width")
        shape=self.add_bell(shape, bell_width)


        # normalize everything so the didge has d0 mouth size and the programmed bell size
        x,y=zip(*shape)
        x=np.array(x)
        y=np.array(y)
        y=y-y[0]
        bell_size=self.get_value("bell_size")
        y=(bell_size-self.d0)*y/y[-1]
        y+=self.d0

        shape=list(zip(x,y))
        return Geo(shape)

        #shape=self.add_bubble(shape, 500, 900, -1, 1)
        # # shape=self.add_bubble(shape, 1300, 1800, 1, 1)
        # # shape=self.widen(shape, 1000, 2)
        # shape=self.add_bell(shape, 300, 2)

        # x,y=zip(*shape)
        # x=np.array(x)
        # y=np.array(y)
        # y=y-y[0]
        # y=(size_bell-d0)*y/y[-1]
        # y+=d0

        # shape=list(zip(x,y))
        # return Geo(shape)

    def after_mutate(self):
        self.toint("num_widens")
        self.toint("num_bubbles")
        self.toint("length")
        self.toint("bell_size")

        # make unused parameters immutable
        # for i in range(self.num_widens):
        #     value=False
        #     if self.get_value(f"{i}_widen_on") >= self.widen_prob:
        #         value=True
        #     self.set_immutable(f"{i}_widen_x", value)
        # for i in range(self.num_bubbles):
        #     value=False
        #     if self.get_value(f"{i}_bubble_on") >= self.bubble_prob:
        #         value=True
            
        #     self.set_immutable(f"{i}_bubble_startx", value)
        #     self.set_immutable(f"{i}_bubble_endx", value)
        #     self.set_immutable(f"{i}_bubble_height", value)
        #     self.set_immutable(f"{i}_bubble_cutx", value)

params=WobbleShape()
mutator=ExploringMutator()

random.seed(0)
for i in range(1):
    print(i)
    mutant=params.copy()
    mutator.mutate(mutant)
    print(mutant)
    geo=mutant.make_geo()   
    plt.clf()
    DidgeVisualizer.vis_didge(geo)
    plt.savefig(f"test/{i}.png")
    plt.show()

# geo=WobbleShape().make_geo()
# plt.show()

# height=0.5
# x=np.arange(-1*height, 0, 1/30)
# y=[np.sqrt(1-a*a) for a in x]

# x+=height
# print(x)




# geo=[[0, 32], [155.79953130903596, 33.32460005042448], [170.8215820902333, 34.57015359728445], [185.84363287143066, 35.73333642718836], [188.02276911222978, 34.36070487122439], [200.865683652628, 36.729252000950865], [215.88773443382536, 37.48597305327159], [230.9097852150227, 37.95049760209339], [245.93183599622006, 38.0932084300103], [260.95388677741744, 37.910461343077316], [275.97593755861476, 37.42507722234471], [290.9979883398121, 36.6846820597922], [306.02003912100946, 35.758014159738096], [321.04208990220684, 34.72948426031741], [677.1111664129595, 37.75676626006363], [693.0931280782052, 37.89264412214574], [1032.838261679418, 38.127141941390526], [1037.950801799321, 38.16232709707329], [1047.5674373130644, 45.74398174063208], [1057.1840728268076, 52.74174572304605], [1066.800708340551, 58.590986714302645], [1076.4173438542941, 62.81834538317274], [1085.1021545387168, 64.86128292570918], [1102.2177058010807, 72.83071736487521], [1107.1839004947822, 72.5314022111478], [1116.917962028583, 88.51995825156418], [1126.6520235623839, 97.24109472261027], [1136.3860850961846, 99.69924683845124], [1146.1201466299854, 102.65589701744919], [1155.854208163786, 105.00287908678668], [1165.588269697587, 114.63551440281357], [1175.3223312313878, 120.4698589236792], [1185.0563927651885, 121.76240145143306], [1194.7904542989895, 115.55622418022816], [1204.5245158327903, 103.96570673648144], [1214.2585773665912, 86.47408439877769], [1222.0265646376272, 87.97187076662885], [1239.142115899991, 86.57585876274737], [1256.257667162355, 81.13992480322048], [1273.3732184247185, 72.98682975996836], [1291.7208627594616, 72.70044169938473], [1310.7252900779908, 70.68457210237827], [1329.72971739652, 67.42934503620285], [1348.7341447150493, 62.34825432624749], [1354.222332825919, 60.78330867411263], [1354.222332825919, 60.78330867411263], [1367.7385720335785, 56.929180616922274], [1376.4796681835483, 59.23194567342132], [1402.6337558056646, 70.72233881641586], [1554.222332825919, 76.42769260802197]]
# geo=Geo(geo)

# # for i in range(len(geo)):
# #     if i>0 and geo[i][0]-geo[i-1][0]==0:
# #         print("*")
# #     print(geo[i])
# print(geo.get_cadsd().get_notes())

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