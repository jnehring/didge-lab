import os
import subprocess
import math
import copy
from prettytable import PrettyTable
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import random
from tqdm import tqdm
from threading import Lock
from cad.calc.geo import Geo
from cad.calc.conv import freq_to_note_and_cent, note_name

class FFT:

    def __init__(self, infile=None, fft=None, resolution=1):

        if infile != None: 
            self.fft=pd.read_csv(infile, delimiter=" ", names=["freq", "impedance", "ground", "overblow"])
            self.fft["freq"]=self.fft["freq"]/resolution
        else:
            self.fft=fft

        self.peaks={"freq":[], "impedance":[], "note-name": [], "note-number": [], "cent-diff": []}

        ascending=True
        lastImpedance=0
        for index, row in self.fft.iterrows():
            freq=row["freq"]
            impedance=row["impedance"]
            #if freq>77 and freq<79:
            #    print(freq, impedance)

            if impedance<lastImpedance and ascending:
                self.peaks["freq"].append(freq)
                self.peaks["impedance"].append(impedance)
                note, cent=freq_to_note_and_cent(freq)
                self.peaks["note-number"].append(note)
                self.peaks["cent-diff"].append(cent)
                self.peaks["note-name"].append(note_name(note))
                ascending=False
            if impedance>lastImpedance:
                ascending=True
            lastImpedance=impedance

        self.peaks=pd.DataFrame(self.peaks)
        self.peaks["amp"]=self.peaks["impedance"]/self.peaks["impedance"].max()

class PeakFile:

    def __init__(self, infile, resolution=1):

        self.impedance_peaks=[]
        self.groundtone_peaks=[]
        self.first_overblow_peaks=[]

        f=open(infile)
        for line in f:
            line=line[0:-1].split(" ")

            note_name=line[2]
            number=int(note_name[-1])
            number-=2
            note_name=note_name[0:-1] + str(number)
            peak={
                "t": int(line[0]),
                "freq": int(line[1])/resolution,
                "note": note_name,
                "cent-diff": int(line[3]),
                "amp": float(line[4])
            }

            if peak["t"]==0:
                self.impedance_peaks.append(peak)
            elif peak["t"]==1:
                self.groundtone_peaks.append(peak)
            elif peak["t"]==2:
                self.first_overblow_peaks.append(peak)
            else:
                raise Exception("unknown t")
        f.close()

    def get_drone_freq(self):
        return self.groundtone_peaks[0]["freq"]

    def print_impedance_peaks(self, limit=None):

        s=""
        c=0
        for p in self.impedance_peaks:

            c+=1

            s += "{%s|%.02f|%.02d}, " % (p["note"], p["freq"], p["cent-diff"])

            if limit != None and c==limit:
                break
        print(s[0:-2])

    def get_impedance_table(self, limit=None):

        df={}
        for key in self.impedance_peaks[0].keys():
            df[key]=[]

        for p in self.impedance_peaks:

            for key in p.keys():
                df[key].append(p[key])
        
        df=pd.DataFrame(df)
        a0=df["amp"][0]
        df["amp_relative"]=df["amp"]/a0
        return df

lock=Lock()
def didgmo_bridge(geo : Geo, skip_fft=False, resolution=1, max=1000):

    lock.acquire()
    file_num=0
    while os.path.exists("temp" + str(file_num) + ".geo"):
        file_num+=1
    lock.release()

    name="temp" + str(file_num)
    outfile=name + ".geo"
    new_geo=geo.copy()
    new_geo.scale(0.001)
    try:
        new_geo.write_geo(outfile)
        command=["didgmo", "geo2fft", name, str(max), str(resolution)]
        subprocess.check_output(command)
        fft=FFT(infile=name + ".fft", resolution=resolution)
        return fft
        # if not skip_fft:
        #     fft=pd.read_csv(name + ".fft", delimiter=" ", names=["freq", "impedance", "ground", "overblow"])
        #     peak=PeakFile(name + ".peak", resolution=resolution)
        #     return peak, fft
        # else:
        #     peak=PeakFile(name + ".peak", resolution=resolution)
        #     return peak
    finally:
        files=[outfile, name + ".fft", name + ".peak", name + ".lab"]
        for f in files:
            os.remove(f)

def didgmo_high_res(geo : Geo ):

    high_res=20
    high_res_limit=300

    fft1=didgmo_bridge(geo, resolution=high_res, max=high_res_limit)
    fft2=didgmo_bridge(geo, resolution=1, max=1000)
    
    fft1=fft1.fft
    fft2=fft2.fft

    fft2=fft2[fft2["freq"]>=high_res_limit]

    fft=pd.concat([fft1,fft2], ignore_index=True)

    fft=FFT(fft=fft)
    return fft


def cleanup():

    files=os.listdir(".")
    for f in files:
        if f[0:4]=="temp":
            os.remove(f)