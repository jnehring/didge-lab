from abc import ABC, abstractmethod
import copy
import pandas as pd
import numpy as np

from didgelab.app import App
from didgelab.calc.geo import Geo

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
        App.register_service(self)
        
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

class MultiSegmentShape(Shape):
    
    def __init__(self, father_geo=None):
        Shape.__init__(self)
        
        if father_geo is None:
            # create new multisegment shape
            average_length = 1500
            self.n_params = 40
            average_bell_size=75
            self.d1 = 32

            minx = 0.9*average_length/self.n_params
            maxx = 1.1*average_length/self.n_params
            mind = -1.0*(average_bell_size-self.d1)/self.n_params
            maxd = 3.0*(average_bell_size-self.d1)/self.n_params
            for i in range(self.n_params):
                self.add_param(f"x{i}", minx, maxx)
                self.add_param(f"d{i}", mind, maxd)
        else:
            # initialize it from the father
            self.n_params = len(father_geo)-1
            self.d1 = father_geo[0][1]
            for i in range(len(father_geo)-1):
                x = father_geo[i+1][0] - father_geo[i][0]
                d = father_geo[i+1][1] - father_geo[i][1]
                self.add_param(f"x{i}", 0.9*x, 1.1*x, x)
                self.add_param(f"d{i}", 0.9*d, 1.1*d, d)

    def make_geo(self):
        geo = [[0, self.d1]]
        for i in range(self.n_params):
            x=self.get_value(f"x{i}") + geo[i][0] 
            d=self.get_value(f"d{i}") + geo[i][1]
            if d<0.5*self.d1:
                d=0.5*self.d1
            geo.append([x,d])
        return Geo(geo)


class Cylinder(Shape):
    
    def __init__(self, boundaries):
        Shape.__init__(self)
        self.boundaries = boundaries
        self.add_param("length", boundaries.min_length, boundaries.max_length)
        self.add_param("bell_size", boundaries.d1, boundaries.max_bell_diameter)
        
    def make_geo(self):
        geo = [[0,self.boundaries.d1], [self.get_value("length"), self.get_value("bell_size")]]
        return Geo(geo)
    
class Cone(Shape):
    
    def __init__(self, boundaries):
        Shape.__init__(self)
        self.boundaries = boundaries
        self.add_param("length", boundaries.min_length, boundaries.max_length)
        self.add_param("bell_size", boundaries.min_length, boundaries.max_length)
        
    def make_geo(self):
        geo = [[0,self.boundaries.d1], [self.get_value("length"), self.boundaries.d1]]
        return Geo(geo)
    
class MultiSegmentShape(Shape):
    
    def __init__(self, boundaries, father_geo=None):
        Shape.__init__(self)
        
        if father_geo is None:
            # create new multisegment shape
            average_length = (boundaries.max_length + boundaries.min_length)/2
            self.n_params = 40
            average_bell_size = (boundaries.max_bell_diameter + boundaries.d1)/2
            self.d1 = boundaries.d1

            minx = 0.9*average_length/self.n_params
            maxx = 1.1*average_length/self.n_params
            mind = -1.0*(average_bell_size-self.d1)/self.n_params
            maxd = 3.0*(average_bell_size-self.d1)/self.n_params
            for i in range(self.n_params):
                self.add_param(f"x{i}", minx, maxx)
                self.add_param(f"d{i}", mind, maxd)
        else:
            # initialize it from the father
            self.n_params = len(father_geo)-1
            self.d1 = father_geo[0][1]
            for i in range(len(father_geo)-1):
                x = father_geo[i+1][0] - father_geo[i][0]
                d = father_geo[i+1][1] - father_geo[i][1]
                self.add_param(f"x{i}", 0.9*x, 1.1*x, x)
                self.add_param(f"d{i}", 0.9*d, 1.1*d, d)

    def make_geo(self):
        geo = [[0, self.d1]]
        for i in range(self.n_params):
            x=self.get_value(f"x{i}") + geo[i][0] 
            d=self.get_value(f"d{i}") + geo[i][1]
            if d<0.5*self.d1:
                d=0.5*self.d1
            geo.append([x,d])
        return Geo(geo)
    
class WideningShape(Shape):
    
    def __init__(self):
        
        Shape.__init__(self)

        self.d1=32
        self.n_segments = 10
        
        self.add_param("length", 1450, 1600)
        self.add_param("bellsize", 65, 80)
        self.add_param("power", 1,2)
        
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
        
        geo = list(zip(x,y))
        
        return Geo(geo)

