from cad.calc.didgmo import PeakFile, didgmo_bridge
import matplotlib.pyplot as plt
from cad.calc.conv import note_to_freq, note_name, freq_to_note
from cad.calc.geo import Geo, geotools
from IPython.display import clear_output
import math
import random
import copy
from tqdm import tqdm
import numpy as np
from abc import ABC, abstractmethod
import pandas as pd
import logging

class MutationParameter:
    
    def __init__(self, name, value, minimum=None, maximum=None, immutable=False):
        self.name=name
        self.value=value
        self.minimum=minimum
        self.maximum=maximum
        self.immutable=immutable
        
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

    def after_mutate(self):
        pass

    def before_mutate(self):
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
        return None

    def has_value(self, name):
        ps=self.mutable_parameters + self.immutable_parameters
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

    def add_param(self, name, minimum, maximum, value=None, immutable=False):
        if value==None:
            value=minimum+(maximum-minimum)/2

        self.mutable_parameters.append(MutationParameter(name, value, minimum, maximum, immutable=immutable))

    def is_mutable(self, name):
        for i in range(len(self.mutable_parameters)):
            if self.mutable_parameters[i].name == name:
                if hasattr(self.mutable_parameters[i], "immutable"):
                    return self.mutable_parameters[i].immutable
                else:
                    return True
        for i in range(len(self.immutable_parameters)):
            if self.immutable_parameters[i].name == name:
                return False
        raise Exception("cannot find parameter \"" + name + "\"")


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
                self.mutable_parameters[i].minimum = min
                self.mutable_parameters[i].maximum = max
                return
        for i in range(len(self.immutable_parameters)):
            if self.immutable_parameters[i].name == name:
                self.immutable_parameters[i].minimum = min
                self.immutable_parameters[i].maximum = max
                return
        raise Exception("cannot find parameter \"" + name + "\"")
    
    def to_pandas(self):
        df={"name": [], "value": [], "min": [], "max": [], "mutable": []}
        for p in self.mutable_parameters + self.immutable_parameters:

            df["name"].append(p.name)
            df["value"].append(p.value)
            df["min"].append(p.minimum)
            df["max"].append(p.maximum)
            df["mutable"].append(self.is_mutable(p.name))

        df=pd.DataFrame(df)
        for c in ["value", "min", "max"]:
            df[c]=df[c].apply(lambda x : f"{x:.2f}")
        return df
        
    def __repr__(self):

        df=self.to_pandas()
        return str(df)

        #return type(self).__name__ + "\n * " + "\n * ".join(str(x) for x in self.mutable_parameters + self.immutable_parameters)

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
        
        # scaling=self.get("max_d").value / max([x[1] for x in shape])
        # for i in range(1,len(shape)):
        #     shape[i][1]*=scaling

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

        self.mutated_geo=None
        
    def make_geo(self):
        if self.mutated_geo is not None:
            return self.mutated_geo
        shape=[[self.geo.geo[0][0], self.geo.geo[0][1]]]
        for i in range(1, len(self.geo.geo)):
            x=self.get_value(f"x{i}")
            y=self.get_value(f"y{i}")
            shape.append([x,y])

        geo=Geo(geo=shape)
        geo.sort_segments()
        self.mutated_geo=geo
        return self.mutated_geo

    def after_mutate(self):
        self.mutated_geo=None
        pass

