import copy
import pandas as pd

class Geo:

    def __init__(self, infile=None, geo=None):
        self.geo=[]

        if infile != None:
            self.geo = self.read_geo(infile)

        if geo != None:
            self.geo=geo

    @classmethod
    def make_cone(cls, length, d1, d2, n_segments):
        shape=[]
        shape.append([0, d1])

        z=(d2-d1)/2
        angle=math.atan(z/length)
        for i in range(1, n_segments):
            x=length*i/(n_segments-1)
            y=2*x*math.tan(angle) + d1
            shape.append([x,y])
        return Geo(geo=shape)

    def read_geo(self, infile):
        f=open(infile)
        geo=[]
        for line in f:
            line=line[0:-1].split(" ")
            geo.append([float(line[0]), float(line[1])])
        f.close()
        return geo

    def write_geo(self, outfile):
        f=open(outfile, "w")
        for segment in self.geo:
            seg=f"{segment[0]:.2f} {segment[1]:.2f}\n"
            f.write(seg)
        f.close()

    def stretch(self, factor):
        for i in range(0, len(self.geo)):
            self.geo[i][0]*=factor

    def copy(self):
        geo=copy.deepcopy(self.geo)
        return Geo(geo=geo)

    # scale all geometries. use it to convert eg. mm to m
    def scale(self, factor):
        for i in range(0, len(self.geo)):
            self.geo[i][0]*=factor
            self.geo[i][1]*=factor
            
    def make_bubble(self, pos, width, height):
        index=0
        for i in range(len(self.geo)):
            if self.geo[i+1][0]>pos:
                index=i
                break
        
        left=self.geo[0:index+1]
        right=self.geo[index+1:]
        new_geo=left + [
            [pos-width/2, self.geo[index][1]],
            [pos, height],
            [pos+width/2, self.geo[index+1][1]],
        ] + right
        self.geo=new_geo
        
    def move_segments_x(self, start, end, offset):
        for i in range(start, end+1):
            self.geo[i][0]+=offset
            pass

    def length(self):
        return self.geo[-1][0]

    def segments_to_str(self):
        df={}
        for x in ["x", "y"]:
            df[x]=[]
        for i in range(0, len(self.geo)):
            df["x"].append(int(self.geo[i][0]))
            df["y"].append(int(self.geo[i][1]))
        df=pd.DataFrame(df)
        return str(df)
