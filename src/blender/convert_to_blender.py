# export a didge-lab geometry to blender

# import bpy
import math
import numpy as np
import sys
import json
from rtree import index
import pickle
from copy import deepcopy
import os
import vektor

from blender_didge_shape import shape_from_geo, connect_ends, log, vertex_circle, init_data

import argparse

def create_vert_index(verts):
    create_index=False

    if create_index:
        files=["3d_index.data", "3d_index.index"]
        for f in files:
            if os.path.exists(f):
                os.remove(f)

    p = index.Property()    
    p.dimension = 3
    p.dat_extension = 'data'
    p.idx_extension = 'index'
    p.interleaved = False
    idx = index.Index("3d_index", properties=p)

    if create_index or not os.path.exists("3d_index.data"):

        for i in range(len(verts)):
            idx.insert(i, verts[i])

    return idx

def muster(data, start_vertex_outer, last_vertex_outer, n_circle_segments):
    
    idx=create_vert_index(data["verts"][start_vertex_outer:last_vertex_outer])
    start_angle=0
    einmal_rum_z=0.01 # 10 centimeter
    hoehe=0.001 # 1 centimeter
    
    start_z=data["verts"][start_vertex_outer+0][2]
    end_z=data["verts"][last_vertex_outer-1][2]   
    
    def make_line_pattern(height, offset=0, rotation_height=0):
        print(height, offset, rotation_height)
        pattern=[]
        i_ring=start_vertex_outer

        last_z=0
        while i_ring<last_vertex_outer:
            shift=offset
            shift=math.ceil(shift)%n_circle_segments

            if rotation_height>0:
                rotation=(last_z%rotation_height)/rotation_height
                rotation=math.ceil(n_circle_segments*rotation)
                print(rotation)
                shift+=rotation
                               

            # move away from center
            v=data["verts"][i_ring+shift]
            l=vektor.length(v)

            new_pattern_point=vektor.mult_skalar(v, (l+height)/l)

            pattern.append(new_pattern_point)

            last_z=data["verts"][i_ring][2]
            i_ring+=n_circle_segments

            if last_z>rotation_height:
                break


        return pattern
    
    pattern=[]
    height=0.002
    rotation_height=0.2

    # n_rings=4
    # for i in range(n_rings):
    #     pattern.extend(make_line_pattern(height, offset=i*n_circle_segments/n_rings, rotation_height=rotation_height))
    
    # attract segments to pattern
    gravity=10/1000 # 50mm

    def gravitate_point(v_origin, v_destination, gravity):
        dist=vektor.distance(v_origin, v_destination)
        diff=(
            v_destination[0]-v_origin[0],
            v_destination[1]-v_origin[1],
            v_destination[2]-v_origin[2]
        )

        dist_square=dist*dist
        if dist_square==0:
            dist_square=pow(2,-20)
        g = min(1, pow(2,-15)/(dist_square))

        v_new=(
            v_origin[0]+diff[0]*g,
            v_origin[1]+diff[1]*g,
            v_origin[2]+diff[2]*g,
        )
        return v_new

    for i in range(len(pattern)):
        p=pattern[i]
        
        coords=[
            p[0]-gravity,p[1]-gravity,p[2]-gravity,
            p[0]+gravity,p[1]+gravity,p[2]+gravity,
        ]
        
        neighbours=list(idx.intersection(coords, objects=True))

        if len(neighbours)>0:
            distances=[vektor.distance(data["verts"][n.id], p) for n in neighbours]
            nearest_neighbour=neighbours[np.argmin(distances)].id
            data["verts"][nearest_neighbour]=gravitate_point(data["verts"][nearest_neighbour], p, gravity)

    # for vert_id in relocations.keys():
    #     rs=relocations[vert_id]
    #     new_pos=rs[np.argmin(x[1] for x in rs)][0]
    #     data["verts"][vert_id]=new_pos
    # make vertizes out of pattern for debugging
    add_pattern_to_mesh=False

    if add_pattern_to_mesh:
        for p in pattern:
            kantenlaenge=0.001

            vert_start=len(data["verts"])
            data["verts"].extend([
                (p[0]-kantenlaenge, p[1]-kantenlaenge, p[2]-kantenlaenge),
                (p[0]+kantenlaenge, p[1]-kantenlaenge, p[2]-kantenlaenge),
                (p[0]-kantenlaenge, p[1]+kantenlaenge, p[2]-kantenlaenge),
                (p[0]+kantenlaenge, p[1]+kantenlaenge, p[2]-kantenlaenge),
                (p[0]-kantenlaenge, p[1]-kantenlaenge, p[2]+kantenlaenge),
                (p[0]+kantenlaenge, p[1]-kantenlaenge, p[2]+kantenlaenge),
                (p[0]-kantenlaenge, p[1]+kantenlaenge, p[2]+kantenlaenge),
                (p[0]+kantenlaenge, p[1]+kantenlaenge, p[2]+kantenlaenge)
            ])
            edge_start=len(data["edges"])

            data["edges"].extend([
                (vert_start, vert_start+1),
                (vert_start, vert_start+2),
                (vert_start+2, vert_start+3),
                (vert_start+3, vert_start+1),
                
                (vert_start+4, vert_start+5),
                (vert_start+4, vert_start+6),
                (vert_start+6, vert_start+7),
                (vert_start+7, vert_start+5),
                
                (vert_start, vert_start+4),
                (vert_start+1, vert_start+5),
                (vert_start+2, vert_start+6),
                (vert_start+3, vert_start+7),
            ])

    return data

