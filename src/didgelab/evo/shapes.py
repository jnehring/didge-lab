from abc import ABC, abstractmethod
import copy
import pandas as pd
import numpy as np

from didgelab.app import get_app
from didgelab.calc.geo import Geo, geotools

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


class Shape(ABC):
    
    def __init__(self):
        self.parameters=[]
        self.loss = None
        get_app().register_service(self)
        
    @abstractmethod
    def make_geo():
        pass

    def after_mutate(self):
        pass

    def before_mutate(self):
        pass

    def copy(self):
        return copy.deepcopy(self)
    
    def get(self, name):
        for i in range(len(self.parameters)):
            if self.parameters[i].name == name:
                return self.parameters[i]
        return None

    def has_value(self, name):
        ps=self.parameters
        for i in range(len(ps)):
            if ps[i].name == name:
                return True
        return False

    def get_value(self, name):      
        return self.get(name).value

    def toint(self, name):
        val=self.get_value(name)
        val=round(val)
        self.set(name, val)

    def add_param(self, name, minimum, maximum, value=None):
        if value==None:
            value=minimum+(maximum-minimum)/2

        self.parameters.append(MutationParameter(name, value, minimum, maximum))

    def set(self, name, value, min=None, max=None):
        for i in range(len(self.parameters)):
            if self.parameters[i].name == name:
                self.parameters[i].value = value
                return
        raise Exception("cannot find parameter \"" + name + "\"")

    def set_minmax(self, name, min, max):
        for i in range(len(self.parameters)):
            if self.parameters[i].name == name:
                self.parameters[i].minimum = min
                self.parameters[i].maximum = max
                return
        raise Exception("cannot find parameter \"" + name + "\"")
    
    def to_pandas(self):
        df={"name": [], "value": [], "min": [], "max": []}
        for p in self.parameters:

            df["name"].append(p.name)
            df["value"].append(p.value)
            df["min"].append(p.minimum)
            df["max"].append(p.maximum)

        df=pd.DataFrame(df)
        for c in ["value", "min", "max"]:
            df[c]=df[c].apply(lambda x : f"{x:.2f}")
        return df

    def read_csv(self, infile):
        df=pd.read_csv(infile)
        self.parameters=[]
        for ix, row in df.iterrows():
            self.add_param(row["name"], row["min"], row["max"], value=row["value"])
        
    def __repr__(self):

        df=self.to_pandas()
        return str(df)


class BasicShape(Shape):
    
    def __init__(
            self,
            n_bubbles=1,
            n_bubble_segments=10,
            n_segments = 10,
            min_length = 1000,
            max_length = 2000,
            d1 = 32,
            min_bellsize = 65,
            max_bellsize = 80
        ):
        
        Shape.__init__(self)

        self.d1=32
        self.n_segments = n_segments
        
        self.add_param("length", min_length, max_length)
        self.add_param("bellsize", min_bellsize, max_bellsize)
        self.add_param("power", 1,2)
        
        self.add_param("widening_1_x", 0.3, 0.5)
        self.add_param("widening_1_y", 1.0, 1.3)
        self.add_param("widening_2_x", 0.6, 0.8)
        self.add_param("widening_2_y", 1.0, 1.3)
        
        self.n_bubbles=n_bubbles
        self.n_bubble_segments=10
        for i in range(self.n_bubble_segments):
            self.add_param(f"bubble{i}_width", 100, 200)
            self.add_param(f"bubble{i}_height", 0, 15)
            self.add_param(f"bubble{i}_pos", -0.3, 0.3)
        
    def make_geo(self):
        length = self.get_value("length")
        bellsize = self.get_value("bellsize")

        x = length*np.arange(self.n_segments+1)/self.n_segments
        y= np.arange(self.n_segments+1)/self.n_segments
        
        
        p = self.get_value("power")
        y = np.power(y, p)
        y = np.power(y, p)
        y = np.power(y, p)
        y = self.d1 + y*(bellsize - self.d1)
        
        widenings = length*np.array([[self.get_value(f"widening_{i}_x"), self.get_value(f"widening_{i}_y")] for i in range(1,3)])

        for w in widenings:
            geo = list(zip(x,y))
            d=geotools.diameter_at_x(Geo(geo), w[0])
            
            add_d = w[1]*d - d
            for i in range(len(geo)):
                if geo[i][0] >= w[0]:
                    break
            
            x = np.concatenate((x[0:i], [w[0]], x[i:]))
            y_right = np.concatenate(([d], y[i:])) + add_d
            y = np.concatenate((y[0:i], y_right))
        
            y[i:] /= y[-1]/bellsize
            
        shape = list(zip(x,y))
        
        bubble_length = length-100

        for i in range(self.n_bubbles):
            
            width = self.get_value(f"bubble{i}_width")
            height = self.get_value(f"bubble{i}_height")
            pos = self.get_value(f"bubble{i}_pos")
                
            x = width * np.arange(self.n_bubble_segments)/self.n_bubble_segments
            y = height * np.sin(np.arange(self.n_bubble_segments)*np.pi/self.n_bubble_segments)
            
            x += bubble_length * i/self.n_bubbles
            x += (0.5+pos)*bubble_length/self.n_bubbles
                        
            if x[0] < 0:
                x += -1*x[0]
                x += 1
            if x[-1] > bubble_length:
                x -= x[-1] - (bubble_length)
            
            geo = Geo(shape)
            y += np.array([geotools.diameter_at_x(geo, _x) for _x in x])
            
            shape = list(filter(lambda a : a[0]<x[0] or a[0]>x[-1], shape))
            shape.extend(zip(x,y))
            shape = sorted(shape, key=lambda x : x[0])
        
        return Geo(shape)
    
class DetailShape(Shape):
    
    def __init__(self, father_shape : Shape):
        Shape.__init__(self)
        
        geo = father_shape.make_geo().geo
        self.d1 = geo[0][1]
        self.num_segments = len(geo)
        for i in range(1, len(geo)):
            x=geo[i][0]
            minx = 0.8*x
            maxx = 1.2*x
            self.add_param(f"x{i}", minx, maxx, value=x)
            
            y=geo[i][1]
            miny = 0.8*y
            maxy = 1.2*y
            self.add_param(f"y{i}", miny, maxy, value=y)
            
            
    def make_geo(self):
        x = [0]
        y = [self.d1]
        for i in range(1, self.num_segments):
            x.append(self.get_value(f"x{i}"))
            y.append(self.get_value(f"y{i}"))
        geo = list(zip(x,y))
        geo = sorted(geo, key=lambda x : x[0])
        return Geo(geo)
            