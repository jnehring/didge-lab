from abc import ABC, abstractmethod
from cad.calc.geo import Geo
from cad.cadsd.cadsd import CADSD
from cad.calc.conv import note_to_freq, note_name, freq_to_note
import math
import numpy as np

class LossFunction(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_loss(self, geo):
        raise Exception("this is abstract so we should never reach this code")

    def __call__(self, geo, context=None):
        return self.get_loss(geo)

def single_note_loss(note, geo, i_note=0, filter_rel_imp=0.1):
    peaks=geo.get_cadsd().get_notes()
    peaks=peaks[peaks.rel_imp>filter_rel_imp]
    if len(peaks)<=i_note:
        return 1000000
    f_target=note_to_freq(note)
    f_fundamental=peaks.iloc[i_note]["freq"]
    return np.sqrt(abs(math.log(f_target, 2)-math.log(f_fundamental, 2)))

class ImpedanceVolumeLoss():

    def __init__(self, min_freq=None, max_freq=None, num_peaks=None, target_volume=1e7):
        self.min_freq=min_freq
        self.max_freq=max_freq
        self.num_peaks=num_peaks
        self.target_volume=target_volume

    def get_loss(self, geo):
        peaks=geo.get_cadsd().get_notes()

        if self.min_freq is not None:
            peaks=peaks[(peaks.freq>=self.min_freq)]
        if self.max_freq is not None:
            peaks=peaks[(peaks.freq<=self.max_freq)]
            
        if self.num_peaks is not None:
            if len(peaks)<self.num_peaks:
                return 10
            else:
                peaks=peaks.loc[peaks.sort_values(by=["impedance"]).impedance[-1*self.num_peaks:].index]

        print(peaks)

        volume_loss=0
        for imp in peaks.impedance:
            print(imp)
            imp=-1*(1-imp/self.target_volume)
            print(imp)
            volume_loss+=imp
        return volume_loss

class TootTuningHelper():

    def __init__(self, scale=None, fundamental=None, filter_rel_imp=0.1, frequencies=None, min_freq=None, max_freq=None):

        self.filter_rel_imp=filter_rel_imp
        self.min_freq=min_freq
        self.max_freq=max_freq
        self.min_freq=min_freq
        self.max_freq=max_freq

        if scale is not None and fundamental is not None:
            self.scale=scale
            self.fundamental=fundamental

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
        elif frequencies is not None and len(frequencies)>0:
            self.scale_frequencies=frequencies
        else:
            raise Exception("Please specify either scale+fundamental or a frequencies list")
    # get a list of all peaks and their deviations from tuning
    def get_tuning_deviations(self, geo, return_peaks=False):
        peaks=geo.get_cadsd().get_notes()
        peaks=peaks[peaks.rel_imp>self.filter_rel_imp]

        if self.min_freq is not None:
            peaks=peaks[peaks.freq>=self.min_freq]

        if self.max_freq is not None:
            peaks=peaks[peaks.freq<=self.max_freq]

        deviations=[]
        for f1 in peaks.freq:
            deviations.append(self.get_tuning_deviation_freq(f1))

        if return_peaks:
            return deviations, peaks
        else:
            return deviations
    
    def get_tuning_deviation_freq(self, freq):
        f2=min(self.scale_frequencies, key=lambda x:abs(x-freq))
        freq=math.log(freq, 2)
        f2=math.log(f2, 2)
        return np.sqrt(abs(freq-f2))

# add loss if the didge gets smaller
def diameter_loss(geo: Geo):

    shape=geo.geo
    loss=0
    for i in range(1, len(shape)):
        delta_y=shape[i-1][1]-shape[i][1]
        if delta_y < 0:
            #l=shape[i][0]-shape[i-1][0]
            loss+=-1*delta_y

    loss*=0.005
    return loss

# class PentaLossFunction(LossFunction):

#     def __init__(self, scale=[0,3,5,7,10], fundamental=-31, n_peaks=5, octave=True):
#         self.scale=scale
#         self.fundamental=fundamental
#         self.n_peaks=n_peaks
#         self.octave=octave

#         self.toot_tuning=TootTuningHelper(scale, fundamental)

#     def get_loss(self, geo, context=None):
        
#         tuning_deviations=self.toot_tuning.get_tuning_deviations(geo)
#         peaks=geo.get_cadsd().get_overblow_notes()
#         peaks["dev"]=tuning_deviations
#         print(peaks)
    