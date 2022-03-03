# python -m cad.calc.util.overtone_finder
 
import matplotlib.pyplot as plt
import numpy as np
from cad.calc.conv import note_to_freq, freq_to_wavelength

# return the distances of the maxima of the wave from the origin
def get_maxima(note):
    freq=note_to_freq(note)
    l=freq_to_wavelength(freq)
    x=l/4
    r=[]
    i=1
    while x<3000:
        r.append(x)
        x=(1+i*2)*l/4 
        i+=1

    return r

def plot_note(note):
    x=np.arange(3000)
    l=freq_to_wavelength(note_to_freq(note))
    y=[abs(np.sin(2*np.pi*a/l)) for a in x]
    plt.plot(x,y)


def comp_tones(n1, n2):
    print(n1, note_to_freq(n1))
    print(n2, note_to_freq(n2))

    max1=get_maxima(n1)
    max2=get_maxima(n2)

    diff=[]
    for x in max1:
        for y in max2:
            d=abs(np.log2(x) - np.log2(y))
            diff.append((d, x, y))
    diff=sorted(diff, key=lambda x : x[0])

    for d in diff[0:3]:
        print(d, freq_to_wavelength(d[1]))

#comp_tones(3,7)

n1=8
n2=12

print("note 1", n1, "freq", note_to_freq(n1))
print("note 2", n2, "freq", note_to_freq(n2))

m1=get_maxima(n1)
m2=get_maxima(n2)

ol=(m1[7]+ m2[9])/2
print("optimal length ", ol)


#plt.show()