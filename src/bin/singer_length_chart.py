# helper to find the length of a didgeridoo that has max / min pressure of multiple overtones at the bell

from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent, freq_to_wavelength
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

fundamental_freq=note_to_freq(-31) # -31 = D
n_overtone=5
f_overtone=fundamental_freq*(n_overtone+1)
f_overtone=440

tones=sorted([1,2,3])
tones=[1,2,3]
tones=sorted([1,5,6,3])


def bore_plot():
    data=[]
    for i in tones:
        name="fundamental" if i==1 else f"overtone {i-1}"
        freq=fundamental_freq*i
        note,cent=freq_to_note_and_cent(freq)
        note=note_name(note)
        name += f", {note}, {freq:.2f} Hz"

        wavelength=freq_to_wavelength(freq)

        #for x in np.arange(1300, 1800, 0.1):
        for x in np.arange(0, 2000, 1):
            data.append([x, abs(np.sin(x*2*np.pi/wavelength)), name])

    df=pd.DataFrame(data, columns=["distance from mouth piece [mm]", "amplitude", "tone"])
    sns.lineplot(data=df, x="distance from mouth piece [mm]", y="amplitude", hue="tone")

bore_plot()
wavelength_overtone=freq_to_wavelength(f_overtone)
print(f"overtone {n_overtone} at {f_overtone:.2f} Hz, wavelength {wavelength_overtone}")
print("maxima")
for i in range(3):
    print(i, (i+1/4)*wavelength_overtone)

sns.set(rc={'figure.figsize':(16,6)})

plt.grid()
plt.legend(loc='lower right')
plt.savefig("singer.jpg")
plt.show()
