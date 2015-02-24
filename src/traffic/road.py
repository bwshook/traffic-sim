'''
Created on Mar 7, 2013

@author: bxs003
'''
from math import sqrt

from OpenGL.GL import *

class Road(object):
    def __init__(self, points):
        self.points = points # units in miles
        self.segments = []
        self.make_segments()
        
        self.vehicles = []
        self.sensors = []
        self.accidents = []
        
    def make_segments(self):
        prev_pt = None
        dist = 0.0
        prev_dist = 0.0
        for pt in self.points:
            if prev_pt is not None:
                dx = pt[0] - prev_pt[0]
                dy = pt[1] - prev_pt[1]
                dist += sqrt(pow(dx, 2) + pow(dy, 2))
                self.segments.append((prev_dist, dist, prev_pt, pt))
                prev_dist = dist
            prev_pt = pt
        
    def draw(self):
        # Draw the road line segments
        glColor3f(1, 1, 1)
        glBegin(GL_LINES)
        prev_pt = None
        for pt in self.points:
            if prev_pt is not None:
                glVertex3f(prev_pt[0], 0, prev_pt[1])
                glVertex3f(pt[0], 0, pt[1])
            prev_pt = pt
        glEnd()
        
        # Draw vehicles and sensors
        for v in self.vehicles: v.draw()
        for s in self.sensors: s.draw()
        for a in self.accidents: a.draw()
        
    def update(self, dt):
        # Update vehicles and sensors
        for v in self.vehicles: v.update(dt)
        for s in self.sensors: s.update()