class AddBubble(MutationParameterSet):

    def __init__(self, geo):
        super(AddBubble, self).__init__()
        
        self.geo=geo
        self.add_param("n_bubbles", 1, 5)

        for i in range(0, 5):
            self.mutable_parameters.append(MutationParameter(f"{i}pos", 0.5, 0, 1))
            self.mutable_parameters.append(MutationParameter(f"{i}width", 0.5, 0.4, 0.9))
            self.mutable_parameters.append(MutationParameter(f"{i}height", 0.3, 0.1, 0.5))
    
    # return last index that is smaller than x
    def get_index(self, shape, x):
        for i in range(len(shape)):
            if shape[i][0]>x:
                return i
        return len(shape)-1

    def get_y(self, shape, x):
        i=self.get_index(shape, x)
        xa=shape[i-1][0]
        xe=shape[i][0]
        ya=shape[i-1][1]
        ye=shape[i][1]
        alpha=math.atan(0.5*(ye-ya) / (xe-xa))

        xd=x-xa
        y=ya + 2*xd*math.tan(alpha)
        return y

    def make_bubble(self, shape, pos, width, height):

        n_segments=11

        i=self.get_index(shape, pos-0.5*width)

        bubbleshape=shape[0:i]

        x=pos-0.5*width
        y=geotools.diameter_at_x(Geo(geo=shape), x)

        if shape[i-1][0]<x:
            bubbleshape.append([x,y])

        for j in range(1, n_segments):
            x=pos-0.5*width + j*width/n_segments

            # get diameter at x
            y=geotools.diameter_at_x(Geo(geo=shape), x)
            factor=1+math.sin(j*math.pi/(n_segments))*height
            y*=factor

            bubbleshape.append([x,y])

        x=pos+0.5*width
        y=geotools.diameter_at_x(Geo(geo=shape), x)
        bubbleshape.append([x,y])

        while shape[i][0]<=bubbleshape[-1][0]+1:
            i+=1
        
        bubbleshape.extend(shape[i:])

        return bubbleshape
        
    def make_geo(self):

        geo=self.geo.copy()
        shape=geo.geo
        bubble_segment_width=geo.length()/self.get_value("n_bubbles")

        for i in range(self.get_value("n_bubbles")):

            width=self.get_value(f"{i}width")*bubble_segment_width
            height=self.get_value(f"{i}height")

            pos=self.get_value(f"{i}pos")
            
            min_pos=i*bubble_segment_width+width/2
            max_pos=(i+1)*bubble_segment_width-width/2
            
            
            pos=min_pos + pos*(max_pos-min_pos)

            if pos-width/2<bubble_segment_width*i:
                pos=i*bubble_segment_width+width/2

            if pos+width/2>bubble_segment_width*(i+1):
                pos=(i+1)*bubble_segment_width-width/2

            shape=self.make_bubble(shape, pos, width, height)

        return Geo(geo=shape)

    def after_mutate(self):
        self.toint("n_bubbles")


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

    def after_mutate(self):
        self.toint("length")
        self.toint("bellsize")
        self.toint("n_segments")

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
                new_shape=new_shape[1:]
                shape.extend(new_shape)

        geo=Geo(geo=shape)
        geo=geotools.scale_length(geo, self.get_value("length"))
        if geo.geo[-1][1]>self.get_value("bellsize"):
            geo=geotools.scale_diameter(geo, self.get_value("bellsize"))
        return geo

class FinetuningParameters(MutationParameterSet):

    def __init__(self, geo):
        super(FinetuningParameters, self).__init__()

        for i in range(0, len(geo.geo)):
            p=geo.geo[i]
            self.add_param(f"x{i}", p[0]*0.8, p[0]*1.2)
            self.add_param(f"y{i}", p[1]*0.8, p[1]*1.2)
            self.set(f"x{i}", p[0])
            self.set(f"y{i}", p[1])
        self.get("x0").immutable=True
        self.get("y0").immutable=True

    def make_geo(self):
        geo=[]
        i=0
        while True:
            if not self.has_value(f"x{i}") :
                break
            x=self.get_value(f"x{i}")
            y=self.get_value(f"y{i}")
            geo.append([x,y])
            i+=1

        geo=Geo(geo=geo)
        geo.sort_segments()
        return geo


class RandomDidgeParameters(MutationParameterSet):
    
    def __init__(self):
        MutationParameterSet.__init__(self)
        
        self.add_param("length", 1000, 1700)
        self.add_param("bell_width", 50, 300)
        self.add_param("n_segments", 2, 20)
        self.add_param("first_segment", 0.2, 0.8)
        self.add_param("d1", 0,0, value=32, immutable=True)
    
    def after_mutate(self):
        self.get("n_segments").toint()
        
    def make_geo(self):
        self.get("n_segments").toint()

        shape=[
            [0, self.get("d1").value]
        ]

        y=np.random.sample(self.get_value("n_segments"))

        target_width=self.get_value("bell_width")-self.get_value("d1")
        y=y/y.sum()
        offset=0
        for i in range(len(y)):
            y[i]+=offset
            offset=y[i]
        y*=target_width
        y+=self.get_value("d1")

        x=np.random.sample(self.get_value("n_segments")-1)
        x=x/x.sum()
        x*=(1-self.get_value("first_segment"))
        x=np.concatenate([[self.get_value("first_segment")], x])
        x*=self.get_value("length")

        offset=0
        for i in range(len(x)):
            x[i]+=offset
            offset=x[i]

        for i in range(len(x)):
            shape.append([x[i], y[i]])

        return Geo(geo=shape)
                           
    def after_mutate(self):
        self.get("n_segments").toint()

