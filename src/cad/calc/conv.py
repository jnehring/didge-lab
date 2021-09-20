import math

def note_to_freq(note):
    return 440*pow(2, note/12)

def note_name(note):
    note+=48
    octave=math.floor(note/12)
    number=note%12
    notes=["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    name=str(notes[number]) + str(octave)
    return name

def freq_to_note(freq):
    return 12* (math.log2(freq) - math.log2(440))
