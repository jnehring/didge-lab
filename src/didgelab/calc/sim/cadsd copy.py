# python setup.py build_ext --inplace

#import pyximport; pyximport.install()

import os

if os.getenv('CADSD_BACKEND') == "python":
    import didgelab.calc.sim.cadsd_py as cadsd_imp
else:
    import didgelab.calc.sim._cadsd as cadsd_imp
import numpy as np
import pandas as pd

from ..conv import freq_to_note_and_cent, note_name, note_to_freq
from didgelab.app import get_config
from .correction_model.correction_model import FrequencyCorrectionModel

class CADSD():

    def __init__(self, geo):
        self.geo=geo
        self.segments=None

        self.impedance_spectrum=None
        self.notes=None
        self.all_spektra_df=None
        self.ground_peaks=None

        self.sound_spektra=None
        self.stepsize = 1

        self.additional_metrics={}

        self.correction_model = None

    def get_segments(self):
        if self.segments==None:
            self.segments=cadsd_imp.create_segments_from_geo(self.geo.geo)
        return self.segments

    def get_impedance_spektrum(self):

        if self.impedance_spectrum is not None:
            return self.impedance_spectrum

        from_freq=get_config()["sim.fmin"]
        to_freq=get_config()["sim.fmax"]
        stepsize=self.stepsize

        segments=self.get_segments()

        if get_config()["sim.resolution"] == "":
            frequencies = self.get_simulation_frequencies(get_config()["sim.resolution"])
        else:
            frequencies = list(np.arange(
                get_config()["sim.fmin"], 
                get_config()["sim.fmax"], 
                get_config()["sim.resolution"]))
        spektrum={
            "freq": frequencies,
            "impedance": []
        }
        for freq in frequencies:
            impedance=cadsd_imp.cadsd_Ze(segments, freq)
            spektrum["impedance"].append(impedance)

        return spektrum["freq"], spektrum["impedance"]
        #self.impedance_spectrum=pd.DataFrame(spektrum)
        #self.impedance_spectrum.impedance *= 1e-6
        #return self.impedance_spectrum

    def apply_frequency_correction(self, frequencies):
        correction = get_config()["sim.correction"]
        if correction == "none":
            return frequencies
        correction_service = App.get_service(type(FrequencyCorrectionModel))
        return correction_service.correct(frequencies)

    def get_simulation_frequencies(self, max_error):
        frequencies = []
        stepsize = max_error/1200
        start_freq = get_config()["sim.fmin"]
        end_freq = start_freq
        octave = 0

        while end_freq < get_config()["sim.fmax"]:
            notes = np.arange(0,1,stepsize) + octave
            frequencies.extend(start_freq*np.power(2, notes))
            end_freq = frequencies[-1]
            octave += 1
            
        frequencies = list(filter(lambda x:x<=get_config()["sim.fmax"], frequencies))
        return frequencies

    # def get_highres_impedance_spektrum(self):

    #     if self.highres_impedance_spektrum!=None:
    #         return self.highres_impedance_spektrum

    #     df1=self.get_impedance_spektrum()

    #     segments=self.get_segments()
    #     spektrum={
    #         "freq": [],
    #         "impedance": []
    #     }

    #     for freq in np.arange(1, 100, 0.1):
    #         if freq%1==0:
    #             continue
            
    #         spektrum["freq"].append(freq)
    #         impedance=cadsd_imp.cadsd_Ze(segments, freq)
    #         spektrum["impedance"].append(impedance)

    #     spektrum=pd.DataFrame(spektrum)

    #     self.highres_impedance_spektrum=pd.concat((df1, spektrum), ignore_index=True).sort_values("freq")
    #     return self.highres_impedance_spektrum

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

        freq, impedance=self.get_impedance_spektrum()
        maxima = get_max(freq, impedance, "max")

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

        freq, impedance=self.get_impedance_spektrum()

        ground = [0] * len(freq)
        # fft={
        #     "freq": freq,
        #     "impedance": impedance,
        #     "ground": [0] * len(freq),
        #     "overblow": [0] * len(freq)
        # }
        #impedance[]

        #fft["impedance"][0]=0
        #for i in range(get_config()["sim.fmin"], get_config()["sim.fmax"]):
        #    fft["ground"][i]=0
        #    fft["overblow"][i]=0
        
        peaks=[0,0]
        vally=[0,0]

        up = 0
        npeaks = 0
        nvally = 0

        # get first maximum of impedance spektrum
        for i in range(1, len(freq)):
            if impedance[i] > impedance[i-1]:
                if npeaks and not up:
                    vally[nvally] = i - 1
                    nvally+=1
                up = 1
            else:
                if up:
                    peaks[npeaks] = freq[i - 1]
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

        # return the index of haystack closest to needle
        def get_closest_index(haystack, needle, offset=0):
            if type(needle) == list:
                return [get_closest_index(haystack, x) for x in needle]
            
            d1=100000
            d2=100000
            for i in range(offset, len(haystack)):
                d3 = np.abs(haystack[i]-needle)
                if d2<d3:
                    if d1<d2:
                        return i-2
                    else:
                        return i-1
                d1=d2
                d2=d3
            return i
        
        # calculate sound spectrum of base tone
        octave=1
        f=mem0
        print("mem0", mem0, mem0a, mem0b)
        fft = {
            "impedance": np.array(impedance).copy(),
            "ground": [0] * len(freq)
        }
        pair_old = []
        values_old = []
        for i in range(mem0, get_config()["sim.fmax"], mem0):
            print("len pairs old", len(pair_old), i)
            print("i, -mem0a, offset", i, -mem0a, offset)
            print("j from ", -mem0a, mem0b)
            for j in range(-mem0a, mem0b):
                if i + j < get_config()["sim.fmax"] and i+j+offset<len(fft["ground"]): 
                    if j < 0:
                        fft["ground"][i + j + offset] += fft["impedance"][mem0 + j] * np.exp (i * k)
                        pair_old.append((i+j+offset, mem0+j))
                    else:
                        fft["ground"][i + j + offset] += fft["impedance"][mem0 - j] * np.exp (i * k)
                        pair_old.append((i+j+offset, mem0-j))
                    values_old.append(fft["ground"][i + j + offset])
            print("switch", pair_old[-1])

        # calculate sound specturm of base tone
        for i in range(get_config()["sim.fmin"], len(fft["ground"])):
            fft["ground"][i] = fft["impedance"][i] * fft["ground"][i] * 1e-6

        print("=======")
        fmax = get_config()["sim.fmax"]
        fmin = get_config()["sim.fmin"]
        pairs_new = []
        values_new = []

        # for i in range()

        # for i in range(mem0, fmax, mem0):
        #     ik = np.exp (i * k)
        #     fj_l = get_closest_index(freq, i-mem0a)
        #     print("fj_l", fj_l, i, i-mem0a, freq[fj_l])
        #     fj_r = 0

        #     print("j from", i-mem0a, i+mem0a)
        #     first = True
        #     while fj_l<len(freq) and (first or fj_r>=1): #and freq[fj_l]<=i+mem0a:
        #         first = False
        #         pairs_new.append((fj_l, fj_r))
        #         ground[fj_l] += impedance[fj_r] * ik
        #         values_new.append(ground[fj_l])
        #         fj_l+=1
        #         if fj_l<=i:
        #             fj_r += 1
        #         else:
        #             fj_r -= 1

        #     print("switch", pairs_new[-1])
            

        for i in range(get_config()["sim.fmin"], len(fft["ground"])):
            ground[i] = impedance[i] * ground[i] * 1e-6

        i=100
        print(pair_old[i:i+10])
        print(pairs_new[i:i+10])
        # print("-")
        # print(values_old[i:i+10])
        # print(values_new[i:i+10])
        # print("-")
        # print(freq[i:i+10])

        for i in range(len(freq)):
            impedance[i] *= 1e-6
            x=ground[i]*2e-5
            ground[i] = 0 if x<1 else 20*np.log10(x) 

        self.sound_spektra = {
            "freq": freq,
            "impedance": impedance,
            "ground": ground
        }
        #self.sound_spektra=fft
        return


    def _get_sound_spektrum_old(self, offset=0):

        freq, impedance=self.get_impedance_spektrum()
        spektrum = pd.DataFrame({"freq": freq, "impedance": impedance})
        fft={
            "impedance": dict(zip(spektrum.freq, spektrum.impedance)),
            "ground": {},
            "overblow": {}
        }
        
        fft["impedance"][get_config()["sim.fmin"]]=0
        for i in range(get_config()["sim.fmin"], get_config()["sim.fmax"]):
            fft["ground"][i]=0
            fft["overblow"][i]=0
        
        peaks=[0,0]
        vally=[0,0]

        up = 0
        npeaks = 0
        nvally = 0

        for i in range(get_config()["sim.fmin"]+1, get_config()["sim.fmax"]):
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

        # calculate sound spectrum of base tone
        pair_old = []
        for i in range(mem0, get_config()["sim.fmax"], mem0):
            for j in range(-mem0a, mem0b):
                if i + j < get_config()["sim.fmax"] and i + j + offset>get_config()["sim.fmin"] and mem0-j>=get_config()["sim.fmin"] and mem0+j>=get_config()["sim.fmin"]: 
                    if j < 0:
                        fft["ground"][i + j + offset] += fft["impedance"][mem0 + j] * np.exp (i * k)
                        pair_old.append((i+j+offset, mem0+j))
                    else:
                        fft["ground"][i + j + offset] += fft["impedance"][mem0 - j] * np.exp (i * k)
                        pair_old.append((i+j+offset, mem0-j))
                    # print(i + j + offset, fft["impedance"][mem0 + j] * np.exp (i * k))

        print("original")
        print(pair_old[40:50])
        # calculate sound specturm of base tone
        for i in range(get_config()["sim.fmin"], get_config()["sim.fmax"]):
            fft["ground"][i] = fft["impedance"][i] * fft["ground"][i] * 1e-6

        mem1 = peaks[1]
        mem1a = peaks[1] - vally[0]
        mem1b = mem1a

        # calculate overblow spectrum of first overblow
        for i in range(mem1, get_config()["sim.fmax"], mem1):
            for j in range(-mem1a, mem1b):
                if i + j < get_config()["sim.fmax"]:
                    if j < 0:
                        fft["overblow"][i + j + offset] += fft["impedance"][mem1 + j] * np.exp (i * k)
                    else:
                        fft["overblow"][i + j + offset] +=fft["impedance"][mem1 - j] * np.exp (i * k)

        # calculate sound spectrum of first overblow
        for i in range(get_config()["sim.fmin"], get_config()["sim.fmax"]):
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

        for i in range(get_config()["sim.fmin"], get_config()["sim.fmax"]):
            #fft["impedance"][i] *= 1e-6
            x=fft["ground"][i]*2e-5
            fft["ground"][i] = 0 if x<1 else 20*np.log10(x) 
            x=fft["overblow"][i]*2e-5
            fft["overblow"][i] = 0 if x<1 else 20*np.log10(x) 
        #print(spektrum.impedance[0:4])


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
