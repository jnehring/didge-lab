import sys
#sys.path.append('../')
from didgelab.calc.geo import Geo
from didgelab.util.didge_visualizer import vis_didge
import seaborn as sns
from didgelab.calc.conv import note_to_freq, freq_to_note_and_cent, note_name
import pandas as pd
import numpy as np
from scipy.interpolate import make_interp_spline
import json
import matplotlib.pyplot as plt
from didgelab.calc.sim.sim import compute_impedance_iteratively, get_notes, compute_impedance, create_segments, get_log_simulation_frequencies, quick_analysis
from scipy.signal import argrelextrema
import jsonlines
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import os
from datetime import datetime
import time
import logging
import concurrent

# compute a smoothed version of a rough didgeridoo shape
def smooth_didge(geo,resolution=20):

    # make spline
    x = [g[0] for g in geo.geo]
    y = [g[1] for g in geo.geo]
    xi = np.concatenate(([-10], x))
    yi = np.concatenate(([y[0]], y))
    bspl = make_interp_spline(xi, yi, k=2)

    x_spline = np.concatenate((x, np.arange(x[0], x[-1], resolution)))
    x_spline = np.arange(x[0], x[-1], resolution)
    x_spline = np.array(x_spline)
    y_spline = bspl(x_spline)
    
    # compute difference from spline to original shape
    orig_shape = np.array([geo.diameter_at_x(x) for x in x_spline])
    diff = y_spline - orig_shape

    # even out large deviations from the original shape
    i=diff<0
    diff[i] = -1*np.sqrt(diff[i]*-1)
    i=diff>0
    diff[i] = np.sqrt(diff[i])
    y_spline = orig_shape + diff

    # assure that the didge is never narrower than half the mouthpiece diameter
    y_spline = np.array([np.max((y_spline[0]/2, _y)) for _y in y_spline])

    x_spline = np.round(x_spline)
    y_spline = np.round(y_spline)

    
    geo = list(zip(x_spline, y_spline))
    return Geo(geo)

# create a simple basic geometry
def create_geo():
    l=1000+np.random.random()*1000
    d1=32
    bellsize=60+np.random.random()*25

    x = np.random.sample(np.random.randint(10,15))
    x = np.sort(x)

    y = np.power(x, 2)
    y = np.power(x, 2)
    y /= y[-1]
    
    deltay = 0.3*2*(np.random.sample(len(y))-0.5)
    y += deltay
    
    y *= (bellsize-d1)
    y += d1

    # assure that the didge is never narrower than half the mouthpiece diameter
    y = np.array([np.max((y[0]/2, _y)) for _y in y])

    x *= l
    
    x = np.concatenate(([0], x, [l]))
    y = np.concatenate(([d1], y, [bellsize]))
    
    # delete duplicate coordinges
    delete = []
    for i in range(len(x)):
        for j in range(i+1, len(x)):
            if x[i] == x[j]:
                delete.append(i)
    x = np.delete(x, delete)
    y = np.delete(y, delete)
    
    x = np.round(x)
    y = np.round(y)

    geo = []
    for (_x, _y) in zip(x,y):
        geo.append([_x, _y])

    geo = Geo(geo)
    return geo

log_simulation_freqs = None

# get the fundamental frequency of a geometry
def get_fundamental_freq(geo):
    global log_simulation_freqs
    if log_simulation_freqs is None:
        log_simulation_freqs = get_log_simulation_frequencies(50, 120, 2)
    segments = create_segments(geo)
    impedance = compute_impedance(segments, log_simulation_freqs)
    fundamental = np.argmax(impedance)
    return log_simulation_freqs[fundamental]

def get_deviation(geo, scaling, target):
    spline_scaled_x = [x[0]*scaling for x in geo.geo]
    geo_y = [x[1] for x in geo.geo]

    scaled_geo = Geo(list(zip(spline_scaled_x, geo_y)))
    fundamental = get_fundamental_freq(scaled_geo)

    return fundamental, np.abs(np.log2(fundamental)-target), scaled_geo

