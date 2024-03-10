"""
python -m experiments.nuevolution.evolve
"""

from didgelab.calc.geo import Geo, geotools
from didgelab.evo.nuevolution import Genome, LossFunction, Nuevolution
from didgelab.evo.nuevolution import GeoGenomeA, NuevolutionWriter, GeoGenome
from didgelab.evo.nuevolution import NuevolutionProgressBar, LinearDecreasingCrossover,LinearDecreasingMutation
from didgelab.util.didge_visualizer import vis_didge
from didgelab.calc.sim.sim import compute_impedance_iteratively, get_notes, compute_impedance, create_segments, get_log_simulation_frequencies, quick_analysis
from didgelab.calc.conv import note_to_freq, freq_to_note_and_cent, note_name
from didgelab.app import get_config

import math
import numpy as np
from typing import DefaultDict, List
import pandas as pd
import logging

class GeoGenomeB (GeoGenome):

    def build(n_segments):
        return GeoGenomeB(n_genes=(n_segments*2)+2)

    def genome2geo(self) -> Geo:
        d0 = 32

        x = [0]
        y = [d0]
        min_l = 1000
        max_l = 2000

        min_b = 32
        max_b = 100

        d_factor = 75
        min_d = 25

        length = self.genome[0] * (max_l-min_l) + min_l 
        bell_size = self.genome[1] * (max_b-min_b) + min_b

        _x = self.genome[np.arange(2, len(self.genome), 2)]
        _y = self.genome[np.arange(3, len(self.genome), 2)]

        x = [0]
        y = [0]
        
        factor = 0.5
        for segx, segy in zip(_x,_y):
            x.append(x[-1] + segx)
            _y = y[-1] + factor*segy - factor * 0.5
            if _y < 0:
                _y = 0
            y.append(_y)

        x = np.array(x)
        y = np.array(y)
        x /= x[-1]
        y /= y.sum()
        y /= y[-1]
        x *= length
        y = np.array(y) * (bell_size-d0) + d0
        
        geo = list(zip(x,y))
        return Geo(geo)


class MbeyaGemome(GeoGenome):

    def add_param(self, name, minval, maxval):
        self.named_params[name] = {
            "index": len(self.named_params),
            "min": minval,
            "max": maxval
        }

    def get_value(self, name):
        p = self.named_params[name]
        v = self.genome[p["index"]]
        v = v*(p["max"]-p["min"]) + p["min"]
        return v

    def __init__(self, n_bubbles=1, add_bubble_prob=0.7):

        self.named_params = {}

        self.d1=32
        self.add_bubble_prob=add_bubble_prob
        self.n_bubbles=n_bubbles

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
        for i in range(self.n_bubbles):
            self.add_param(f"add_bubble_{i}", 0, 1)
            self.add_param(f"bubble_height_{i}", -0.5, 1)
            self.add_param(f"bubble_pos_{i}", 0, 1)
            self.add_param(f"bubble_width_{i}", 150, 300)

        GeoGenome.__init__(self, n_genes = len(self.named_params))

    def make_bubble(self, shape, pos, width, height):

        n_segments=11

        i=self.get_index(shape, pos-0.5*width)

        bubbleshape=shape[0:i]

        x=pos-0.5*width
        y=Geo(geo=shape).diameter_at_x(x)

        if shape[i-1][0]<x:
            bubbleshape.append([x,y])

        for j in range(1, n_segments):
            x=pos-0.5*width + j*width/n_segments

            # get diameter at x
            y=Geo(geo=shape).diameter_at_x(x)
            factor=1+math.sin(j*math.pi/(n_segments))*height
            y*=factor

            bubbleshape.append([x,y])

        x=pos+0.5*width
        y=Geo(geo=shape).diameter_at_x(x)
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

    def genome2geo(self):
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
        for i in range(self.n_bubbles):
            if self.get_value(f"add_bubble_{i}")<self.add_bubble_prob:
                pos=shape[-1][0]*self.get_value(f"bubble_pos_{i}")
                width=self.get_value(f"bubble_width_{i}")
                height=self.get_value(f"bubble_height_{i}")
                if pos-width/2<-10:
                    pos=width/2 + 10
                if pos+width/2+10>shape[-1][0]:
                    pos=shape[-1][0]-width/2 - 10
                shape=self.make_bubble(shape, pos, width, height)

        geo=Geo(shape)
        geo=geotools.fix_zero_length_segments(geo)
        return geo


def get_fundamental_freq(geo):
    segments = create_segments(geo)
    freqs = get_log_simulation_frequencies(50, 120, 2)
    impedance = compute_impedance(segments, freqs)
    fundamental = np.argmax(impedance)
    return freqs[fundamental]

class MultiplierLoss(LossFunction):
    
    def __init__(self):
        self.target_f = np.arange(1,15) * note_to_freq(-31)
        self.target_f = np.log2(self.target_f)

    def loss(self, genome : GeoGenome):
        geo = genome.genome2geo()
        freqs = get_log_simulation_frequencies(1, 1000, 10)
        segments = create_segments(geo)
        impedance = compute_impedance(segments, freqs)
        notes = get_notes(freqs, impedance)
        notes = notes[notes.impedance>3]

        logfreq = np.log2(notes.freq)
        deltas = []
        for freq in logfreq:
            closest_target_i = np.argmin(np.abs(self.target_f - freq))
            deltas.append(np.abs(self.target_f[closest_target_i]-freq))

        fundamental_loss = 5*deltas[0]
        if len(deltas) == 1:
            harmonic_loss = 10
        else:
            harmonic_loss = np.mean(deltas[1:])
        n_notes_loss = (10-len(notes))/10

        return {
            "total": fundamental_loss + harmonic_loss + n_notes_loss,
            "fundamental_loss": fundamental_loss,
            "harmonic_loss": harmonic_loss,
            "n_notes_loss": n_notes_loss
        }

def evolve():

    get_config()["log_folder_suffix"] = "nuevolution_test"
    loss = MultiplierLoss()

    writer = NuevolutionWriter()

    n_segments = 10

    evo = Nuevolution(
        loss, 
        MbeyaGemome(n_bubbles=3, add_bubble_prob=0.7),
        generation_size = 200,
        num_generations = 1000,
        population_size = 1000,
    )

    schedulers = [
        LinearDecreasingCrossover(),
        LinearDecreasingMutation()
    ]

    pbar = NuevolutionProgressBar()
    population = evo.evolve() 

    best_geo = population[0].genome2geo()
    freqs = get_log_simulation_frequencies(1, 1000, 1)
    segments = create_segments(best_geo)
    impedance = compute_impedance(segments, freqs)
    notes = get_notes(freqs, impedance)
    for c in ["cent_diff", "freq", "impedance", "rel_imp"]:
        notes[c] = notes[c].round(2)

    print()
    print("losses")
    for key, value in population[0].loss.items():
        print(key, np.round(value, 2))

    print()
    target_f = np.arange(1,15) * note_to_freq(-31)
    log_target_freq = np.log2(target_f) 
    logfreq = np.log2(notes.freq)
    deltas = DefaultDict(list)
    for i in range(len(logfreq)):
        closest_target_i = np.argmin(np.abs(log_target_freq - logfreq[i]))

        deltas["mult"].append(closest_target_i)
        deltas["freq"].append(notes.freq[i])
        deltas["target"].append(target_f[i])
        
    deltas = pd.DataFrame(deltas)
    deltas.target = deltas.target.round(2)
    deltas["diff"] = np.abs(deltas.target - deltas.freq)
    print(deltas)


if __name__ == "__main__":
    try:
        evolve()
    except Exception as e:
        logging.exception(e)