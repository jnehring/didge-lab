import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy.signal import argrelextrema
import os
import sys
import pandas as pd
import seaborn as sns
import json

#from cad.calc.geo import Geo
#from cad.calc.conv import freq_to_note_and_cent, note_name

# analyze peaks from the record
def do_fft(infile, maxfreq=1000):
    """Compute FFT of an audiofile.

    Args:
        infile (_type_): audiofile
        maxfreq (int, optional): maximal frequency. Defaults to 1000.

    Returns:
        _type_: list of frequencies‚ and list of amplitudes.
    """
    sampFreq, sound = wavfile.read(infile)
    
    if len(sound.shape)==2:
        signal = sound[:,0]
    else:
        signal = sound

    size=len(signal)
    fft_spectrum = np.fft.rfft(signal, n=size)
    freq = np.fft.rfftfreq(size, d=1./sampFreq)
    fft_spectrum_abs = np.abs(fft_spectrum)
 
    i=0
    while i<len(freq) and freq[i]<=maxfreq:
        i+=1
    freq = freq[0:i]
    fft_spectrum_abs = fft_spectrum_abs[0:i]

    return freq, fft_spectrum_abs

def window_average(freq, fft_spectrum, window_size = 0.1 ):
    """Average fft_spectrum with a sliding window technique for low pass filtering.
   
        freq (_type_): list of frequency values
        fft_spectrum (_type_): list of fft values for the frequency values
        window_size (float, optional): The window_size as a fraction of an octave. Defaults to 0.1.

    Returns:
        _type_: The averaged fft spectrum.
    """
    averaged_fft_spectrum = []
    _freq = freq.copy()
    zeros = _freq==0
    _freq[zeros] = 1
    log_freq = np.log2(_freq)
    log_freq[zeros] = 0
    for i in range(len(fft_spectrum)):
        window = (log_freq>log_freq[i]-window_size) & (log_freq<log_freq[i]+window_size)
        avg = np.mean(fft_spectrum[window])
        averaged_fft_spectrum.append(avg)
    averaged_fft_spectrum = np.array(averaged_fft_spectrum)
    return averaged_fft_spectrum

# retrieve all local maxima 
# also merge maxima that are close to each other
def get_maxima(freq, averaged_fft_spectrum, min_freq=60):
    """Retrieve all local maxima. Also merge maxima that are close to each other.

    Args:
        freq (_type_): List of frequencies
        averaged_fft_spectrum (_type_): List of amplitudes.
        min_freq (_type_): Ignore clusterr below min_freq

    Returns:
        _type_: list of integers of the positions of the maxima
    """
    i_maxima = argrelextrema(averaged_fft_spectrum, np.greater)[0]
    
    i_maxima = np.array(i_maxima)
    
    maxima = freq[i_maxima]
    maxima = maxima[maxima>min_freq]
    log_max = np.log2(maxima)

    counter=0
    len_clusters_before = -1
    stop = False

    while not stop:
        counter+=1
        if counter==200:
            break

        distance_matrix = []
        for y in range(len(log_max)):
            row = []
            for x in range(len(log_max)):
                row.append(np.abs(log_max[x] - log_max[y]))
            distance_matrix.append(row)    
        distance_matrix = np.array(distance_matrix)

        clusters = []
        for i in range(len(distance_matrix)):
            c = np.arange(len(distance_matrix))[distance_matrix[i]<0.1]
            clusters.append(c)

        clusters = {str(c):c for c in clusters}.values() # duplicate removal
        clusters = list(clusters)

        for i in range(len(clusters)):
            cluster_amplitudes = averaged_fft_spectrum[i_maxima[clusters[i]]]
            max_i = np.argmax(cluster_amplitudes)
            clusters[i] = clusters[i][max_i]

        clusters=np.array([int(x) for x in clusters])

        maxima = maxima[clusters]
        log_max = np.log2(maxima)

        if len_clusters_before == len(clusters):
            break
        len_clusters_before = len(clusters)

    return maxima
      