# scale the didge to tune its fundamental
tuned_notes = None
tuned_frequencies = None
def find_scaling(geo, n_steps=10, interval=0.15, max_error=3):

    global tuned_notes, tuned_frequencies
    if tuned_notes is None:
        tuned_notes = np.arange(-36, -23) # from A1-A2
        tuned_frequencies = note_to_freq(tuned_notes)

    fundamental = get_fundamental_freq(geo)
    argmin = np.argmin(np.abs(tuned_frequencies-fundamental))
    target_freq = tuned_frequencies[argmin]
    
    if np.abs(freq_to_note_and_cent(fundamental)[1]) < max_error:
        return fundamental, geo
    
    log_target_freq = np.log2(target_freq)
    
    assert fundamental>tuned_notes[0] or fundamental<tuned_notes[-1]
        
    deviation = np.abs(np.log2(fundamental)-target_freq)
        
    i=0
    scaling=1

    f1, d1, ng = get_deviation(geo, scaling-interval, log_target_freq)

    if np.abs(freq_to_note_and_cent(f1)[1]) < max_error:
        return f1, ng
    
    f2, d2, ng = get_deviation(geo, scaling+interval, log_target_freq)
    if np.abs(freq_to_note_and_cent(f2)[1]) < max_error:
        return f2, ng
    
    f = (f1, f2)
    f1 = np.min(f)
    f2 = np.max(f)

    
    for i in range(n_steps):
        
        fnew, dnew, ng = get_deviation(geo, scaling, log_target_freq)
        if np.abs(freq_to_note_and_cent(fnew)[1]) < max_error:
            return fnew, ng

        interval /= 2
        if target_freq>fnew:
            f1=fnew
            d1=dnew
            scaling-=interval
        else:
            f2=fnew
            d2=fnew
            scaling+=interval

    print(fnew)
    return fnew, ng

# get all features for the didgeridoo database
def extract_didge_info(geo):
    # get impedance
    freqs, impedances= compute_impedance_iteratively(geo, n_precision_peaks=10)
    
    features = {
        "length": geo.geo[-1][0],
        "mouthpiece_diameter": geo.geo[0][1],
        "bellsize": geo.geo[-1][1],
        #"impedance_freqs": list(freqs),
        #"impededances": list(impedances)
    }

    # get notes
    extrema = argrelextrema(impedances, np.greater)
    peak_freqs = freqs[extrema]
    note_and_cent = [freq_to_note_and_cent(f) for f in peak_freqs]

    peaks = {
        "note_name": [note_name(n[0]) for n in note_and_cent],
        "cent_diff": [float(n[1]) for n in note_and_cent],
        "note_nr": [int(n[0]) for n in note_and_cent],
        "freq": peak_freqs,
        "impedance": impedances[extrema],
    }
    
    peaks = pd.DataFrame(peaks)
    peaks["rel_imp"] = peaks.impedance / peaks.impedance.max()

    toots = peaks.query("rel_imp>0.2 and freq<500")

    fundamental = toots.query("freq>50 and freq<120").iloc[0]
    
    features["fundamental_note_name"] = fundamental["note_name"]
    features["fundamental_note_number"] = int(fundamental["note_nr"])
    features["fundamental_cent_diff"] = float(fundamental["note_nr"])
    features["playable_notes"] = list(toots.note_nr)
    features["peaks"] = {key: list(peaks[key]) for key in peaks.columns}
    
    return features

def create_db_entry():
    try:
        geo = create_geo()
        geo = smooth_didge(geo)
        f, geo = find_scaling(geo)
        features = extract_didge_info(geo)
        return features
    except Exception as e:
        logging.error(e)
        return None

def create_database(folder):

    n_files = 10
    n_entries = 100000
    pbar = tqdm(total=n_files*n_entries)
    for i in range(10):
        outfile = os.path.join(folder, f"database_{i}.jsonl")
        with jsonlines.open(outfile, mode='w') as writer:
            n_created = 0

            num_cpus = os.getenv("NUM_CPUS")
            if num_cpus is None:
                num_cpus = multiprocessing.cpu_count()
            else:
                num_cpus = int(os.getenv("NUM_CPUS"))
            batch_size = num_cpus*10
            while n_created<n_entries:

                n_tasks = np.min((batch_size, n_entries-n_created))
                                
                with ProcessPoolExecutor(max_workers=num_cpus) as executor:

                    futures = [executor.submit(create_db_entry) for i in range(n_tasks)]

                    for future in concurrent.futures.as_completed(futures):
                        result = future.result()
                        if result is not None:
                            writer.write(result)
                        pbar.update(1)
                        n_created += 1

def main():
    folder = os.path.join(
        "../../didge-database/", 
        datetime.now().isoformat()
    )
    if not os.path.exists(folder):
        os.makedirs(folder)
    create_database(folder)

if __name__ == "__main__":
    features = create_db_entry()
    #main()
