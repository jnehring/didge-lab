import pyximport; pyximport.install()
import cad.cadsd._cadsd as cadsd
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from cad.calc.conv import freq_to_note_and_cent, note_name

class CADSDResult():

    def __init__(self, fft, peaks, geo):
        self.fft=fft
        self.peaks=peaks
        self.geo=geo

    @classmethod
    def from_geo(cls, geo):
        fft=get_highres_spektrum(geo.geo)
        peaks=get_peaks(fft)
        return CADSDResult(fft, peaks, geo)

    def print_summary(self, loss=None):
        s=f"length:\t\t{self.geo.length():.2f}\n"
        s+=f"bell size:\t{self.geo.geo[-1][1]:.2f}\n"
        s+=f"num segments:\t{len(self.geo.geo)}\n"
        s+=f"num peaks:\t{len(self.peaks)}\n"
        if loss != None:
            s+=f"loss:\t\t{loss:.2f}\n"
            
        peaks=self.peaks.copy()
        peaks.rel_imp=peaks.rel_imp.apply(lambda x : f"{x:.2f}")
        peaks.impedance=peaks.impedance.apply(lambda x : f"{x:.2e}")
        peaks["cent-diff"]=peaks["cent-diff"].apply(lambda x : f"{x:.2f}")
        s+=str(peaks)
        
        print(s)

def get_peaks(fft):
    peaks = fft.iloc[argrelextrema(fft.impedance.values, np.greater_equal)[0]].copy()
    peaks["rel_imp"]=peaks.impedance / peaks.iloc[0]["impedance"]
    peaks=peaks[peaks.rel_imp>0.1]
    t=[freq_to_note_and_cent(x) for x in peaks["freq"]]
    peaks["note-number"], peaks["cent-diff"]=zip(*t)
    peaks["note-name"] = peaks["note-number"].apply(lambda x : note_name(x))
    return peaks

def get_impedance_spektrum(geo, from_freq, to_freq, stepsize):

    segments=cadsd.create_segments_from_geo(geo)
    spektrum={
        "freq": [],
        "impedance": []
    }

    for freq in np.arange(from_freq, to_freq, stepsize):
        spektrum["freq"].append(freq)
        impedance=cadsd.cadsd_Ze(segments, freq)
        spektrum["impedance"].append(impedance)
    
    return pd.DataFrame(spektrum)

def get_highres_spektrum(geo):

    df1=get_impedance_spektrum(geo, 1, 100, 0.1)
    df2=get_impedance_spektrum(geo, 101, 1000, 1)
    return pd.concat([df1, df2])


def geo_fft (geo, gmax, offset):

    fft={
        "impedance": {},
        "overblow": {},
        "ground": {}
    }

    for key in fft.keys(): 
        fft[key][0]=0

    segments=cadsd.create_segments_from_geo(geo)
    for f in range(1, gmax):
        fft["impedance"][f] = cadsd.cadsd_Ze(segments, f)
        fft["overblow"][f] = 0
        fft["ground"][f] = 0


    # search for peaks and valleys
    peaks=[0,0]
    vally=[0,0]

    up=False
    npeaks=0
    nvally=0

    freqs=fft["impedance"].keys()
    for i in range(2, len(freqs)):
        if fft["impedance"][i] > fft["impedance"][i-1]:
            if npeaks and not up:
                vally[nvally]=i-1
                nvally+=1
            up=True
        else:
            if up:
                peaks[npeaks] = i-1
                npeaks+=1
            up=False 

        if nvally>1:
            break

    if peaks[0]<0:
        return None

    k = 0.0001

    mem0 = peaks[0]
    mem0a = peaks[0]

    mem0b = mem0a   

    # calculate overblow spectrum of base tone
    for i in np.arange(mem0, gmax, mem0):
        for j in range(-1*mem0a, mem0b):
	        if i + j +offset < gmax:

	            if j < 0:
	                fft["ground"][i + j + offset] += fft["impedance"][mem0 + j] * pow(np.e, i * k)
	            else:
	                fft["ground"][i + j + offset] += fft["impedance"][mem0 - j] * pow(np.e, i * k)

    # calculate sound specturm of base tone
    for i in range(gmax):
        fft["ground"][i] = fft["impedance"][i] * fft["ground"][i] * 1e-6

    mem1 = peaks[1]

    mem1a = peaks[1] - vally[0]

    mem1b = mem1a

    # calculate overblow spectrum of first overblow
    for i in np.arange(mem1, gmax, mem1):
        for j in range(-1*mem1a, mem1b):
            if i + j < gmax:
                if j < 0:
                    fft["overblow"][i + j + offset] +=fft["impedance"][mem1 + j] * pow(np.e, i * k)
                else:
                    fft["overblow"][i + j + offset] += fft["impedance"][mem1 - j] * pow(np.e, i * k)

    # calculate sound spectrum of first overblow
    for i in range(gmax):
        fft["overblow"][i] = fft["impedance"][i] * fft["overblow"][i] * 1e-6

    return fft