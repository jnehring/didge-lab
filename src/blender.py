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

geo=[[0, 28.420336012204675], [149.66252222332295, 33.76465931705686], [190.9290008000925, 37.136787546663314], [244.89950634656705, 40.235970850002836], [267.197109496854, 38.933665356976064], [276.9460374941963, 46.35490419076429], [287.84265643219896, 44.88838723923583], [289.894285469773, 50.927491383239754], [360.34369757772356, 48.669218753653475], [396.43370498059744, 46.806285867103355], [409.32143938082766, 41.274723636350856], [423.9985789846164, 35.01575339833586], [424.2811264061683, 37.279304221141594], [729.2632190020428, 49.46070797554034], [740.7038677244886, 51.96537438783191], [789.8098078211553, 56.37809305432246], [824.832633647184, 68.36355645709236], [844.2682043448712, 69.9719439562858], [887.6988218643637, 79.85741511381877], [939.3293995392683, 81.89786666925995], [958.5489269061865, 87.32771823229093], [977.427370589506, 81.03551120758384], [1024.954074923267, 67.89104152354093], [1027.923756304213, 82.27533977143929], [1028.4748918559312, 76.57047829191704], [1127.6598143038887, 70.19686612077433], [1333.563045949629, 71.31491552502824], [1375.2296925866858, 77.86762899198946], [1403.6584342204371, 82.81687154371089], [1423.0422543288637, 118.44355573277267], [1479.5891859178114, 119.30317881758904], [1517.9732378535984, 112.77543303612462], [1527.960064860913, 122.46832243080033], [1536.747557302574, 123.99468289941827], [1563.03926027132, 92.49862077431649], [1610.0212281675192, 97.96890202699274], [1625.7259664897474, 91.33665691698417], [1683.1368964170545, 100.56678436539872], [1707.7801903787224, 131.42380178924867], [1766.8454291022174, 125.98025384544576]]


data = {
        'verts': [],
        'edges': [],
        'faces': [],
}

n_circle_segments=64
z=geo[0][0]/1000
r=0.5*geo[0][1]/1000

circle0=vertex_circle(n_circle_segments, z, r)
data["verts"].extend(circle0)
for i in range(n_circle_segments):
    data["edges"].append((i, i+1))
data["edges"].append((n_circle_segments-1, 0))

offset_last_circle=0
for g in geo[1:]:

    z=g[0]/1000
    r=0.5*g[1]/1000
    
    circle1=vertex_circle(n_circle_segments, z, r)

    vert_start=len(data["verts"])
    data["verts"].extend(circle1)
    
    for i in range(n_circle_segments):
        data["edges"].append((vert_start+i, vert_start+i+1))
        data["edges"].append((vert_start+i, offset_last_circle+i))
    data["edges"].append((vert_start, vert_start+n_circle_segments-1))
    offset_last_circle=vert_start
        
scene = bpy.context.scene

object_from_data(data, "didge", scene)