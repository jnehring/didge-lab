from cad.cadsd.cadsd import CADSD
from cad.calc.geo import Geo
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

# perform fft analysis of a soundfile and normalize it
# returns a list of frequencies and a list of amplitudes
def do_fft(infile, maxfreq=1000):
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


def comparison_plot(sound_file : str, geo : list, didge_name=None):
    
    geo = Geo(geo)
    cadsd = geo.get_cadsd()

    ground_spektrum=cadsd.get_ground_spektrum()
    ground_freqs = np.array(list(ground_spektrum.keys()))
    ground_vols = np.array(list(ground_spektrum.values()))
    ground_vols -= ground_vols.min()
    ground_vols /= ground_vols.max()
    
    impedance_spektrum = cadsd.get_impedance_spektrum()
    impedance_freqs = impedance_spektrum.freq
    impedance_amps = impedance_spektrum.impedance
    
    impedance_amps -= impedance_amps.min()
    impedance_amps /= impedance_amps.max()

    freq, fft_spectrum_abs = do_fft(sound_file)
    fft_spectrum_abs = np.log2(fft_spectrum_abs)
    fft_spectrum_abs -= fft_spectrum_abs.min()
    fft_spectrum_abs /= fft_spectrum_abs.max()
    
    plt.plot(impedance_freqs, impedance_amps, label="berechnete impedanz")
    plt.plot(ground_freqs, ground_vols, label="berechneter grundton")
    plt.plot(freq, fft_spectrum_abs, label="gemessener grundton")
    
    title = ""
    if didge_name is not None:
        title += " " + str(didge_name)
    plt.title(title)
    plt.ylabel("")
    plt.xlim(0,1000)
    plt.legend()
    plt.show()

    