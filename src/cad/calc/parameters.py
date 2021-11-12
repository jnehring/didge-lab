from cad.calc.didgmo import PeakFile, didgmo_bridge
from cad.calc.visualization import DidgeVisualizer, FFTVisualiser
import matplotlib.pyplot as plt
from cad.calc.conv import note_to_freq, note_name, freq_to_note
from cad.calc.geo import Geo, geotools
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

    def toint(self, name):
        val=self.get_value(name)
        val=round(val)
        self.set(name, val)

    def add_param(self, name, minimum, maximum, value=None):
        if value==None:
            value=minimum+(maximum-minimum)/2
        self.mutable_parameters.append(MutationParameter(name, value, minimum, maximum))

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
        
        self.mutable_parameters.append(MutationParameter("length", 2500, 2000, 3000))
        self.mutable_parameters.append(MutationParameter("segment_width", 500, 200, 300))
        self.mutable_parameters.append(MutationParameter("n_segments", 5, 5, 15))
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

        length=shape[-1][0]
        scaling=self.get_value("length")/length
        for i in range(len(shape)):
            shape[i][0]*=scaling

        return Geo(geo=shape)
                           
    def after_mutate(self):
        self.get("n_segments").toint()


class BubbleParameters(MutationParameterSet):

    def __init__(self, geo, pos=0.5, height=1.5, width=200):
        self.geo=geo
        super(BubbleParameters, self).__init__()
        
        #self.mutable_parameters.append(MutationParameter("length", 2500, 1800, 3000))
        self.mutable_parameters.append(MutationParameter("pos", pos, 0, 1))
        self.mutable_parameters.append(MutationParameter("height", height, 1, 2))
        self.mutable_parameters.append(MutationParameter("width", width, 50, 300))     
    
    def make_geo(self):
        shape=self.geo.copy().geo

        for index in range(len(shape)):
            if shape[index][0]>self.geo.length()*self.get_value("pos"):
                break

        x4=shape[index][0]
        y4=shape[index][1]
        x0=shape[index-1][0]
        y0=shape[index-1][1]

        alpha=math.atan(0.5*(y4-y0)/(x4-x0))

        x2=self.geo.length()*self.get_value("pos")
        x1=self.geo.length()*self.get_value("pos")-self.get_value("width")/2
        x3=self.geo.length()*self.get_value("pos")+self.get_value("width")/2

        def limit_point(x):
            if x<0:
                return 1
            elif x>self.geo.length():
                return self.geo.length()-1
            else:
                return x

        x1=limit_point(x1)
        x2=limit_point(x2)
        x3=limit_point(x3)
        
        get_y = lambda x : 2*(0.5*y0 + math.tan(alpha)*(x-x0))
        y1=get_y(x1)
        y2=get_y(x2)*self.get_value("height")
        y3=get_y(x3)

        add_point = lambda x,y : new_shape.append([x,y])

        new_shape=shape[0:index]
        add_point(x1, y1)
        add_point(x2, y2)
        add_point(x3, y3)
        new_shape.extend(shape[index:])

        new_shape=sorted(new_shape, key=lambda x : x[0])

        return Geo(geo=new_shape)

class MultiBubble(MutationParameterSet):

    def __init__(self, geo, n_bubbles):
        super(MultiBubble, self).__init__()
        self.geo=geo
        self.n_bubbles=n_bubbles
        for i in range(n_bubbles):
            si=str(i)
            self.mutable_parameters.append(MutationParameter(si+"pos", 0.5, 0, 1))
            self.mutable_parameters.append(MutationParameter(si+"height", 1, 0.2, 3))
            self.mutable_parameters.append(MutationParameter(si+"width", 200, 50, 400))

    def set_values(self, key, values):
        assert len(values) == self.n_bubbles
        for i in range(self.n_bubbles):
            si=str(i)
            self.set(si+key, values[i])

    def make_geo(self):
        geo=self.geo.copy()
        for i in range(self.n_bubbles):
            si=str(i)
            bp=BubbleParameters(geo, pos=self.get_value(si+"pos"), height=self.get_value(si+"height"), width=self.get_value(si+"width"))
            geo=bp.make_geo()

        geo.sort_segments()
        return geo

class ExploringShape(MutationParameterSet):

    def __init__(self):        
        super(ExploringShape, self).__init__()

        self.max_diameter=300
        self.min_length=1500
        self.max_length=3000

    def make_geo(self):

        n_segments=random.randrange(8,20)
        final_length=random.randrange(self.min_length, self.max_length)
        shape=[[0,32]]


        x=final_length*(0.2*random.random() + 0.3)
        y=shape[0][1]*(1+0.2*random.random())
        shape.append([x,y])

        xd=(final_length-x)/n_segments
        for i in range(n_segments-1):
            x=shape[-1][0] + xd*(random.random()+0.5)
            y=shape[-1][1] * (0.5*random.random()+0.9)
            shape.append([x,y])

        bell_y=shape[-1][1] * (1+random.random())
        bell_x=shape[-1][0] + random.randrange(80, 300)
        shape.append([bell_x, bell_y])
            
        geo=Geo(geo=shape)
        geotools.scale_length(geo, final_length)

        if geotools.get_max_d(geo) > self.max_diameter:
            geotools.scale_diameter(geo, self.max_diameter)

        return geo


class EvolveGeoParameter(MutationParameterSet):

    def __init__(self, geo):
        super(EvolveGeoParameter, self).__init__()
        
        self.geo=geo
        for i in range(1, len(self.geo.geo)):
            x=self.geo.geo[i][0]
            y=self.geo.geo[i][1]
            self.mutable_parameters.append(MutationParameter(f"x{i}", x, x*0.3, x*3))
            self.mutable_parameters.append(MutationParameter(f"y{i}", y, y*0.3, y*3))
        
    def make_geo(self):

        shape=[[self.geo.geo[0][0], self.geo.geo[0][1]]]
        for i in range(1, len(self.geo.geo)):
            x=self.get_value(f"x{i}")
            y=self.get_value(f"y{i}")
            shape.append([x,y])

        geo=Geo(geo=shape)
        geo.sort_segments()
        return geo

    def after_mutate(self):
        pass
