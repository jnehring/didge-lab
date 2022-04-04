import matplotlib.pyplot as plt
import math
import matplotlib.pyplot as plt
import numpy as np

from scipy import signal
from scipy.signal import butter, lfilter
from scipy.signal import freqs

import argparse
import json


def diameter_at_x(geo, x):

    if x==0:
        return geo[0][1]

    for i in range(len(geo)):
        if x<geo[i][0]:
            break

    x1=geo[i-1][0]
    y1=geo[i-1][1]
    x2=geo[i][0]
    y2=geo[i][1]

    ydiff=(y2-y1)/2
    xdiff=(x2-x1)

    winkel=math.atan(ydiff/xdiff)
    y=math.tan(winkel)*(x-x1)*2+y1
    return y

def smooth_geo(geo, resolution=10, thickness=5):
    x_orig,y_orig=zip(*geo)

    x_new=list(np.arange(0, x_orig[-1], resolution))

    for x in x_orig:
        if x not in x_new:
            x_new.append(x)

    x_new=sorted(x_new)

    y_corrections={}

    max_iter=200

    y_inner=[]
    for x in x_new:
        y_inner.append(diameter_at_x(geo, x))
        
    for iter in range(max_iter):
        y_outer=[a+thickness for a in y_inner]
        
        for x,y in y_corrections.items():
            y_outer[x]+=y

        # Create an order 3 lowpass butterworth filter:
        b, a = signal.butter(1, 0.1)
        # Apply the filter to xn. Use lfilter_zi to choose the initial condition of the filter:
        zi = signal.lfilter_zi(b, a)
        z, _ = signal.lfilter(b, a, y_outer, zi=zi*y_outer[0])
        y_outer = signal.filtfilt(b, a, y_outer)

        # find all places where thickness is smaller thickness parameter

        all_good=True
        for i in range(len(y_outer)):
            if y_outer[i]-y_inner[i] < thickness:
                correction = y_corrections[i]+1 if i in y_corrections else 1
                y_corrections[i]=correction
                #=y_outer[i]-y_inner[i]
                all_good=False

        def at_x(x):
            for i in range(len(y_inner)):
                if x_new[i]==x:
                    break
    
        if all_good:
            break

    inner_geo=list(zip(x_new, y_inner))
    smooth_outer_geo=list(zip(x_new, y_outer))
    return inner_geo, smooth_outer_geo

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Prepare blender import')
    parser.add_argument('-infile', type=str, required=True)
    parser.add_argument('-resolution', type=float, default=5, help="Put a segment every resolution mm.")
    parser.add_argument('-thickness', type=int, default=5, help="Wall thickness in mm.")
    parser.add_argument('-outfile', type=str, default="out.json")
    parser.add_argument('-plot', action="store_true", default="make a plot")
    args = parser.parse_args()

    f=open(args.infile, "r")
    geo=json.load(f)
    f.close()

    inner_geo, smooth_outer_geo=smooth_geo(geo, resolution=args.resolution, thickness=args.thickness)
    geos={
        "inner": inner_geo,
        "outer": smooth_outer_geo
    }
    f=open(args.outfile, "w")
    f.write(json.dumps(geos))
    f.close()

    if args.plot:

        y_offset=50
        smooth_outer_geo=[[a[0], a[1]+y_offset] for a in smooth_outer_geo]
        for geo in [inner_geo, smooth_outer_geo]:
            y_offset=0
            x,y=zip(*geo)
            y_oben=[y_offset+a/2 for a in y]
            y_unten=[y_offset-a/2 for a in y]
            plt.plot(x,y_oben, 'k')
            plt.plot(x,y_unten, 'k')

        # x,y_inner=zip(*inner_geo)
        # x,y_outer=zip(*smooth_outer_geo)

        # plt.fill_between(x, y_inner, y_outer)
        # plot_geo_2d(inner_geo)
        # plot_geo_2d([[a[0], a[1]+50] for a in smooth_outer_geo])
        plt.xlim([0, inner_geo[-1][0]])
        plt.ylim([-1*inner_geo[-1][0]/2, inner_geo[-1][0]/2])
        plt.savefig("plot.png")
    