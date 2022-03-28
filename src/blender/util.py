import matplotlib.pyplot as plt
import math

def plot_geo_2d(geo):
    y_offset=1000
    x,y=zip(*geo)
    y_oben=[y_offset+a/2 for a in y]
    y_unten=[y_offset-a/2 for a in y]
    plt.plot(x,y_oben)
    plt.plot(x,y_unten)


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
