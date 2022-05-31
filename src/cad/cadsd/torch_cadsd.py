import torch
from cad.cadsd.cadsd_py import Segment, cadsd_Ze
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

fmin=30
fmax=800

class DidgeModel(torch.nn.Module):

    def __init__(self):

        length=1800
        d0=32
        d1=74
        n_segments=50

        self.segments=[]

        for i in range(n_segments+1):
            x=x*length/n_segments
            y=d0+(d1-d0)*x(m_segments)
            
            segments.append([
                torch.nn.Parameter(torch.randn(x)),
                torch.nn.Parameter(torch.randn(y)),
            ])

    def forward(self):
        segments=Segment.create_segments_from_geo(self.segments)
        impedances=[]
        for f in range(fmin, fmax):
            impedances.append(cadsd_Ze(segments, f))
        return impedances

def train():

    f0=73
    target_freqs=[f0, 2*f0]
    width=10

    x=np.arange(fmin, fmax)
    y=[]
    for _x in x:
        f=np.argmin([np.abs(f-_x) for f in target_freqs])
        f=target_freqs[f]
        d=np.abs(_x-f)
        if d>width:
            y.append(0)
        else:
            y.append(np.power(width-d, 2))
    y=np.array(y)
    y=y/y.max()
    


    # x=np.arange(fmin, fmax)
    # y=[]
    # for _x in x:
    #     _y=0
    #     for f in target_freqs:
    #         d=np.abs(_x-f)
    #         d=np.log2(d) if d!=0 else d

    #         d=np.power(d, 0.5)
    #         _y+=d

    #     y.append(_y)
    # y=np.array(y)
    # y=1-y/y.max()
    # y=y/y.max()

    # new_y=[]
    # for _y in y:
    #     if _y<0.5:
    #         _y*=(0.5-_y)/0.5
    #     new_y.append(_y)
    # y=new_y

    # # further stretch it
    # # y=np.



    plt.plot(x,y)
    plt.show()


if __name__=="__main__":

    train()
