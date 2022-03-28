
import math
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt

# split circle in how many segments?
n_circle_segments=64

# add additional rings every n_additional_segments mm
n_additional_segments=3

def vertex_circle(segments, z, r):
    """ Return a ring of vertices """
    verts = []

    for i in range(segments):
        angle = (math.pi*2) * i / segments
        verts.append((r*math.cos(angle), r*math.sin(angle), z))

    return verts

def shape_from_geo(geo, data):
    
    # create first ring
    offset_last_circle_vert=len(data["verts"])
    last_ring_edge_start=len(data["edges"])

    z=geo[0][0]/1000
    r=0.5*geo[0][1]/1000
    circle0=vertex_circle(n_circle_segments, z, r)
    data["verts"].extend(circle0)
    for i in range(n_circle_segments):
        next=i+1
        if i==n_circle_segments-1:
            next=offset_last_circle_vert
        data["edges"].append((i, next))
        # print("add bottom edge", len(data["edges"])-1)

    for g in geo[1:]:

        z=g[0]/1000
        r=0.5*g[1]/1000
        
        circle1=vertex_circle(n_circle_segments, z, r)

        vert_start=len(data["verts"])
        data["verts"].extend(circle1)
        
        this_ring_edge_start=len(data["edges"])
        
        for i in range(n_circle_segments):
            next=vert_start+i+1
            if i==n_circle_segments-1:
                next=vert_start
            data["edges"].append((vert_start+i, next))
            # print("add top edge", len(data["edges"])-1)

        for i in range(n_circle_segments):
            data["edges"].append((vert_start+i, offset_last_circle_vert+i))
            # print(f"add vertical edge", len(data["edges"]))
            
            e1=data["edges"][this_ring_edge_start+i] # top edge
            e2=data["edges"][last_ring_edge_start+i] # bottom edge
            data["faces"].append((e1[0],e1[1],e2[1],e2[0]))
                    
        last_ring_edge_start=this_ring_edge_start
        offset_last_circle_vert=vert_start
    return data

def plot_3d(data):
    fig = plt.figure()
    ax = Axes3D(fig, auto_add_to_figure=False)
    fig.add_axes(ax)
    x = [0,1,1,0]
    y = [0,0,1,1]
    z = [0,1,0,1]
    verts = [list(zip(x,y,z))]
    ax.add_collection3d(Poly3DCollection(verts))
    plt.show()


if __name__=="__main__":

    data = {
        'verts': [],
        'edges': [],
        'faces': [],
    }
    geo=[[0, 32], [119.9958769849766, 33.60786924930998], [182.96338939932383, 37.43993858124537], [229.31303306092116, 37.65868840095003], [243.87150359250768, 44.24922301095391], [248.22661301651374, 44.66872200645895], [273.35700590490666, 45.427288404108324], [325.1833660559223, 45.10078689004896], [326.6977955401382, 38.56326921940415], [331.3271419201785, 39.24648289540542], [348.80183650206857, 43.44272291801225], [430.9911964176373, 36.58658612297562], [467.1100014503583, 38.75489455260514], [656.2303357738663, 43.14580720660788], [674.7045855405672, 42.09763460759996], [788.1166743193038, 45.731774426101126], [800.7700549159376, 48.91416216097986], [874.3223026858111, 57.48849785851295], [894.4633095356007, 57.85511636112676], [920.7665646046486, 62.810078863961245], [924.8861710152711, 60.406541693482154], [965.9223894013795, 52.92986907805038], [993.5297817069403, 47.8899396101002], [1019.7355557222457, 45.38388648475607], [1053.7014100144995, 51.906767868800614], [1056.08323493601, 51.31169232421349], [1167.4257484469804, 61.68647957633659], [1246.3874724224754, 65.64353932959351], [1319.8878127066603, 83.97728075004777], [1349.4583898219896, 115.89351882544594], [1380.2817590427794, 114.68014975992207], [1413.7176032103646, 94.53429022929657], [1469.3136630077106, 124.90807502454308], [1509.405056810938, 137.6973360550101], [1522.1553223428134, 131.80498827396133], [1577.9706393666918, 117.21227761742348], [1583.3482983545491, 93.28860915227246], [1638.6735630485543, 103.50077790754942], [1644.2168949520724, 102.52500775914766], [1754.2999121728851, 97.17805174620413], [1770.779686401861, 117.79236877888135]]

    data=shape_from_geo(geo, data)
    print(data)