class ConeMutationParameter(MutationParameterSet):

    def __init__(self):
        MutationParameterSet.__init__(self)
        self.add_param("length", 1200, 2800)
        self.add_param("bell_width", 40, 120)
        self.add_param("min_t", -10, 0)
        self.add_param("max_t",0.01, 10)

        self.d1=32
        
    def make_geo(self):
        n_segments=20

        geo=[]
        min_t=self.get_value("min_t")
        max_t=self.get_value("max_t")
        t_diff=max_t-min_t
        max_y=(math.pow(2, (t_diff*n_segments/(n_segments+1))+min_t))-math.pow(2, min_t)
        for i in range(n_segments+1):
            x=self.get_value("length")*i/n_segments
            y=((math.pow(2, (t_diff*i/(n_segments+1))+min_t))-math.pow(2, min_t))/max_y
            y*=(self.get_value("bell_width")-self.d1)
            y+=self.d1
            geo.append([x,y])
        return Geo(geo=geo)

class ConeBubble(MutationParameterSet):
    def __init__(self, father_cone, father_bubble):
        MutationParameterSet.__init__(self)
        
        self.father_cone=father_cone
        self.father_bubble=father_bubble

        for father in [father_cone, father_bubble]:
            for param in father.mutable_parameters:
                self.add_param(param.name, param.minimum, param.maximum, param.value, param.immutable)

        self.after_mutate()
    
    def after_mutate(self):
        for param in self.mutable_parameters:
            try:
                self.father_cone.set(param.name, param.value)
                self.father_bubble.set(param.name, param.value)
            except Exception as e:
                continue
            
        self.father_cone.after_mutate()
        self.father_bubble.after_mutate()

    def make_geo(self):
        self.father_bubble.geo=self.father_cone.make_geo()
        return self.father_bubble.make_geo()

class IringaShape(MutationParameterSet):

    def __init__(self):
        MutationParameterSet.__init__(self)

        self.d1=32
        self.add_param("length", 1500, 3000)
        self.add_param("bell_size", 70, 120)
        self.add_param("x0", 0.4, 0.7)
        self.add_param("y0", 1.0, 1.3)

        self.n_segments=8
        #self.add_param("n_segments", 3, self.max_n_segments)

        for i in range(1, self.n_segments):
            self.add_param(f"x{i}", 0.1, 0.9)
            self.add_param(f"y{i}", 0.1, 0.9)

    def make_geo(self):
        shape=[[0, self.d1]]
        x0=self.get_value("length")*self.get_value("x0")
        y0=self.d1*self.get_value("y0")
        shape.append([x0,y0])

        x_left=self.get_value("length")-x0
        y_left=self.get_value("bell_size")-y0

        x_sum=sum([self.get_value(f"x{i}") for i in range(1, self.n_segments)])
        y_sum=sum([self.get_value(f"y{i}") for i in range(1, self.n_segments)])

        for i in range(1, self.n_segments):
            x=x0+self.get_value(f"x{i}")*x_left/x_sum
            y=y0+self.get_value(f"y{i}")*y_left/y_sum
            x0=x
            y0=y
            shape.append([x,y])
        return Geo(geo=shape)        

    def after_mutate(self):
        pass

