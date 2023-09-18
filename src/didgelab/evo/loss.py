from abc import ABC, abstractmethod
import numpy as np
import math

from didgelab.app import get_app
from didgelab.calc.geo import Geo
from didgelab.calc.conv import note_to_freq

class LossFunction(ABC):

    def __init__(self):
        get_app().register_service(self)

    @abstractmethod
    def get_loss(self, geo):
        raise Exception("this is abstract so we should never reach this code")

    def __call__(self, geo, context=None):
        return self.get_loss(geo)

# a loss that measures the deviation from a single note 
def single_note_loss(note, peaks, i_note=0, filter_rel_imp=0.1):
    peaks=peaks[peaks.rel_imp>filter_rel_imp]
    if len(peaks)<=i_note:
        return 1000000
    f_target=note_to_freq(note)
    f_fundamental=peaks.iloc[i_note]["freq"]
    return np.sqrt(abs(math.log(f_target, 2)-math.log(f_fundamental, 2)))

# add loss if the didge gets smaller
def diameter_loss(geo):
    if type(geo)==Geo:
        shape=geo.geo
    elif type(geo) == list:
        shape=geo
    else:
        raise Exception("unknown type " + str(type(geo)))

    loss=0
    for i in range(1, len(shape)):
        delta_y=shape[i-1][1]-shape[i][1]
        if delta_y < 0:
            loss+=-1*delta_y

    loss*=0.005
    return loss

