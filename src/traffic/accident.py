'''
Created on Mar 19, 2013

@author: shook
'''
from time import time
from math import sin

from OpenGL.GL import *
from OpenGL.GLUT import *

from trafficsim.util import find_pos_from_segments

class AccidentField(object):
    def __init__(self, road_dist, radius, road):
        self.road_dist = road_dist
        self.radius = radius
        ret = find_pos_from_segments(self.road_dist, road.segments)
        self.position = ret[0]
        
    def draw(self):
        glColor4f(1.0, 0.0, 0.0, 0.5*sin(5.0*time())+0.7)
        glPushMatrix()
        glTranslatef(self.position[0], 0.0, self.position[1])
        glRotatef(90.0, 1.0, 0.0, 0.0)
        glutSolidTorus(self.radius*0.08, self.radius, 10, 14)
        glPopMatrix()