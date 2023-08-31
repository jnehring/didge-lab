import numpy as np
from cad.calc.geo import Geo
from .fft import do_fft

def quantize(freq, amp, size=1, min_freq=35, max_freq=1000):
    """Bring the signal to a new frequency raster.

    Args:
        freq (_type_): list of frequencies
        amp (_type_): list of amplitudes
        size (int, optional): size of the raster. Defaults to 1.
        min_freq (int, optional): minimum frequency. Defaults to 35.
        max_freq (int, optional): maximum frequency. Defaults to 1000.

    Returns:
        _type_: New lists of frequencies and amplitudes
    """
    qfreqs = np.arange(min_freq, max_freq, size) + size/2
    qamps = []
    for f in qfreqs:
        window = (freq>f-size) & (freq<f+size)
        qamps.append(np.mean(amp[window]))
    qamps = np.array(qamps)
    return qfreqs, qamps
 
def ground_spectrum_difference(sound_file : str, geo : list):
    """Return the difference between the computed and measured ground sound spektra.

    Args:
        sound_file (str): _description_
        geo (list): _description_

    Returns:
        _type_: _description_
    """
    geo = Geo(geo)
    cadsd = geo.get_cadsd()

    ground_spektrum=cadsd.get_ground_spektrum()
    ground_freqs = np.array(list(ground_spektrum.keys()))
    ground_vols = np.array(list(ground_spektrum.values()))
    ground_vols -= ground_vols.min()
    ground_vols /= ground_vols.max()
    
    freq, fft_spectrum_abs = do_fft(sound_file)
    fft_spectrum_abs = np.log2(fft_spectrum_abs)
    fft_spectrum_abs -= fft_spectrum_abs.min()
    fft_spectrum_abs /= fft_spectrum_abs.max()

    ground_freqs, ground_vols = quantize(ground_freqs, ground_vols)
    freqs, fft_spectrum = quantize(freq, fft_spectrum_abs)

    diff = [np.power(ground_vols[i]-fft_spectrum[i], 2) for i in range(len(ground_vols))]
    diff = np.sum(diff)
    return diff