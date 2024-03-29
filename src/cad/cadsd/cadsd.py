# python setup.py build_ext --inplace

#import pyximport; pyximport.install()

import os

if os.getenv('CADSD_BACKEND') == "python":
    import cad.cadsd.cadsd_py as cadsd_imp
else:
    import cad.cadsd._cadsd as cadsd_imp
import numpy as np
import pandas as pd
from cad.calc.conv import freq_to_note_and_cent, note_name, note_to_freq

class CADSD():

    def __init__(self, geo):
        self.geo=geo
        self.segments=None

        self.impedance_spectrum=None
        self.notes=None
        self.highres_impedance_spektrum=None
        self.all_spektra_df=None
        self.ground_peaks=None

        self.sound_spektra=None
        self.fmin = 30
        self.fmax=1000
        self.stepsize = 1

        self.additional_metrics={}

    def get_segments(self):
        if self.segments==None:
            self.segments=cadsd_imp.create_segments_from_geo(self.geo.geo)
        return self.segments

    def get_impedance_spektrum(self):

        if self.impedance_spectrum is not None:
            return self.impedance_spectrum

        from_freq=self.fmin
        to_freq=self.fmax
        stepsize=self.stepsize

        segments=self.get_segments()
        spektrum={
            "freq": [],
            "impedance": []
        }

        for freq in np.arange(from_freq, to_freq, stepsize):
            spektrum["freq"].append(freq)
            impedance=cadsd_imp.cadsd_Ze(segments, freq)
            spektrum["impedance"].append(impedance)

        self.impedance_spectrum=pd.DataFrame(spektrum)
        return self.impedance_spectrum

    def get_highres_impedance_spektrum(self):

        if self.highres_impedance_spektrum!=None:
            return self.highres_impedance_spektrum

        df1=self.get_impedance_spektrum()

        segments=self.get_segments()
        spektrum={
            "freq": [],
            "impedance": []
        }

        for freq in np.arange(1, 100, 0.1):
            if freq%1==0:
                continue
            
            spektrum["freq"].append(freq)
            impedance=cadsd_imp.cadsd_Ze(segments, freq)
            spektrum["impedance"].append(impedance)

        spektrum=pd.DataFrame(spektrum)

        self.highres_impedance_spektrum=pd.concat((df1, spektrum), ignore_index=True).sort_values("freq")
        return self.highres_impedance_spektrum

    def get_ground_peaks(self):
        if self.ground_peaks is not None:
            return self.ground_peaks
        ground=self.get_all_spektra_df()
        
        maxima = get_max(ground.impedance.freq, ground.impedance.values, "max")
        self.ground_peaks=ground.iloc[maxima].copy()

        return self.ground_peaks
        
    def get_notes(self):        

        if self.notes is not None:
            return self.notes

        fft=self.get_highres_impedance_spektrum()
        maxima = get_max(fft.freq, fft.impedance, "max")
        peaks=fft.iloc[maxima].copy()
        peaks["rel_imp"]=peaks.impedance / peaks.iloc[0]["impedance"]
        t=[freq_to_note_and_cent(x) for x in peaks["freq"]]
        peaks["note-number"], peaks["cent-diff"]=zip(*t)
        peaks["note-name"] = peaks["note-number"].apply(lambda x : note_name(x))
        self.notes=peaks
        return peaks

    def get_ground_spektrum(self):
        if self.sound_spektra==None:
            self._get_sound_spektrum()

        return self.sound_spektra["ground"]

    def get_overblow_spektrum(self):
        if self.sound_spektra==None:
            self._get_sound_spektrum()

        return self.sound_spektra["overblow"]

    # this function could use some optimization
    # 1) split it in ground and overblow spektrum
    # 2) reuse peaks / valley analysis from get_overblow_notes
    # 3) cython

    # parameter offset: frequency offset of ground tone and first overblow
    def _get_sound_spektrum(self, offset=0):

        spektrum=self.get_impedance_spektrum()

        fft={
            "impedance": dict(zip(spektrum.freq, spektrum.impedance)),
            "ground": {},
            "overblow": {}
        }

        fft["impedance"][self.fmin]=0
        for i in range(self.fmin, self.fmax):
            fft["ground"][i]=0
            fft["overblow"][i]=0
        
        peaks=[0,0]
        vally=[0,0]

        up = 0
        npeaks = 0
        nvally = 0

        #print(fft["impedance"].keys())
        for i in range(self.fmin+1, self.fmax):
            if fft["impedance"][i] > fft["impedance"][i-1]:
                if npeaks and not up:
                    vally[nvally] = i - 1
                    nvally+=1
                up = 1
            else:
                if up:
                    peaks[npeaks] = i - 1
                    npeaks+=1
                up = 0
            if nvally > 1:
                break

        if peaks[0]<0:
            raise Exception("bad fft")
        
        k = 0.0001

        mem0 = peaks[0]

        mem0a = peaks[0]

        mem0b = mem0a

        # calculate overblow spectrum of base tone
        for i in range(mem0, self.fmax, mem0):
            for j in range(-mem0a, mem0b):
                if i + j < self.fmax and i + j + offset>self.fmin and mem0-j>=self.fmin and mem0+j>=self.fmin: 
                    if j < 0:
                        fft["ground"][i + j + offset] += fft["impedance"][mem0 + j] * np.exp (i * k)
                    else:
                        fft["ground"][i + j + offset] += fft["impedance"][mem0 - j] * np.exp (i * k)

        # calculate sound specturm of base tone
        for i in range(self.fmin, self.fmax):
            fft["ground"][i] = fft["impedance"][i] * fft["ground"][i] * 1e-6

        mem1 = peaks[1]
        mem1a = peaks[1] - vally[0]
        mem1b = mem1a

        # calculate overblow spectrum of first overblow
        for i in range(mem1, self.fmax, mem1):
            for j in range(-mem1a, mem1b):
                if i + j < self.fmax:
                    if j < 0:
                        fft["overblow"][i + j + offset] += fft["impedance"][mem1 + j] * np.exp (i * k)
                    else:
                        fft["overblow"][i + j + offset] +=fft["impedance"][mem1 - j] * np.exp (i * k)

        # calculate sound spectrum of first overblow
        for i in range(self.fmin, self.fmax):
            fft["overblow"][i] = fft["impedance"][i] * fft["overblow"][i] * 1e-6

        # df={
        #     "freq": fft["ground"].keys(),
        #     "impedance": fft["impedance"].values(),
        #     "ground": fft["ground"].values(),
        #     "overblow": fft["overblow"].values()
        # }
        # df=pd.DataFrame(df)

        # df.impedance=df.impedance.apply(lambda x : x*1e-6)
        # df.ground=df.ground.apply(lambda x : max(0, 20*np.log10(x*2e-5)))
        # df.overblow=df.overblow.apply(lambda x : max(0, 20*np.log10(x*2e-5)))

        for i in range(self.fmin, self.fmax):
            fft["impedance"][i] *= 1e-6
            x=fft["ground"][i]*2e-5
            fft["ground"][i] = 0 if x<1 else 20*np.log10(x) 
            x=fft["overblow"][i]*2e-5
            fft["overblow"][i] = 0 if x<1 else 20*np.log10(x) 


        self.sound_spektra=fft

    def get_all_spektra_df(self):
        if self.all_spektra_df is not None:
            return self.all_spektra_df
            
        if self.sound_spektra==None:
            self._get_sound_spektrum()

        self.all_spektra_df={
            "freq": self.sound_spektra["ground"].keys(),
            "impedance": self.sound_spektra["impedance"].values(),
            "ground": self.sound_spektra["ground"].values(),
            "overblow": self.sound_spektra["overblow"].values()
        }

        self.all_spektra_df=pd.DataFrame(self.all_spektra_df)
        return self.all_spektra_df

    def set_additional_metric(self, key, value):
        self.additional_metrics[key]=value

    def get_additional_metric(self, key):
        if key not in self.additional_metrics:
            return key
        else:
            return self.additional_metrics[key]

    def has_additional_metric(self, key):
        return key in self.additional_metrics

    def release_memory(self):
        self.impedance_spectrum=None
        self.notes=None
        self.highres_impedance_spektrum=None
        self.all_spektra_df=None
        self.ground_peaks=None
        self.sound_spektra=None

