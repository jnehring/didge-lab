# calculate the necessary resolution to achieve a tuning as exact as 1 cent
from cad.calc.conv import freq_to_note_and_cent, note_to_freq, note_name

for freq in range(35, 1000):
    note, cent = freq_to_note_and_cent(freq)
    print(freq, note_name(note), cent)

#notes=list(range(-45,15))

# for note in notes:
#     print(note, note_to_freq(note))

