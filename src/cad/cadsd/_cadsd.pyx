#!python
#cython: language_level=3

import math
import cmath
cimport numpy as np
import pandas as pd
cimport cython
import numpy as npy

np.import_array()

cdef np.longdouble_t p = 1.2929
cdef np.longdouble_t n = 1.708e-5
cdef np.longdouble_t c = 343.37
cdef np.longdouble_t PI= 3.14159265358979323846 

cdef packed struct Segment:
    np.longdouble_t L, d0, d1, a0, a01, a1, phi, l, x1, x0, r0

def segment_from_geo(seg1, seg0):
    cdef np.longdouble_t L=seg1[0]-seg0[0]
    cdef np.longdouble_t d0=seg0[1]
    cdef np.longdouble_t d1=seg1[1]

    new_seg=Segment()
    new_seg["L"] = L
    new_seg["d0"] = d0
    new_seg["d1"] = d1

    new_seg["a0"] = PI * d0 * d0 / 4
    new_seg["a01"] = PI * (d0 + d1) * (d0 + d1) / 16
    new_seg["a1"] = PI * d1 * d1 / 4
    new_seg["phi"] = math.atan ((d1 - d0) / (2 * L))

    new_seg["l"] = (d1 - d0) / (2 * math.sin (new_seg["phi"]))
    new_seg["x1"] = d1 / (2 * math.sin (new_seg["phi"]))
    new_seg["x0"] = new_seg["x1"] - new_seg["l"]
    new_seg["r0"] = p * c / new_seg["a0"]

    return new_seg

def create_segments_from_geo(geo):

    segments=[]

    shape=[[x[0]/1000, x[1]/1000] for x in geo]
    for i_seg in range(1, len(shape)):
        seg1=shape[i_seg]
        seg0=shape[i_seg-1]
        seg=segment_from_geo(seg1, seg0)
        segments.append(seg)
    return segments

def ap_loop(w,x,y,z,t_seg):
    cdef np.longdouble_t L=t_seg["L"]
    d0=t_seg["d0"]
    d1=t_seg["d1"]

    a0 = t_seg["a0"]
    a01 = t_seg["a01"]
    a1 = t_seg["a1"]
    l = t_seg["l"]
    x0 = t_seg["x0"]
    x1 = t_seg["x1"]
    r0 = t_seg["r0"]

    rvw = math.sqrt (p * w * a01 / (n * PI))
    kw = w / c
    cdef np.complex128_t Tw =kw * 1.045 / rvw + (kw * (1.0 + 1.045 / rvw))*1j
    cdef np.complex128_t Zcw = r0 * (1.0 + 0.369 / rvw) - 1j*r0 * 0.369 / rvw

    cdef np.complex128_t ccoshlwl = cmath.cosh(Tw * l)
    cdef np.complex128_t csinhlwl = cmath.sinh(Tw * l)
    cdef np.complex128_t ccoshlwL = cmath.cosh(Tw * L)
    cdef np.complex128_t csinhlwL = cmath.sinh(Tw * L)

    if (d0 != d1):
        y[0][0] = x1 / x0 * (ccoshlwl - csinhlwl / (Tw * x1))
        y[0][1] = x0 / x1 * Zcw * csinhlwl
        y[1][0] = ((x1 / x0 - 1.0 / (Tw * Tw * x0 * x0)) * csinhlwl + Tw * l / ((Tw * x0) * (Tw * x0)) * ccoshlwl) / Zcw
        y[1][1] = x0 / x1 * (ccoshlwl + csinhlwl / (Tw * x0))
    else:
        y[0][0] = ccoshlwL
        y[0][1] = Zcw * csinhlwL
        y[1][0] = csinhlwL / Zcw
        y[1][1] = ccoshlwL

    # dot product
    z[0][0] = x[0][0] * y[0][0] + x[0][1] * y[1][0]
    z[0][1] = x[0][0] * y[0][1] + x[0][1] * y[1][1]
    z[1][0] = x[1][0] * y[0][0] + x[1][1] * y[1][0]
    z[1][1] = x[1][0] * y[0][1] + x[1][1] * y[1][1]

    x[0][0] = z[0][0]
    x[0][1] = z[0][1]
    x[1][0] = z[1][0]
    x[1][1] = z[1][1]

    return x,y,z

def ap (w, segments):

    cdef np.ndarray[np.complex128_t, ndim=2] x = npy.array([[1,0],[0,1]], dtype=npy.complex128)
    cdef np.ndarray[np.complex128_t, ndim=2] y = npy.array([[0,0],[0,0]], dtype=npy.complex128)
    cdef np.ndarray[np.complex128_t, ndim=2] z = npy.array([[0,0],[0,0]], dtype=npy.complex128)

    for t_seg in segments:
        x,y,z=ap_loop(w,x,y,z,t_seg)
    return z

def Za( np.longdouble_t w, segments):
    cdef Segment t_seg=segments[-1]

    cdef np.longdouble_t L = t_seg.L
    cdef np.longdouble_t d1 = t_seg.d1
    cdef np.longdouble_t a01 = t_seg.a01
    cdef np.longdouble_t r0 = t_seg.r0

    cdef np.longdouble_t rvw = math.sqrt (p * w * a01 / (n * PI))
    cdef np.complex128_t Zcw = (r0*(1.0 + 0.369 / rvw) - 1j*r0 * 0.369 / rvw)

    cdef np.complex128_t res = 0.5 * Zcw * (w * w * d1 * d1 / c / c + 1j*0.6 * L * w * d1 / c)	# from geipel

    return res

def cadsd_Ze (segments, f):
  cdef np.longdouble_t w = 2.0 * PI * f
  cdef np.complex128_t a = Za (w, segments)

  cdef np.ndarray[np.complex128_t, ndim=2] b = ap (w, segments)

  cdef np.longdouble_t Ze = abs ((a * b[0][0] + b[0][1]) / (a * b[1][0] + b[1][1]))
  return Ze

# def geo_fft (geo, gmax, offset):
#
#    fft={
#        "impedance": {},
#        "overblow": {},
#        "ground": {}
#    }
#
#    for key in fft.keys(): 
#        fft[key][0]=0
#
#    segments=Segment.create_segments_from_geo(geo)
#    for f in range(1, gmax):
#        fft["impedance"][f] = cadsd_Ze(segments, f)
#        fft["overblow"][f] = 0
#        fft["ground"][f] = 0
#
#
#    # search for peaks and valleys
#    peaks=[0,0]
#    vally=[0,0]
#
#    up=False
#    npeaks=0
#    nvally=0
#
#    freqs=fft["impedance"].keys()
#    for i in range(2, len(freqs)):
#        if fft["impedance"][i] > fft["impedance"][i-1]:
#            if npeaks and not up:
#                vally[nvally]=i-1
#                nvally+=1
#            up=True
#        else:
#            if up:
#                peaks[npeaks] = i-1
#                npeaks+=1
#            up=False 
#
#        if nvally>1:
#            break
#
#    if peaks[0]<0:
#        return None
#
#    k = 0.0001
#
#    mem0 = peaks[0]
#    mem0a = peaks[0]
#
#    mem0b = mem0a   
#
#    return fft