def convert_to_blender(infile, outfile, inner_only=False):
    f=open(infile, "r")
    data=json.load(f)
    f.close()
    n_circle_segments=64

    if inner_only:
        inner_shape=data["inner"]

        log("inner shape")

        count=0
        meshes=[]
        for g in inner_shape:
            data=init_data()
            offset_last_circle_vert=len(data["verts"])
            x=g[0]/1000
            y=0.5*g[1]/1000
            verts=vertex_circle(n_circle_segments, x,y)
            data["verts"].extend(verts)

            for i in range(n_circle_segments):
                next=i+1
                if i==n_circle_segments-1:
                    next=0
                edge=(i+offset_last_circle_vert, next+offset_last_circle_vert)
                log("add edge", len(data["edges"]), edge)
                data["edges"].append(edge)
            meshes.append({
                "name": f"segment{count}",
                "data": data
            })
            count+=1


        # #data_inner_shape=shape_from_geo(inner_shape, data, n_circle_segments)
        # meshes=[{
        #     "name": "inner_shape",
        #     "data": data
        # }]
        f=open(outfile, "w")
        f.write(json.dumps(meshes))
        f.close()

    else:
        inner_shape=data["inner"]
        outer_shape=data["outer"]

        data=init_data()

        start_vertex_outer=len(data["verts"])
        start_edge_outer=len(data["edges"])
        log("outer shape")
        data_outer_shape=shape_from_geo(outer_shape, data, n_circle_segments)
        
        meshes=[{
            "name": "outer_shape",
            "data": data_outer_shape
        }]
        
        data=init_data()

        log("inner shape")

        data_inner_shape=shape_from_geo(inner_shape, data, n_circle_segments)
        meshes.append({
            "name": "inner_shape",
            "data": data
        })

        last_inner_vertex=len(data["verts"])

        log("connect ends")
        data_ends=connect_ends(data_inner_shape, data_outer_shape, n_circle_segments)
        meshes.append({
            "name": "ends",
            "data": data_ends
        })

        f=open(outfile, "w")
        f.write(json.dumps(meshes))
        f.close()

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Convert didgelab geometry to blender import.')
    parser.add_argument('-infile', type=str, required=True)

