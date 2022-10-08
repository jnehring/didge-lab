'''
Help finding the necessary frequency resolution for cadsd

run it:
python -m cad.bin.get_freq_resolution
'''

from cad.calc.conv import freq_to_note_and_cent, note_to_freq, note_name
import pandas as pd
import numpy as np

resolutions=[0, 1, 2]
df={"note-number": [], "note-name": [], "target-freq": []}
for r in resolutions:
    df[f"cent-diff{r}"] = []
for r in resolutions:
    df[f"freq-{r}"] = []

start_note=-36
for note in np.arange(start_note, start_note+24, 2):
    df["note-number"].append(note)
    df["note-name"].append(note_name(note))
    target_freq=note_to_freq(note)
    df["target-freq"].append(target_freq)

    for r in resolutions:
        f=round(target_freq, r)
        note, cent=freq_to_note_and_cent(f)
        print(target_freq, f, cent)
        df[f"cent-diff{r}"].append(round(cent))
        df[f"freq-{r}"].append(f)

df=pd.DataFrame(df)
print(df)
