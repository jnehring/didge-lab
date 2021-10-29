from cad.calc.didgmo import PeakFile, didgmo_bridge
from cad.calc.visualization import DidgeVisualizer, FFTVisualiser
import matplotlib.pyplot as plt
from cad.calc.conv import note_to_freq, note_name, freq_to_note
from cad.calc.geo import Geo
from IPython.display import clear_output
import math
import random
import copy
from tqdm import tqdm

from abc import ABC, abstractmethod

class MutationParameter:
    
    def __init__(self, name, value, minimum=None, maximum=None):
        self.name=name
        self.value=value
        self.minimum=minimum
        self.maximum=maximum
        
    def __repr__(self):
        return f"{self.name}={self.value}"

    def toint(self):
        self.value=int(self.value)


class MutationParameterSet(ABC):
    
    def __init__(self):
        self.mutable_parameters=[]
        self.immutable_parameters=[]
        
    @abstractmethod
    def make_geo():
        pass

    # overwrite for custom validation
    def after_mutate(self):
        pass

    def validate(self):
        return True
    
    def copy(self):
        return copy.deepcopy(self)
    
    def get(self, name):
        
        ps=self.mutable_parameters + self.immutable_parameters
        for i in range(len(ps)):
            if ps[i].name == name:
                return ps[i]
        raise Exception("unknown parameter " + name)

    def get_value(self, name):
        return self.get(name).value

    def set(self, name, value, min=None, max=None):
        for i in range(len(self.mutable_parameters)):
            if self.mutable_parameters[i].name == name:
                self.mutable_parameters[i].value = value
                return
        for i in range(len(self.immutable_parameters)):
            if self.immutable_parameters[i].name == name:
                self.immutable_parameters[i].value = value
                return
        raise Exception("cannot find parameter \"" + name + "\"")

    def set_minmax(self, name, min, max):
        for i in range(len(self.mutable_parameters)):
            if self.mutable_parameters[i].name == name:
                self.mutable_parameters[i].min = min
                self.mutable_parameters[i].max = max
                return
        for i in range(len(self.immutable_parameters)):
            if self.immutable_parameters[i].name == name:
                self.immutable_parameters[i].min = min
                self.immutable_parameters[i].max = max
                return
        raise Exception("cannot find parameter \"" + name + "\"")
            
    # def mutate(self, learning_rate):
    #     for i in range(0, len(self.mutable_parameters)):
            
    #         if random.random() < learning_rate:
    #             p=self.mutable_parameters[i]

    #             r=(random.random()-0.5)*2
    #             c=p.maximum-p.value
    #             if r<0:
    #                 c=p.value-p.minimum
    #             p.value += r*c
            
    #     self.after_mutate()            

    def __repr__(self):
        return type(self).__name__ + "\n * " + "\n * ".join(str(x) for x in self.mutable_parameters + self.immutable_parameters)

class BasicShapeParameters(MutationParameterSet):
    
    def __init__(self):
        super(BasicShapeParameters, self).__init__()
        
        #self.mutable_parameters.append(MutationParameter("length", 2500, 1800, 3000))
        self.mutable_parameters.append(MutationParameter("segment_width", 500, 400, 600))
        self.mutable_parameters.append(MutationParameter("n_segments", 5, 1, 10))
        self.mutable_parameters.append(MutationParameter("f", 0.6, 0.0, 1.0))     
        self.mutable_parameters.append(MutationParameter("bell_d", 1.5, 1.0, 2.5))
        self.mutable_parameters.append(MutationParameter("max_d", 80, 50, 100))
        self.mutable_parameters.append(MutationParameter("bell_x", 200, 100, 300))
        self.immutable_parameters.append(MutationParameter("d1", 32))
        
    def make_geo(self):
        shape=[
            [0, self.get("d1").value]
        ]
        f=self.get("f").value
        for i in range(self.get("n_segments").value):
            x_delta=1.25-(((f+2*i/10)*10)%10)/10
            x=shape[-1][0] + self.get("segment_width").value*x_delta
            d_delta=1.25+(((f+2*i/10)*10)%10)/1000
            d=shape[-1][1]*d_delta
            shape.append([x,d])
            i+=1
        
        shape.append([shape[-1][0] + self.get("bell_x").value, shape[-1][1]*self.get("bell_d").value])
        
        scaling=self.get("max_d").value / max([x[1] for x in shape])
        for i in range(1,len(shape)):
            shape[i][1]*=scaling
        return Geo(geo=shape)
                           
    def after_mutate(self):
        self.get("n_segments").toint()
