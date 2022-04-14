#Create a circular path for Blender 2.42a
import Blender
from Blender import *
import math
from math import *
   
def makeCircle(passedNumberOfPoints, passedRadius):
    c = Curve.New()
    c.setPathLen(300)
    c.setFlag(8)

    z = 0         # 2D Drawing for now.
    w = 1         #Weight is 1.
    final_x = 0
    final_y = 0
    angleStep = 360/ passedNumberOfPoints
    for ang in range(0, 359,angleStep):
        x = passedRadius * math.cos(math.radians(ang))
        y = passedRadius * math.sin(math.radians(ang))
        if (ang ==0):
            final_x = x
            final_y = y
            c.appendNurb([x,y,z,w])
            c[0].type = 0      # Poly line
        else:
            c.appendPoint(0,[x,y,z,w,0])  # Can add tilt here with w.
    c.appendPoint(0,[final_x,final_y,z,w,0]) # Can add tilt here.
    c.update()
    scn = Scene.GetCurrent()     # New Curve and add to Scene.
    ob = Object.New('Curve')
    ob.setName ("PolyBezier")
    ob.link(c)
    scn.link(ob)
    ob.sel = 1         # Make active and selected
makeCircle(16,5)
