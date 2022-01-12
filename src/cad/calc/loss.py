#from cad.calc.didgmo import PeakFile, didgmo_high_res
from cad.cadsd.cadsd import CADSDResult
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
import pandas as pd
import logging
import traceback
import numpy as np
from cad.common.app import App

class Loss(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_loss(self, geo, peak=None, fft=None) -> (float, CADSDResult):
        pass
    
class TargetNoteLoss(Loss):
    
    def __init__(self, targets):
        Loss.__init__(self)
        self.target_numbers=targets
        self.target_freqs=[note_to_freq(x) for x in targets]
        
    def get_loss(self, geo, peak=None, fft=None):
        assert type(geo) == Geo
        try:
            fft=self.get_fft(geo, fft)
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
    def __init__(self, scale=[0,3,5,7,10], fundamental=-31, n_peaks=5, octave=False):
        Loss.__init__(self)

        self.scale_note_numbers=[]
        for i in range(len(scale)):
            self.scale_note_numbers.append(scale[i]+fundamental)

        self.scale_frequencies=[]
        self.n_peaks=n_peaks
        self.fundamental=fundamental
        self.note_names=[]
        n_octaves=10
        for note_number in self.scale_note_numbers:
            self.note_names.append(note_name(note_number))
            for i in range(0, n_octaves):
                transposed_note=note_number+12*i
                freq=note_to_freq(transposed_note)
                self.scale_frequencies.append(freq)

        self.octave=octave
                
    def loss_per_frequency(self, f1, f2, i):
        f1=math.log(f1, 2)
        f2=math.log(f2, 2)
        #decrease_factor=1-(0.5*i/self.n_peaks)
        decrease_factor=1
        return decrease_factor*abs(f1-f2)

    def get_loss(self, geo, cadsd_result=None):
        
        res=None
        try:
            assert type(geo) == Geo

            if cadsd_result is None:

                cadsd_result=CADSDResult.from_geo(geo)
                peaks=cadsd_result.peaks

            loss=0
            if len(peaks) < self.n_peaks+1:
                loss += 1.5*(self.n_peaks+1-len(peaks))

            i_fundamental=0
            while peaks.iloc[i_fundamental]["note-number"]+12<self.fundamental:
                i_fundamental+=1

            f_fundamental=note_to_freq(self.fundamental)

            f0=peaks.iloc[i_fundamental]["freq"]
            loss+=2*self.loss_per_frequency(f_fundamental, f0, 0)

            logging.debug(f"l0: {loss:.2f}, target freq: {f_fundamental:.2f}, actual freq: {f0:.2f}")

            start_index=1
            if self.octave:
                f1=peaks.iloc[i_fundamental+1]["freq"]
                start_index=2
                l=self.loss_per_frequency(f_fundamental*2, f1, 0)
                loss+=l
                logging.debug(f"l1: {l:.2f}, target freq: {f_fundamental*2:.2f}, actual freq: {f1:.2f}")

            for i in range(start_index,self.n_peaks):

                if i_fundamental+i >= len(peaks)-1:
                    break
                f_peak=peaks.iloc[i_fundamental+i]["freq"]
                # get closest key from scale
                f_next_scale=min(self.scale_frequencies, key=lambda x:abs(x-f_peak))
                l = self.loss_per_frequency(f_peak, f_next_scale, i)
                loss += l
                logging.debug(f"l{i}: {l:.2f}, target freq: {f_next_scale:.2f}, actual freq: {f_peak:.2f}")
                    
            return loss, cadsd_result
        except Exception as e:
            logging.error("problematic geo: " + str(geo.geo))
            App.log_exception(e)
            return 100000.0, cadsd_result

    def __str__(self):
        s = "ScaleLoss\n"
        for key, value in self.__dict__.items():
            if key=="scale_frequencies":
                value=[round(x, 2) for x in value]
            s+=f"{key}={value}\n"
        return s, res
        
class AmpLoss(Loss):
    
    def __init__(self, n_peaks=1):
        Loss.__init__(self)
        self.n_peaks=n_peaks
    
    def get_loss(self, geo, cadsd_result=None):
        
        assert type(geo) == Geo

        if cadsd_result==None:
            cadsd_result=CADSDResult.from_geo(geo)
        peaks=cadsd_result.peaks

        if len(peaks) < self.n_peaks:
            return 100000.0, None

        loss=0
        a0=peaks.iloc[0]["impedance"]
        for i in range(self.n_peaks):
            amp=peaks.iloc[0]["impedance"]/a0
            if amp<0.1:
                loss += 1/amp
                
        return loss, cadsd_result
    
class CombinedLoss(Loss):
    
    def __init__(self, losses, weights):
        
        self.losses=losses
        self.weights=weights        
        
    def get_loss(self, geo, cadsd_result=None):
        
        assert type(geo) == Geo

        loss=0.0
        for i in range(len(self.losses)):
            thisloss, cadsd_result=self.losses[i].get_loss(geo, cadsd_result=cadsd_result)
            thisloss *= self.weights[i]
            loss += thisloss
        return loss, cadsd_result

class SingerLoss(Loss):

    def __init__(self):
        Loss.__init__(self)
        self.weight_base_note_loss=1.0
        self.weight_overtone_loss=1.0
        self.weight_singer_loss=1.0

    def loss_per_frequency(self, f1, f2):
        f1=math.log(f1, 2)
        f2=math.log(f2, 2)
        return abs(f1-f2)

    def get_loss(self, geo, peaks=None, fft=None):
        
        base_note=-31 # should be a D
        res=CADSDResult.from_geo(geo)
        peaks=res.peaks

        freqs=list(peaks.freq)

        # tune base note

        fundamental=-31
        base_freq=note_to_freq(-31)
        base_note_loss=self.loss_per_frequency(base_freq, freqs[0])

        # tune overtones
        overtone_loss=0
        
        scale=np.array([0,2,3,5,7,9,10])+fundamental
        scale_frequencies=[]
        for i in range(len(scale)):
            for octave in range(5):
                scale_frequencies.append(note_to_freq(scale[i] + 12*octave))

        for i in range(1, len(freqs)):
            freq=freqs[i]
            f_next_scale=min(scale_frequencies, key=lambda x:abs(x-freq))
            l = self.loss_per_frequency(freq, f_next_scale)
            overtone_loss+=l
        overtone_loss /= len(freqs)-1

        # singer loss
        singer_loss=1-(peaks[peaks.freq>=500].impedance.sum()/peaks.impedance.sum())
        singer_loss=max(0, singer_loss-0.2)

        final_loss=self.weight_base_note_loss*base_note_loss + self.weight_overtone_loss*overtone_loss + self.weight_singer_loss*singer_loss
        return final_loss, res

