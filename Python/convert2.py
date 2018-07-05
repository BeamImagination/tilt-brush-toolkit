#!/usr/bin/env python

from tiltbrush import tilt;
import json;
import base64;
from pprint import pprint;
import struct;

from tiltbrush_fbx import *;

sketch_name = "Untitled_1";

json_data = json.loads(open(sketch_name + '.json').read());
tilt_data = tilt.Tilt(sketch_name + '.tilt');

def addModelInfoFBX(node):
    node.setType('Model');
    node.addChild(FBXNode('Version', '232'));
    node.addChild(FBXNode('MultiLayer', '0'));
    node.addChild(FBXNode('MultiTake', '0'));
    node.addChild(FBXNode('Shading', 'Y'));
    node.addChild(FBXNode('Culling', '\"CullingOff\"'));
    node.addChild(FBXNode('GeometryVersion', '124'));

#format = "fbx" or "obj"
def export(format):
    assert(format == "obj" or format == "fbx");
    
    f = None;
    
    # if the format is obj then we just continuously write to the file
    # otherwise we wait until the end to write out the fbx file
    if format == 'obj':
        f = open('output.obj', 'w');
    
    # node list for fbx export
    obj_node = None;
    connections_node = None;
    node_list = [];
    if format == 'fbx':
        node_list.append(generateHeader());
        obj_node = FBXNode('Objects');
        connections_node = FBXNode('Connections');
    
    # since vertices are defined globally for .obj we have to keep track of the offset
    vert_offset = 0;

    for strokenum, stroke in enumerate(json_data["strokes"]):
        Model = None;
        if format == "obj":
            f.write("o stroke_" + str(strokenum) + '\n');
            f.write("g " + str(strokenum) + '\n');
        else:
            modelname = '\"Model::Stroke' + str(strokenum) + '\"';
            Model = FBXNode('Model', modelname + ', \"Mesh\"');
            addModelInfoFBX(Model);
            obj_node.addChild(Model);
            connections_node.addChild(FBXNode('Connect', '\"OO\", ' + modelname + ', \"Model::Scene\"'));
            
        vert_data = base64.b64decode(stroke["v"]);
        color_data = base64.b64decode(stroke["c"]);
        tri_data = base64.b64decode(stroke["tri"]);
        nrm_data = base64.b64decode(stroke["n"]);
        
        color_list = [];
        vert_list = [];
        tri_list = [];
        nrm_list = [];
        
        # this starts at 1 for .obj
        tri_offsetted = [];
        
        # read in the colors as 4 byte RGBA
        for i in range(len(color_data) // 4):
            color_list.append(map(lambda x: x/255.0, struct.unpack('BBBB', color_data[i*4:i*4 + 4])));
        
        # read in the binary data to vert_list
        for i in range(len(vert_data) // 12):
            vert_list.append(struct.unpack('fff', vert_data[i*12:i*12 + 12]));
            
        # read in the binary data to tri_list
        for i in range(len(tri_data) // 12):
            tri_list.append(struct.unpack('iii', tri_data[i*12:i*12 + 12]));
            
        # read in the binary data to vert_list
        for i in range(len(nrm_data) // 12):
            nrm_list.append(struct.unpack('fff', nrm_data[i*12:i*12 + 12]));

        # vertex list
        if format == "obj":
            # the obj format is v x y z r g b a
            for i, xyz in enumerate(vert_list):
                f.write('v {0[0]} {0[1]} {0[2]}'.format(xyz));
                f.write(' {0[0]} {0[1]} {0[2]}'.format(color_list[i]));
                cp_index = min(i // 2, len(tilt_data.sketch.strokes[strokenum].controlpoints) - 1);
                if (i // 2) > cp_index:
                    print("error!!!!! i: " + str(i // 2) + " and cp_index:" + str(cp_index));
                f.write(' {}.0 \n'.format(tilt_data.sketch.strokes[strokenum].controlpoints[cp_index].extension[1])); # time in alpha
            f.write('s 1' + '\n');
        else:
            vertices_str = "";
            end_index = (len(vert_list) - 1);
            for i, xyz in enumerate(vert_list):
                vertices_str += '{0[0]},{0[1]},{0[2]}'.format(xyz);
                if i < end_index:
                    vertices_str += ',';
            Model.addChild(FBXNode('Vertices', vertices_str));
        
        # tri list
        if format == "obj":
            for tri in tri_list:
                for vert in tri:
                    tri_offsetted.append(vert + 1 + vert_offset);
                f.write('f {0[0]} {0[1]} {0[2]}'.format(tri_offsetted) + '\n');
        else:
            end_index = (len(tri_list) - 1);
            tri_str = "";
            for i, tri in enumerate(tri_list):
                fbx_tri = (tri[0], tri[2], (tri[1] * (- 1)) - 1);
                tri_str += "{0[0]},{0[1]},{0[2]}".format(fbx_tri);
                if i < end_index:
                    tri_str += ','

            Model.addChild(FBXNode('PolygonVertexIndex', tri_str));
        
        # nrm list
        if format == "obj":
            print('Error: no normals in obj export');
        else:
            normal_node = FBXNode('LayerElementNormal', '0');
            normal_node.addChild(FBXNode('Version', '101'));
            normal_node.addChild(FBXNode('Name', '\"\"'));
            normal_node.addChild(FBXNode('MappingInformationType', '\"ByVertex\"'));
            normal_node.addChild(FBXNode('ReferenceInformationType', '\"Direct\"'));
            normal_str = "";
            end_index = (len(nrm_list) - 1);
            for i, xyz in enumerate(nrm_list):
                normal_str += '{0[0]},{0[1]},{0[2]}'.format(xyz);
                if i < end_index:
                    normal_str += ',';
            normal_node.addChild(FBXNode('Normals', normal_str));
            Model.addChild(normal_node);
            
            layer_node = FBXNode('Layer', '0');
            layer_node.addChild(FBXNode('Version', '100'));
            layer_element = FBXNode('LayerElement');
            layer_element.addChild(FBXNode('Type', '\"LayerElementNormal\"'));
            layer_element.addChild(FBXNode('TypedIndex', '0'));
            layer_node.addChild(layer_element);
            Model.addChild(layer_node);
        
        # for obj,the indicies of the verts in the next object are offsetted by the number
        # of verts in this object
        if format == 'obj':
            vert_offset = vert_offset + len(vert_list);
            f.write('\n');
        
    if format == 'fbx':
        global_settings = FBXNode('GlobalSettings').setType('GlobalSettings');
        global_settings.addChild(FBXNode('Version', '1000'));
        properties60 = FBXNode('Properties60');
        properties60.addChild(FBXNode('Property', '\"UpAxis\", \"int\", \"\", 1'));
        properties60.addChild(FBXNode('Property', '\"UpAxisSign\", \"int\", \"\", 1'));
        properties60.addChild(FBXNode('Property', '\"FrontAxis\", \"int\", \"\", 2'));
        properties60.addChild(FBXNode('Property', '\"FrontAxisSign\", \"int\", \"\", 1'));
        properties60.addChild(FBXNode('Property', '\"CoordAxis\", \"int\", \"\", 0'));
        properties60.addChild(FBXNode('Property', '\"CoordAxisSign\", \"int\", \"\", 1'));
        properties60.addChild(FBXNode('Property', '\"UnitScaleFactor\", \"double\", \"\", 1'));
        global_settings.addChild(properties60);
        obj_node.addChild(global_settings);
    
        def_node = FBXNode('Definitions');
        def_node.addChild(FBXNode('Version', '100'));
        def_node.addChild(FBXNode('Count', str(len(obj_node.children))));
        
        num_settings = 0;
        num_models = 0;
        for node in obj_node.children:
            if node.getType() == 'Model':
                num_models += 1;
            elif node.getType() == 'GlobalSettings':
                num_settings += 1;
        
        modelcount_node = FBXNode('ObjectType', '\"Model\"');
        modelcount_node.addChild(FBXNode('Count', str(num_models)));
        
        globalsettings_node = FBXNode('ObjectType', '\"GlobalSettings\"');
        globalsettings_node.addChild(FBXNode('Count', str(num_settings)));
        
        def_node.addChild(modelcount_node);
        def_node.addChild(globalsettings_node);
    
        node_list.append(def_node);
        node_list.append(obj_node);
        node_list.append(connections_node);
    
        f = open('output.fbx', 'w');
        f.write("; FBX 6.1.0 project file\n" +
                "; Copyright (C) 1997-2008 Autodesk Inc. and/or its licensors.\n" +
                "; All rights reserved.\n" +
                "; ----------------------------------------------------\n\n");
        for node in node_list:
            f.write(str(node));
            f.write('\n');
        
    f.close();



export("fbx");
