#!/usr/bin/env python

from tiltbrush import tilt;
import json;
import base64;
from pprint import pprint;
import struct;

sketch_name = "Untitled_1";

json_data = json.loads(open(sketch_name + '.json').read());
tilt_data = tilt.Tilt(sketch_name + '.tilt');
outstr = "";

# since vertices are defined globally we have to keep track of the offset
vert_offset = 0;

for strokenum, stroke in enumerate(json_data["strokes"]):
    outstr = outstr + "o stroke_" + str(strokenum) + '\n';
    outstr = outstr + "g " + str(strokenum) + '\n';
    vert_data = base64.b64decode(stroke["v"]);
    color_data = base64.b64decode(stroke["c"]);
    tri_data = base64.b64decode(stroke["tri"]);
    
    # read in the colors as 4 byte RGBA
    color_list = [];
    for i in range(len(color_data) // 4):
        color_list.append(map(lambda x: x/255.0, struct.unpack('BBBB', color_data[i*4:i*4 + 4])));
    
    # read in the binary data to vert_list
    vert_list = [];
    for i in range(len(vert_data) // 12):
        vert_list.append(struct.unpack('fff', vert_data[i*12:i*12 + 12]));

    # put the binary data in the output string
    for i, xyz in enumerate(vert_list):
        #pprint(tilt_data.sketch.strokes[strokenum].controlpoints[i // 2].extension[1]);
        #pprint(vars(tilt_data.sketch.strokes[strokenum].controlpoints[i // 2]));
        #break;
        outstr = outstr + 'v {0[0]} {0[1]} {0[2]}'.format(xyz);
        outstr = outstr + ' {0[0]} {0[1]} {0[2]}'.format(color_list[i]);
        cp_index = min(i // 2, len(tilt_data.sketch.strokes[strokenum].controlpoints) - 1);
        if (i // 2) > cp_index:
            print("error!!!!! i: " + str(i // 2) + " and cp_index:" + str(cp_index));
        outstr = outstr + ' {}.0 \n'.format(tilt_data.sketch.strokes[strokenum].controlpoints[cp_index].extension[1]); # time in alpha
        #print(outstr);
        #break;
    outstr = outstr + 's 1' + '\n';

    # read in the binary data to tri_list
    tri_list = [];
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
    
    #pprint(strokenum);
    #pprint(tilt_data.sketch.strokes[strokenum]);
    #pprint(len(tilt_data.sketch.strokes));
    #pprint(strokenum);
    #if strokenum % 2 == 0:
    #    pprint("sketch len:" + str(len(tilt_data.sketch.strokes[strokenum // 2].controlpoints)));
    #pprint("json len:" + str(len(vert_list)));

#pprint(len(tilt_data.sketch.strokes))
#pprint(len(json_data["strokes"]))

#for i in range(len(tilt_data.sketch.strokes)):
#    pprint(json_data["strokes"][i]);
    
f = open('output.obj', 'w');
f.write(outstr);
f.close();
