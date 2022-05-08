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

import sys

# from convert_to_blender import convert_to_blender
from blender_didge_shape import shape_from_geo, connect_ends, log, vertex_circle, init_data

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

def smooth_geo(geo, args):
    x_orig,y_orig=zip(*geo)
    
    # create new inner shape
    x_new_inner=list(np.arange(0, x_orig[-1], args.inner_resolution))
    for x in x_orig:
        if x not in x_new_inner:
            x_new_inner.append(x)

    x_new_inner=sorted(x_new_inner)

    y_corrections={}

    max_iter=200

    y_inner=[]
    for x in x_new_inner:
        y_inner.append(diameter_at_x(geo, x))

    # create new outer shape
    x_new_outer=list(np.arange(0, x_orig[-1], args.outer_resolution))
    if x_new_outer[-1]<x_orig[-1]:
        x_new_outer.append(x_orig[-1])
    y_inner_regular=[diameter_at_x(geo, x) for x in x_new_outer]
    for iter in range(max_iter):
        y_outer=[a+args.thickness for a in y_inner_regular]

        for x,y in y_corrections.items():
            y_outer[x]+=y

        # Create an order 3 lowpass butterworth filter:
        b, a = signal.butter(1, args.wn)
        # Apply the filter to xn. Use lfilter_zi to choose the initial condition of the filter:
        zi = signal.lfilter_zi(b, a)
        z, _ = signal.lfilter(b, a, y_outer, zi=zi*y_outer[0])
        y_outer = signal.filtfilt(b, a, y_outer)

        # find all places where thickness is smaller thickness parameter

        all_good=True
        for i in range(len(y_outer)):
            if y_outer[i]-y_inner_regular[i] < args.thickness:
                correction = y_corrections[i]+1 if i in y_corrections else 1
                y_corrections[i]=correction
                #=y_outer[i]-y_inner[i]
                all_good=False

        def at_x(x):
            for i in range(len(y_inner)):
                if x_new_inner[i]==x:
                    break
    
        if all_good:
            break

    inner_geo=list(zip(x_new_inner, y_inner))
    smooth_outer_geo=list(zip(x_new_outer, y_outer))

    return inner_geo, smooth_outer_geo

def merge_geos(new_geo, old_geo):
    for g in old_geo:
        if g[0]<new_geo[0][0] or g[0]>=new_geo[-1][0]:
            new_geo.append(g)
    return new_geo

def add_mouthpiece(inner_geo, outer_geo):

    inner_mouthpiece_r=4
    inner_mouthpiece_resolution=10

    # rundung im inneren teil
    x=np.arange(0,inner_mouthpiece_r,1/inner_mouthpiece_resolution)
    def arc_innen(x, r, geo):
        y=[]
        for _x in x:
            _x=r-_x
            _y=r-np.sqrt(r*r - _x*_x)
            _y+=diameter_at_x(geo, _x)
            y.append(_y)
        return y
    y=arc_innen(x,inner_mouthpiece_r,inner_geo)
    geo=list(zip(x,y))

    inner_geo=merge_geos(geo, inner_geo)

    # rundung am ende des aeusseren teils

    mouthpiece_outer_geo=[]
    for g in outer_geo:
        if g[0]>20:
            break
        mouthpiece_outer_geo.append(g)


    mouthpiece_l=20
    mouthpiece_d=20
    x=np.arange(-3, 10, 1/mouthpiece_l)

    def sigmoid(x, d):
        return d*(1-1 / (1 + math.exp(-x)))

    y=[sigmoid(a, mouthpiece_d) for a in x]
    x=mouthpiece_l*(x-x.min())/x.max()

    for i in range(len(x)):
        y[i]+=diameter_at_x(mouthpiece_outer_geo, x[i])

    geo=list(zip(x,y))
    mouthpiece_outer_geo=merge_geos(geo, mouthpiece_outer_geo)

    new_outer_geo=[mouthpiece_outer_geo[-1]]
    for g in outer_geo:
        if g[0]>mouthpiece_outer_geo[-1][0]:
            new_outer_geo.append(g)

    return inner_geo, new_outer_geo, mouthpiece_outer_geo

def make_blender_form(inner_geo, outer_geo, mouthpiece, n_circle_segments=64):

    meshes=[
        {
            "data": shape_from_geo(inner_geo, n_circle_segments),
            "name": "inner_geo"
        },
        {
            "data": shape_from_geo(outer_geo, n_circle_segments),
            "name": "outer_geo"
        },
        {
            "data": shape_from_geo(mouthpiece, n_circle_segments),
            "name": "mouthpiece"
        }
    ]

    ends=connect_ends(meshes[0]["data"], meshes[2]["data"], n_circle_segments, lower=True)
    meshes.append({"data": ends, "name": "lower_end"})

    ends=connect_ends(meshes[0]["data"], meshes[1]["data"], n_circle_segments, lower=False)
    meshes.append({"data": ends, "name": "upper_end"})

    return meshes

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Create outer shape to a didgelab geometry with smoothing.')
    parser.add_argument('-infile', type=str, required=True)
    parser.add_argument('-inner_resolution', type=float, default=3, help="Put an inner segment every resolution mm. default=5")
    parser.add_argument('-outer_resolution', type=float, default=5, help="Put an outer segment every resolution mm. default=10")
    parser.add_argument('-thickness', type=int, default=5, help="Wall thickness in mm. default=5.")
    parser.add_argument('-outfolder', type=str, default="./")
    parser.add_argument('-wn', type=float, default=0.1, help="butterdingens. default=0.1")
    parser.add_argument('-inner_only', action="store_true", help="necessary inner rings only")
    parser.add_argument('-no_mouthpiece', action="store_true", help="do not add the mouthpiece")
    args = parser.parse_args()

    f=open(args.infile, "r")
    inner_geo=json.load(f)
    f.close()

    if args.inner_only:
        geos={
            "inner": inner_geo
        }
        outer_shape_file=os.path.join(args.outfolder, "outer_shape.json")
        f=open(outer_shape_file, "w")
        print("created " + os.path.abspath((outer_shape_file)))
        f.write(json.dumps(geos))
        f.close()

        print("number of segments in inner shape", len(inner_geo))

        outfile=os.path.join(args.outfolder, "blender_bridge.json")
        convert_to_blender(outer_shape_file, outfile, inner_only=True)
        print("created " + os.path.abspath(outfile))
    else:

        inner_geo, outer_geo=smooth_geo(inner_geo, args)

        inner_geo, outer_geo, mouthpiece_outer_geo=add_mouthpiece(inner_geo, outer_geo)

        geos={
            "inner": inner_geo,
            "outer": outer_geo
        }

        # outer_shape_file=os.path.join(args.outfolder, "outer_shape.json")
        # f=open(outer_shape_file, "w")
        # print("created " + os.path.abspath((outer_shape_file)))
        # f.write(json.dumps(geos))
        # f.close()

        y_offset=50     # artificial additional wall thickness for better visualization
        outer_geo_plot=[[a[0], a[1]+y_offset] for a in outer_geo]
        for geo in [inner_geo, outer_geo_plot]:
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
        print("number of segments in mouthpiece", len(mouthpiece_outer_geo))

        outfile=os.path.join(args.outfolder, "blender_bridge.json")
        meshes=make_blender_form(inner_geo, outer_geo, mouthpiece_outer_geo)
        f=open(outfile, "w")
        f.write(json.dumps(meshes))
        f.close()

        # convert_to_blender(outer_shape_file, outfile)
        print("created " + os.path.abspath(outfile))