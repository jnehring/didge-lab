from cad.ui.ui import Window
import shutil
import numpy as np

class FFTWindow(Window):

    def __init__(self, fft=None):
        if fft is None:
            self.chart=""
        else:
            self.set_fft(fft)

    def set_fft(self, df):
        Window.__init__(self, "FFT")

        width=(shutil.get_terminal_size().columns-1) - len("1.0e+01 | ")
        height=15
        
        bins=[]

        maximum=df.impedance.max()

        df.impedance=np.log2(df.impedance)

        mini=df.impedance.min()

        bin_size=(df.freq.max()-df.freq.min())/width
        freq=df.freq.min()
        for i in range(width):
            y=df[(df.freq>=freq) & (df.freq<freq+bin_size)].impedance.max()
            bins.append(y)
            freq+=bin_size

        bins=np.array(bins)
        bins-=bins.min()
        maxi=bins.max()
        bins=bins*height/maxi
        bins=np.array([round(x) for x in bins])

        
        ticks=[mini, (maxi-mini)/2, maxi]
        ticks=[f"{x:.2e}" for x in ticks]

        chart=""
        for y in range(height):

            row=""
            tick=""

            for x in range(width):
                if bins[x]>=height-y:
                    row+="x"
                    tick=f"{(2^bins[x]):.1e}"
                else:
                    row += " "
            chart += tick + " | "+ row + "\n"

        num_ticks=4
        min_freq=str(int(df.freq.min())) + " "
        max_freq=" " + str(int(df.freq.max()))

        label = " frequency (hz) "
        pad=width - len(min_freq) - len(max_freq) - len(label)
        pad/=2
        pad="-"*int(np.ceil(pad))
        ticks=(" " * (len(tick)+3)) + min_freq + pad + label + pad + max_freq
        chart += ticks + "\n"
        
        self.chart=chart

    def _render(self):
        return self.chart