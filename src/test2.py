import math
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy.interpolate import make_interp_spline, BSpline
from scipy import interpolate

geo=[[0, 32], [119.9958769849766, 33.60786924930998], [182.96338939932383, 37.43993858124537], [229.31303306092116, 37.65868840095003], [243.87150359250768, 44.24922301095391], [248.22661301651374, 44.66872200645895], [273.35700590490666, 45.427288404108324], [325.1833660559223, 45.10078689004896], [326.6977955401382, 38.56326921940415], [331.3271419201785, 39.24648289540542], [348.80183650206857, 43.44272291801225], [430.9911964176373, 36.58658612297562], [467.1100014503583, 38.75489455260514], [656.2303357738663, 43.14580720660788], [674.7045855405672, 42.09763460759996], [788.1166743193038, 45.731774426101126], [800.7700549159376, 48.91416216097986], [874.3223026858111, 57.48849785851295], [894.4633095356007, 57.85511636112676], [920.7665646046486, 62.810078863961245], [924.8861710152711, 60.406541693482154], [965.9223894013795, 52.92986907805038], [993.5297817069403, 47.8899396101002], [1019.7355557222457, 45.38388648475607], [1053.7014100144995, 51.906767868800614], [1056.08323493601, 51.31169232421349], [1167.4257484469804, 61.68647957633659], [1246.3874724224754, 65.64353932959351], [1319.8878127066603, 83.97728075004777], [1349.4583898219896, 115.89351882544594], [1380.2817590427794, 114.68014975992207], [1413.7176032103646, 94.53429022929657], [1469.3136630077106, 124.90807502454308], [1509.405056810938, 137.6973360550101], [1522.1553223428134, 131.80498827396133], [1577.9706393666918, 117.21227761742348], [1583.3482983545491, 93.28860915227246], [1638.6735630485543, 103.50077790754942], [1644.2168949520724, 102.52500775914766], [1754.2999121728851, 97.17805174620413], [1770.779686401861, 117.79236877888135]]

#geo=[[0,32], [10,32], [50, 50]]

def diameter_at_x(geo, x):

    if x==0:
        return geo.geo[0][1]

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

def smooth_geo(geo):

    def get_w(g0, g1):
        return math.atan((g1[1]-g0[1])/(g1[0]-g0[0]))

    new_geo=[]

    last_w=get_w(geo[0], geo[1])

    segment_size=3
    wall_thickness=5
    max_diff=1
    window_size=100
    thinness_factor=0.2

    p=geo[0]
    ws=[]
    new_geo.append(p)
    newx=np.arange(segment_size, geo[-1][0], segment_size)
    for x in newx:
        d_geo=diameter_at_x(geo, x)
        w=get_w(p, [x, d_geo])
        ws.append(w)

    for i in range(len(ws)-window_size):
        ws[i]=sum([x for x in ws[i:i+window_size]]) / window_size

    for i in range(len(newx)):
        x=newx[i]
        w=ws[i]
        y=p[1] + segment_size*math.tan(w)
        d_geo=diameter_at_x(geo, x)

        if y>d_geo+wall_thickness*thinness_factor:
            y-=wall_thickness*thinness_factor
        if y<d_geo:
           y=d_geo
        p=[x,y]
        new_geo.append(p)

    new_geo=[[x[0], x[1]+wall_thickness] for x in new_geo]
    return new_geo

def df_from_geo(geo, series_name):
    df=[]
    for g in geo:
        df.append([g[0], g[1], series_name])
    df=pd.DataFrame(df, columns=["x", "r", "series"])
    #df["y"]+=200
    return df

df1=df_from_geo(geo, "0")
s_geo=smooth_geo(geo)
df2=df_from_geo(s_geo, "1")

print(s_geo)
df=pd.concat([df1, df2], ignore_index=True)

if False:
    ax=sns.lineplot(data=df, x="x", y="r", hue="series")
    #ax=sns.lineplot(data=df, x="x", y="r")
    plt.xlim(0, 1800)
    plt.ylim(0, 1800)
    plt.show()