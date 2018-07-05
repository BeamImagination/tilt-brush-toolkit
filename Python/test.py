#!/usr/bin/env python

from tiltbrush import tilt;
from pprint import pprint;

test = tilt.Tilt('../../TiltBrush/Untitled_0.tilt');

for stroke in test.sketch.strokes:
    for point in stroke.controlpoints:
        pprint(point);