class MbeyaShape(MutationParameterSet):

    def __init__(self):
        MutationParameterSet.__init__(self)

        self.d1=32
        # straight part
        self.add_param("l_gerade", 500, 1500)
        self.add_param("d_gerade", 0.9, 1.2)

        # opening part
        self.add_param("n_opening_segments", 0, 8)
        self.add_param("opening_factor_x", -2, 2)
        self.add_param("opening_factor_y", -2, 2)
        self.add_param("opening_length", 700, 1000)

        # bell
        self.add_param("d_pre_bell", 40, 50)
        self.add_param("l_bell", 20, 50)
        self.add_param("bellsize", 5, 30)

        # bubble
        self.add_param("add_bubble", 0, 1)
        self.add_param("bubble_height", 0, 1)
        self.add_param("bubble_pos", 0, 1)
        self.add_param("bubble_width", 0, 300)

    def make_bubble(self, shape, pos, width, height):

        n_segments=11

        i=self.get_index(shape, pos-0.5*width)

        bubbleshape=shape[0:i]

        x=pos-0.5*width
        y=geotools.diameter_at_x(Geo(geo=shape), x)

        if shape[i-1][0]<x:
            bubbleshape.append([x,y])

        for j in range(1, n_segments):
            x=pos-0.5*width + j*width/n_segments

            # get diameter at x
            y=geotools.diameter_at_x(Geo(geo=shape), x)
            factor=1+math.sin(j*math.pi/(n_segments))*height
            y*=factor

            bubbleshape.append([x,y])

        x=pos+0.5*width
        y=geotools.diameter_at_x(Geo(geo=shape), x)
        bubbleshape.append([x,y])

        while shape[i][0]<=bubbleshape[-1][0]+1:
            i+=1
        
        bubbleshape.extend(shape[i:])

        return bubbleshape

    # return last index that is smaller than x
    def get_index(self, shape, x):
        for i in range(len(shape)):
            if shape[i][0]>x:
                return i
        return len(shape)-1

    def make_geo(self):
        shape=[[0, self.d1]]

        # straight part
        p=[self.get_value("l_gerade"), shape[-1][1]*self.get_value("d_gerade")]
        shape.append(p)

        # opening part
        n_seg=self.get_value("n_opening_segments")
        seg_x=[]
        seg_y=[]
        for i in range(int(n_seg)):
            x=pow(i+1, self.get_value("opening_factor_x"))
            y=pow(i+1, self.get_value("opening_factor_y"))
            seg_x.append(x)
            seg_y.append(y)

        def normalize(arr):
            m=sum(arr)
            return [x/m for x in arr]

        seg_x=normalize(seg_x)
        seg_y=normalize(seg_y)
        seg_x=[x*self.get_value("opening_length") for x in seg_x]
        seg_y=[y*self.get_value("d_pre_bell") for y in seg_y]

        start_x=shape[-1][0]
        start_y=shape[-1][1]
        for i in range(int(n_seg)):
            x=sum(seg_x[0:i+1]) + start_x
            y=sum(seg_y[0:i+1]) + start_y
            shape.append([x,y])

        p=[shape[-1][0] + self.get_value("l_bell"), shape[-1][1]+self.get_value("bellsize")]
        shape.append(p)

        # add bubble
        if self.get_value("add_bubble")>0.7:
            pos=shape[-1][0]*self.get_value("bubble_pos")
            width=self.get_value("bubble_width")
            height=self.get_value("bubble_height")
            if pos-width/2<-10:
                pos=width/2 + 10
            if pos+width/2+10>shape[-1][0]:
                pos=shape[-1][0]-width/2 - 10
            shape=self.make_bubble(shape, pos, width, height)

        return Geo(shape)

class AddPointOptimizer(MutationParameterSet):

    def __init__(self, geo):
        MutationParameterSet.__init__(self)

        self.geo=geo
        self.n_points=1
        for i in range(self.n_points):
            self.add_param("x" + str(i), 0, 1, value=0.5)
            self.add_param("y" + str(i), 0.5, 1.5, value=1.0)

    def make_geo(self):

        new_geo=self.geo.copy()
        for i in range(self.n_points):
            x=self.get_value(f"x{i}")
            x=new_geo.length()*x

            has_point_at_x=False
            for s in new_geo.geo:
                if s[0]==x:
                    has_point_at_x=True
                    break
            if has_point_at_x:
                continue

            y=geotools.diameter_at_x(new_geo, x)
            y*=self.get_value(f"y{i}")

            new_geo.geo.append([x,y])
            new_geo.sort_segments()

        return new_geo