import math

def distance(v1, v2):
    d1=v1[0]-v2[0]
    d2=v1[1]-v2[1]
    d3=v1[2]-v2[2]
    return math.sqrt(d1*d1 + d2*d2 + d3*d3)

def length(v):
    return math.sqrt(
        v[0]*v[0] +
        v[1]*v[1] +
        v[2]*v[2]
    )   

def add_skalar(v1, s):
    return (
        v1[0]+s,
        v1[1]+s,
        v1[2]+s
    )

def add_vektor(v1, v2):
    return (
        v1[0]+v2[0],
        v1[1]+v2[1],
        v1[2]+v2[2]
    )

def substract_vektor(v1, v2):
    return (
        v1[0]-v2[0],
        v1[1]-v2[1],
        v1[2]-v2[2]
    )

def mult_skalar(v1, s):
    return (
        v1[0]*s,
        v1[1]*s,
        v1[2]*s
    ) 
