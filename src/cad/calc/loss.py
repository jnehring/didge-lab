from abc import ABC, abstractmethod
from cad.calc.geo import Geo
from cad.cadsd.cadsd import CADSD
from cad.calc.conv import note_to_freq, note_name, freq_to_note
import math

class LossFunction(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_loss(self, geo, context=None) -> float:
        raise Exception("this is abstract so we should never reach this code")

    def __call__(self, geo, context=None):
        return self.get_loss(geo, context)

class TootTuningHelper():

    def __init__(self, scale, fundamental, filter_rel_imp=0.1):
        self.scale=scale
        self.fundamental=fundamental
        self.filter_rel_imp=filter_rel_imp

        self.scale_note_numbers=[]
        for i in range(len(scale)):
            self.scale_note_numbers.append(scale[i]+fundamental)

        n_octaves=10
        self.scale_frequencies=[]
        for note_number in self.scale_note_numbers:
            for i in range(0, n_octaves):
                transposed_note=note_number+12*i
                freq=note_to_freq(transposed_note)
                self.scale_frequencies.append(freq)

    # get a list of all peaks and their deviations from tuning
    def get_tuning_deviations(self, geo):
        peaks=geo.get_cadsd().get_notes()
        peaks=peaks[peaks.rel_imp>self.filter_rel_imp]
        deviations=[]
        for f1 in peaks.freq:
            f2=min(self.scale_frequencies, key=lambda x:abs(x-f1))
            f1=math.log(f1, 2)
            f2=math.log(f2, 2)
            deviations.append(abs(f1-f2))
        return deviations

class PentaLossFunction(LossFunction):

    def __init__(self, scale=[0,3,5,7,10], fundamental=-31, n_peaks=5, octave=True):
        self.scale=scale
        self.fundamental=fundamental
        self.n_peaks=n_peaks
        self.octave=octave

        self.toot_tuning=TootTuningHelper(scale, fundamental)

    def get_loss(self, geo, context=None):
        
        tuning_deviations=self.toot_tuning.get_tuning_deviations(geo)
        peaks=geo.get_cadsd().get_overblow_notes()
        peaks["dev"]=tuning_deviations
        print(peaks)
    