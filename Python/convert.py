#!/usr/bin/env python3
import json;
import base64;
from pprint import pprint;
import struct;

json_data = json.loads(open("Untitled_0.json").read());

#print(base64.b64decode(json_data["strokes"][0]["v"]))

outstr = "";
data = base64.b64decode(json_data["strokes"][0]["v"]);

# since vertices are defined globally we have to keep track of the offset
vert_offset = 0;

for strokenum, stroke in enumerate(json_data["strokes"]):
    outstr = outstr + "o stroke_" + str(strokenum) + '\n';
    outstr = outstr + "g " + str(strokenum) + '\n';
    vert_data = base64.b64decode(stroke["v"]);
    tri_data = base64.b64decode(stroke["tri"]);

    # read in the binary data to vert_list
    vert_list = []
    for i in range(len(vert_data) // 12):
        vert_list.append(struct.unpack('fff', vert_data[i*12:i*12 + 12]));

    # put the binary data in the output string
    for xyz in vert_list:
        outstr = outstr + 'v {0[0]} {0[1]} {0[2]}'.format(xyz) + '\n';
    outstr = outstr + 's 1' + '\n';

    # read in the binary data to tri_list
    tri_list = []
    for i in range(len(tri_data) // 12):
        tri_list.append(struct.unpack('iii', tri_data[i*12:i*12 + 12]));
    
    # write out the data to the string
    for tri in tri_list:
        tri_offsetted = [];
        for vert in tri:
            tri_offsetted.append(vert + 1 + vert_offset);
        outstr = outstr + 'f {0[0]} {0[1]} {0[2]}'.format(tri_offsetted) + '\n';

    # the indicies of the verts in the next object are offsetted by the number
    # of verts in this object
    vert_offset = vert_offset + len(vert_list);
    outstr = outstr + '\n';

    # this is test shit
    time_data = base64.b64decode(stroke["t"]);
    time_list = [];
    for i in range(len(time_data) // 4):
        time_list.append(struct.unpack('f', time_data[i*4:i*4 + 4]));

    for time in time_list:
        print(time);

f = open('output.obj', 'w');
f.write(outstr);
f.close();
