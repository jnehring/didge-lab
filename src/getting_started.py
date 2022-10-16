from cad.calc.geo import Geo

geo = [[0,32], [800,32], [900,38], [970,42], [1050, 40], [1180, 48], [1350, 60], [1390, 68], [1500, 72]]
geo = Geo(geo)
print(geo.get_cadsd().get_notes())