import unittest
import configparser 
import os
import matplotlib.pyplot as plt

from cad.calc.visualization import DidgeVisualizer
from cad.calc.geo import Geo
from cad.common.app import App

# python -m unittest cad.tests.visualizer
class TestDidgeVisualizer(unittest.TestCase):

    def test(self):

        geo=[[0,32],
            [800,32],
            [900,38],
            [970,42],
            [1050,40],
            [1180,48],
            [1350,60],
            [1390,68],
            [1500,72]]
        geo=Geo(geo=geo)
        g=DidgeVisualizer.vis_didge(geo)

        path = os.path.join(App.get_config()["TEST"]["temp_dir"], "test.png")
        plt.savefig(path)