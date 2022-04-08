import math
import numpy as np
import sys
import json

is_logging=False

def log(*x):
    if is_logging:
        print(x)

def vertex_circle(segments, z, r):
    """ Return a ring of vertices """
    verts = []

    for i in range(segments):
        angle = (math.pi*2) * i / segments
        verts.append((r*math.cos(angle), r*math.sin(angle), z))

    return verts

def shape_from_geo(geo, data, n_circle_segments):
    
    # create first ring
    offset_last_circle_vert=len(data["verts"])
    this_ring_edge_start=len(data["edges"])
    last_ring_edge_start=len(data["edges"])
    
    z=geo[0][0]/1000
    r=0.5*geo[0][1]/1000
    # make first ring
    circle0=vertex_circle(n_circle_segments, z, r)
    
    log("first ring vertices")
    for i in range(len(circle0)):
        log("add vert", len(data["verts"]), circle0[i])
        
    #log("circle0", len(data["verts"]), circle0)
        data["verts"].append(circle0[i])
    
    log("first ring horizontal edges")
    for i in range(n_circle_segments):
        next=i+1
        if i==n_circle_segments-1:
            next=0
        edge=(i+offset_last_circle_vert, next+offset_last_circle_vert)
        log("add edge", len(data["edges"]), edge)
        data["edges"].append(edge)

    for g in geo[1:]:

        z=g[0]/1000
        r=0.5*g[1]/1000
        
        # ring
        circle1=vertex_circle(n_circle_segments, z, r)
        
        vert_start=len(data["verts"])
        for i in range(len(circle1)):
            log("add vert", len(data["verts"]), circle1[i])
            data["verts"].append(circle1[i])
        
            
        
        this_ring_edge_start=len(data["edges"])
        
        log("horizontal edges")
        for i in range(n_circle_segments):
            next=vert_start+i+1
            if i==n_circle_segments-1:
                next=vert_start
            edge=(vert_start+i, next)
            data["edges"].append(edge)
            log("add edge", len(data["edges"]), edge)

        vert_edge_start=len(data["edges"])
        # make vertical edges
        
        log("add vertical edges")
        for i in range(n_circle_segments):
            edge=(vert_start+i, offset_last_circle_vert+i)
            log("add edge", len(data["edges"]), edge)
            data["edges"].append(edge)
            e1=data["edges"][this_ring_edge_start+i] # top edge
            e2=data["edges"][last_ring_edge_start+i] # bottom edge

            face=(e1[0],e1[1],e2[1],e2[0])
            log("add face", len(data["faces"]), face)
            data["faces"].append(face)
            
                    
        last_ring_edge_start=this_ring_edge_start
        offset_last_circle_vert=vert_start

    return data

def connect_ends(data, start_vertex_inner, start_vertex_outer, start_edge_inner, start_edge_outer, n_circle_segments, last_inner_vertex, last_outer_vertex):
    
    log("last outer vertex", last_outer_vertex)
    for end in range(2):
        log("connect end " + str(end))
        edge_start=len(data["edges"])
        if end==1:
            start_vertex_inner=last_inner_vertex-n_circle_segments
            start_vertex_outer=last_outer_vertex-n_circle_segments
            
        for i in range(0, n_circle_segments):
            edge=(i+start_vertex_inner, i+start_vertex_outer)
            log("add edge", len(data["edges"]), edge)
            data["edges"].append(edge)
            
        for i in range(n_circle_segments):
            e1=data["edges"][edge_start+i]
            e2=None
            if i==n_circle_segments-1:
                e2=data["edges"][edge_start]
            else:
                e2=data["edges"][edge_start+i+1]
            face=(e1[0],e1[1], e2[1],e2[0])
            log("add face", len(data["faces"]), face)
            data["faces"].append(face)
    
    return data
