'''
Created on Mar 7, 2013

@author: bxs003
'''
from OpenGL.GL import *
from OpenGL.GLUT import *

from trafficsim.util import find_pos_from_segments

class SensorNode(object):
    def __init__(self, dist, road, node_index):
        self.dist = dist
        self.road = road
        self.node_index = node_index
        self.status = 0
        self.position = (0.0, 0.0)
        self.find_pos()
        
        self.sense_dist = 250.0/5280.0
        self.sensing = 0
        self.speed = 0.0
        
        self.off = (0.2, 0.2, 0.2)
        self.green = (0, 1, 0)
        self.yellow = (1, 1, 0)
        self.red = (1, 0, 0)
        self.purple = (0.7, 0, 0.7)
        self.colors = {0: self.green, 1: self.green, 2: self.yellow, \
                       3: self.red, 4: self.purple}
        
        self.rx_msgs = []
        self.rx_hyst = 0
        self.rx_status = 0
        
    def find_pos(self):
        ret = find_pos_from_segments(self.dist, self.road.segments)
        if ret is not None:
            self.position = ret[0]
        else:
            self.position = (0.0, 0.0)
            
    def update(self):
        self.sensing = 0
        self.status = 0
        for v in self.road.vehicles:
            away = self.dist - v.road_dist
            if away < self.sense_dist and away > 0.0:
                self.sensing = 1
                self.speed = v.speed
                break
            
        if self.sensing == 1:
            warning = False
            if self.speed < 50.0:
                warning = True
                self.status = 3
            elif self.speed < 90.0:
                warning = True
                self.status = 2
            if self.node_index-1 >= 0 and warning:
                    self.road.sensors[self.node_index-1].rx_msgs.append(self.status)
            
        # Check msgs from other nodes
        if len(self.rx_msgs) > 0:
            for msg in self.rx_msgs:
                if self.status < msg:
                    self.rx_status = msg
                    self.rx_hyst = 100
            del self.rx_msgs[:]
        
        self.rx_hyst -= 1
        if self.rx_hyst > 0:
            self.status = self.rx_status
        
    def draw(self):
        glEnable(GL_LIGHTING)
        glPushMatrix()
        glColor3fv(self.colors[self.status])
        glTranslate(self.position[0], 0.0, self.position[1])
        glutSolidSphere(0.05, 10, 10)
        glPopMatrix()
        glDisable(GL_LIGHTING)