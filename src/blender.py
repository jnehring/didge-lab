# export a didge-lab geometry to blender

import bpy
import bmesh
import math

def object_from_data(data, name, scene, select=True):
    """ Create a mesh object and link it to a scene """

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(data['verts'], data['edges'], data['faces'])

    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)

    bpy.context.view_layer.objects.active = obj


    mesh.validate(verbose=True)

    return obj

def vertex_circle(segments, z, r):
    """ Return a ring of vertices """
    verts = []

    for i in range(segments):
        angle = (math.pi*2) * i / segments
        verts.append((r*math.cos(angle), r*math.sin(angle), z))

    return verts

def make_circle(name, z, r):
    """ Make a circle """
    segments=64
    data = {
            'verts': vertex_circle(segments, z, r),
            'edges': [],
            'faces': [],
           }

    data['edges'] = [(i, i+1) for i in range(segments)]
    data['edges'].append((segments - 1, 0))

    scene = bpy.context.scene
    return object_from_data(data, name, scene)

geo=[[0.0, 32], [817.0486047169525, 41.5999785334556], [851.7075445084539, 50.43152161722423], [931.4996024285304, 45.41110329840837], [1014.5223467577993, 53.52519750042781], [1114.7672422285755, 72.21773641073615], [1182.1075440839359, 74.7025967800953], [1270.4413573179793, 69.67119255962623], [1316.3371428089783, 65.68281795212081], [1399.9104688320197, 63.18868459398395], [1474.510513323225, 71.62681059877697], [1551.755981833699, 67.42247481186227], [1636.2083754379262, 93.07377036427401], [1672.751835912501, 120.28807158687461], [1768.0572546509482, 131.36718426322713], [1852.4637445091807, 182.36337961101106], [2009.9999999999998, 275.21370431262454]]
for g in geo:
    z=g[0]/1000
    r=0.5*g[1]/1000
    make_circle('segment', z,r)