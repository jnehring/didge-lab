import pyximport; pyximport.install()
import cad.cadsd.cadsd

def get_impedance_spektrum(geo, from_freq, to_freq, stepsize):

    segments=cadsd.Segment.create_segments_from_geo(geo)
    spektrum={
        "freq": [],
        "impedance": []
    }

    for freq in np.arange(from_freq, to_freq, stepsize):
        spektrum["freq"].append(freq)
        impedance=cadsd.cadsd_Ze(segments, freq)
        spektrum["impedance"].append(impedance)
    
    return pd.DataFrame(spektrum)
