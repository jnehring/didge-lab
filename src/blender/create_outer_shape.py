# Create outer shape to a didgelab geometry with smoothing.
 
import matplotlib.pyplot as plt
import math
import numpy as np

from scipy import signal
from scipy.signal import butter, lfilter
from scipy.signal import freqs

import argparse
import json
import os

from convert_to_blender import convert_to_blender

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

def smooth_geo(geo, resolution=10, thickness=5, Wn=0.1, skip_mouthpiece=0):
    x_orig,y_orig=zip(*geo)
    
    x_new=list(np.arange(skip_mouthpiece, x_orig[-1], resolution))
    for x in x_orig:
        if x not in x_new and x>=skip_mouthpiece:
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
        b, a = signal.butter(1, Wn)
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

    if skip_mouthpiece>0:
        for i in range(len(x_orig)):
            if x_orig[i]>=skip_mouthpiece:
                break

        mouthpiece_x=list(x_orig[0:i])
        mouthpiece_y=list(y_orig[0:i])

        # print(mouthpiece_y)
        # print(y_outer)

        x_new=[*mouthpiece_x, *x_new]
        y_inner=[*mouthpiece_y, *y_inner]
        y_outer=[*[y + thickness for y in mouthpiece_y], *y_outer]

    inner_geo=list(zip(x_new, y_inner))
    smooth_outer_geo=list(zip(x_new, y_outer))

    return inner_geo, smooth_outer_geo

def add_simple_wall(geo, thickness):
    outer_geo=np.copy(geo)
    outer_geo=[[int(s[0]), int(s[1]+thickness)] for s in outer_geo]
    return outer_geo

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Create outer shape to a didgelab geometry with smoothing.')
    parser.add_argument('-infile', type=str, required=True)
    parser.add_argument('-resolution', type=float, default=1, help="Put a segment every resolution mm.")
    parser.add_argument('-thickness', type=int, default=5, help="Wall thickness in mm. default=5.")
    parser.add_argument('-skip_mouthpiece', type=int, default=20, help="Do not add additional segments in the first -skip_mouthpiece mm of the didge.")
    parser.add_argument('-outfolder', type=str, default="./")
    parser.add_argument('-no_smooth', action="store_true", help="switch of lp filtering")
    parser.add_argument('-wn', type=float, default=0.1, help="butterdingens. default=0.1")
    args = parser.parse_args()

    f=open(args.infile, "r")
    inner_geo=json.load(f)
    f.close()

    # if args.no_smooth:
    #     outer_geo=add_simple_wall(inner_geo, args.thickness)
    # else:
    inner_geo, outer_geo=smooth_geo(inner_geo, resolution=args.resolution, thickness=args.thickness, Wn=args.wn, skip_mouthpiece=args.skip_mouthpiece)

    geos={
        "inner": inner_geo,
        "outer": outer_geo
    }

    outer_shape_file=os.path.join(args.outfolder, "outer_shape.json")
    f=open(outer_shape_file, "w")
    print("created " + os.path.abspath((outer_shape_file)))
    f.write(json.dumps(geos))
    f.close()

    y_offset=50     # artificial additional wall thickness for better visualization
    outer_geo=[[a[0], a[1]+y_offset] for a in outer_geo]
    for geo in [inner_geo, outer_geo]:
        y_offset=0
        x,y=zip(*geo)
        y_oben=[y_offset+a/2 for a in y]
        y_unten=[y_offset-a/2 for a in y]
        plt.plot(x,y_oben, 'k')
        plt.plot(x,y_unten, 'k')

    plt.xlim([0, inner_geo[-1][0]])
    plt.ylim([-1*inner_geo[-1][0]/2, inner_geo[-1][0]/2])
    outfile=os.path.join(args.outfolder, "didge_shape_plot.png")
    plt.savefig(outfile)
    print("created " + os.path.abspath(outfile))
    print("number of segments in inner shape", len(inner_geo))
    print("number of segments in outer shape", len(outer_geo))

    outfile=os.path.join(args.outfolder, "blender_bridge.json")
    convert_to_blender(outer_shape_file, outfile)
    print("created " + os.path.abspath(outfile))