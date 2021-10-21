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
import statistics

class Loss(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_loss(self, geo, peak=None, fft=None):
        pass

    def get_peak_fft(self, geo, peak, fft):
        if peak == None and fft == None:
            peak, fft=didgmo_bridge(geo)
            return peak, fft
        else:
            return peak, fft
    
class TargetNoteLoss(Loss):
    
    def __init__(self, targets):
        Loss.__init__(self)
        self.target_numbers=targets
        self.target_freqs=[note_to_freq(x) for x in targets]
        
    def get_loss(self, geo, peak=None, fft=None):
        try:
            peak, fft=self.get_peak_fft(geo, peak, fft)
        except Exception:
            return 100000.0
        l=0.0
        if len(peak.impedance_peaks) < len(self.target_freqs):
            return 100000.0
        
        for i in range(len(self.target_freqs)):
            damping=1-(0.5*i/len(self.target_freqs))
            l1 = self.target_freqs[i] - peak.impedance_peaks[i]["freq"]
            l+=l1*l1*damping
        return l
    
    def get_frequencies(self):
        return self.target_freqs
    
    def __repr__(self):
        n=[ str(note_name(t)) + " (" + str(round(note_to_freq(t), 2)) + ")" for t in self.target_numbers]
        return ", ".join(n)

class ScaleLoss(Loss):
    
    # default: d minor pentatonic with 5 toots
    def __init__(self, scale=[0,3,5,7,10], fundamental=-31, n_peaks=5):
        Loss.__init__(self)

        self.scale_note_numbers=[]
        for i in range(len(scale)):
            self.scale_note_numbers.append(scale[i]+fundamental)
        self.scale_frequencies=[]
        self.n_peaks=n_peaks
        self.fundamental=fundamental
        n_octaves=10
        for note_number in self.scale_note_numbers:
            for i in range(n_octaves):
                freq=note_to_freq(note_number+12*i)
                self.scale_frequencies.append(freq)
                
    def loss_per_frequency(self, f1, f2, i):
        f1=math.log(f1, 2)
        f2=math.log(f2, 2)
        
        decrease_factor=1-(0.5*i/self.n_peaks)
        return 100*decrease_factor*abs(f1-f2)

    def get_loss(self, geo, peak=None, fft=None):
        
        try:
            peak, fft=self.get_peak_fft(geo, peak, fft)
        except Exception:
            return 100000.0

        if len(peak.impedance_peaks) < self.n_peaks:
            return 100000.0

        f_fundamental=note_to_freq(self.fundamental)
        f0=peak.impedance_peaks[0]["freq"]
        loss=self.loss_per_frequency(f_fundamental, f0, 0)
        for i in range(1,self.n_peaks):
            f_peak=peak.impedance_peaks[i]["freq"]
            # get closest key from scale
            f_next_scale=min(self.scale_frequencies, key=lambda x:abs(x-f_peak))
            loss += self.loss_per_frequency(f_peak, f_next_scale, i)
            
        return loss
        
class AmpLoss(Loss):
    
    def __init__(self, n_peaks=1):
        Loss.__init__(self)
        self.n_peaks=n_peaks
    
    def get_loss(self, geo, peak=None, fft=None   ):
        
        try:
            peak, fft=self.get_peak_fft(geo, peak, fft)
        except Exception:
            return 100000.0
        if len(peak.impedance_peaks) < self.n_peaks:
            return 100000.0

        loss=0
        a0=peak.impedance_peaks[0]["amp"]
        for i in range(self.n_peaks):
            amp=peak.impedance_peaks[i]["amp"]/a0
            if amp<0.1:
                loss += 1/amp
                
        return loss
    
class CombinedLoss(Loss):
    
    def __init__(self, losses, weights):
        
        self.losses=losses
        self.weights=weights
        self.n_average_window=20000
        self.averages=[[] for x in losses]
        
        
    def get_loss(self, geo, peak=None, fft=None):
        
        loss=0.0
        for i in range(len(self.losses)):
            thisloss=self.losses[i].get_loss(geo, peak=peak, fft=fft) * self.weights[i]
            self.averages[i].append(thisloss)

            if len(self.averages[i]) > self.n_average_window:
                del self.averages[0]
            loss += thisloss
        return loss

    def get_average_losses(self):

        avg={}
        for i in range(len(self.losses)):
            m=statistics.mean(self.averages[i])
            t=type(self.losses[i])
            avg[t]=m
        return avg
            