# volume of the didgeridoo ground tone
# computed as the mean of the ground spektrum
def cadsd_volume(cadsd):

    if cadsd.has_additional_metric("volume"):
        return cadsd.get_additional_metric("volume")
    
    df=cadsd.get_all_spektra_df()
    vol=df["ground"].mean()
    cadsd.set_additional_metric("volume", vol)
    return vol

# area under the ground spektrum
# divided in one bin per octave
def cadsd_octave_tonal_balance(geo, fundamental_note=-31):

    cadsd=geo.get_cadsd()
    key=f"oct_tonal_balance_fundamental={fundamental_note}"
    if cadsd.has_additional_metric(key):
        return cadsd.get_additional_metric(key)

    frequencies=[]
    f=note_to_freq(fundamental_note)/2
    df=cadsd.get_all_spektra_df()
    max_f=df.freq.max()
    while f<max_f:
        frequencies.append(f)
        f*=2
    frequencies.append(max_f)

    bins=[]

    for i in range(len(frequencies)-1):
        f1=frequencies[i]
        f2=frequencies[i+1]
        df_oct=df[(df.freq>=f1) & (df.freq<=f2)]

        vol=df_oct.ground.mean() / len(df_oct)
        bins.append(vol)

    m=sum(bins)
    bins=[x/m for x in bins]

    cadsd.set_additional_metric(key, bins)
    return bins

# area under the ground spektrum
# divided in n equally spaced n_bins
def cadsd_abs_tonal_balance(geo, n_bins=3):

    cadsd=geo.get_cadsd()
    key=f"abs_tonal_balance_nbins={n_bins}"
    if cadsd.has_additional_metric(key):
        return cadsd.get_additional_metric(key)

    bins=[0 for i in range(n_bins)]
    df=cadsd.get_all_spektra_df()
    ground=list(df.ground)
    bin_size=math.ceil(len(ground)/n_bins)

    for i_bin in range(n_bins):
        for i_sample in range(bin_size):
            bins[i_bin] += ground[i_sample + i_bin*bin_size]


    m=sum(bins)
    bins=[x/m for x in bins]

    cadsd.set_additional_metric(key, key)
    return bins

# find maxima or minima of a numpy array
# scipy.signal import argrelextrema caused problems
# code from https://stackoverflow.com/questions/4624970/finding-local-maxima-minima-with-numpy-in-a-1d-numpy-array
def get_max(x, y, find):
    assert find in ("max", "min")
    a = np.diff(np.sign(np.diff(y))).nonzero()[0] + 1 # local min+max

    if find == "min":
        return (np.diff(np.sign(np.diff(y))) > 0).nonzero()[0] + 1 # local min
    elif find == "max":
        return (np.diff(np.sign(np.diff(y))) < 0).nonzero()[0] + 1 # local max
