import pandas as pd
from cad.calc.conv import freq_to_note_and_cent, note_name, note_to_freq

if __name__=="__main__":
    
    base_freq=note_to_freq(-31)
    i=1
    df=[]
    while i*base_freq<1000:
        freq=base_freq*i
        note_number, cent=freq_to_note_and_cent(freq)
        df.append([note_name(note_number), freq, note_number])
        i+=1

    df=pd.DataFrame(df, columns=["note_name", "freq", "note_number"])
    print(df)