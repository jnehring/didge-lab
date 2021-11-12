from cad.calc.geo import Geo, geotools
from cad.calc.didgmo import didgmo_high_res, didgmo_bridge
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
from cad.calc.visualization import DidgeVisualizer
from scipy import interpolate
import numpy as np
import sys
from cad.calc.parameters import MutationParameterSet
from collections.abc import Iterable


# x=list(np.arange(0, 20, 0.1))
# y=sigmoid(x)
# x,y=stretch(100, 10)
# print(x)
# print(y)

# plt.figure()
# plt.plot(x, y)
# plt.axis([-5, 105, -5, 105])
# plt.title('Cubic-spline interpolation')
# plt.show()


class RoundedDidge(MutationParameterSet):

    def __init__(self):
        super(RoundedDidge, self).__init__()

        max_n_segments=10
        self.add_param("n_segments", 1, max_n_segments, value=3)
        self.add_param("length", 1300, 3000)
        self.add_param("bellsize", 80, 300)
        self.add_param("straight_length", 1000, 2000)
        self.add_param("straight_widening", 1, 3)
        for i in range(max_n_segments):
            self.add_param(f"{i}length", 1000, 2000)
            self.add_param(f"{i}wide", 1, 3)
        self.add_param("bell", 0.2, 1)

        self.set("2wide", 3)

    def after_mutate():
        self.toint("bell")
        self.toint("length")
        self.toint("bellsize")

    def sigmoid(self, x):
        return 0.5*(1+math.tanh((x)/2))

    def make_curve(self, length, height, offset_x=0, offset_y=0, end=1.0, n_points=10):
        shape=[]

        start=0.0
        interval=(end-start)/n_points
        for a in np.arange(start, end+interval, interval):
            x=a*length + offset_x
            y=height*self.sigmoid((a*10)-5) + offset_y
            shape.append([x,y])
        return shape

    def make_geo(self):

        shape=[[0, 32]]
        x=self.get_value("straight_length")
        y=shape[-1][1] * self.get_value("straight_widening")
        shape.append([x,y])

        n_segments=self.get_value("n_segments")
        for i in range(n_segments):
            seg_length=1000
            seg_height=30
            bell=1
            if i==n_segments-1:
                bell=self.get_value("bell")
            new_shape=self.make_curve(seg_length, seg_height, offset_x=shape[-1][0], offset_y=shape[-1][1], end=bell)
            shape.extend(new_shape)

        geo=Geo(geo=shape)
        geo=geotools.scale_length(geo, self.get_value("length"))
        if geo.geo[-1][1]>self.get_value("bellsize"):
            geo=geotools.scale_diameter(geo, self.get_value("bellsize"))
        return geo

rd=RoundedDidge()
print(rd)
geo=rd.make_geo()
print(geo.geo[-1])
DidgeVisualizer.vis_didge(geo)
plt.show()





# geo=[[0,32], [1400, 50], [1900, 60], [2300, 120]]
# geo=Geo(geo=geo)
# DidgeVisualizer.vis_didge(geo)
# plt.show()


# df={"x": [], "y": [], "series": []}
# n=5


# peaks=pd.DataFrame(peaks)
# print(peaks)
# df=pd.DataFrame(df)
# sns.lineplot(data=df, x="x", y="y", hue="series")
# plt.show()
# #print(pd.DataFrame(df))
# #geotools.print_geo_summary(geo, fft.peaks)
