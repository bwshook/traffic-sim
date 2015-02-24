'''
Created on Mar 7, 2013

@author: bxs003
'''
from math import cos, sin, pi, fabs

from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np

from trafficsim.util import find_pos_from_segments, check_radial_enclosure

class Vehicle(object):
    def __init__(self, preferred_speed, road, start=0.0, length=10.0):
        self.length = length # in feet (vehicle length)
        self.road = road
        self.speed = preferred_speed # miles per hour
        self.prev_speed = 0.0
        self.prev_error = 0.0
        self.integral = 0.0
        self.u = 0.0 # acceleration input
        self.preferred_speed = preferred_speed
        self.medium_speed = 80.0
        self.slow_speed = 40.0
        self.target_speed = preferred_speed
        self.control_count = 0
        self.control_dt = 0.0
        
        self.position = (0.0, 0.0)
        self.orient = None
        self.cur_seg = None # current road segment that vehicle is on
        self.road_dist = start
        
        self.FOV = 45 # degrees
        self.view_dist = 500 # feet
        self.sensors_visible = []
        self.vehicles_visible = []
        
        self.update(0.0)
        
    def update(self, dt):
        if dt > 500.0:
            print 'dt is too large:', dt, 'ms; Reducing dt to zero for the time being.'
            dt = 0.0
                        
        self.update_dynamics(dt)
        self.road_dist += self.speed*(dt/3600.0)
        ret = find_pos_from_segments(self.road_dist, self.road.segments)
        if ret is not None:
            self.position = ret[0]
            self.cur_seg = ret[1]
        else: # if the car is not on the road, return it to the beginning
            self.road_dist = 0.0
            self.cur_seg = self.road.segments[0]
            
        self.check_sight()
        
        self.control_count += 1
        self.control_dt += dt
        if self.control_count > 1:
            self.pi_control(dt)
            self.control_count = 0
            self.control_dt = 0.0
            
    def check_sight(self):
        # find current view orientation based on current segment
        seg_orient_x = self.cur_seg[3][0] - self.cur_seg[2][0]
        seg_orient_y = self.cur_seg[3][1] - self.cur_seg[2][1]
        seg_vec = seg_orient_x + seg_orient_y*1j
        orient = np.angle(seg_vec, deg=True)
        self.orient = orient
        
        self.target_speed = self.preferred_speed
        # Check for sensors
        del self.sensors_visible[:]
        for s in self.road.sensors:
            dist = s.dist - self.road_dist
            if dist < 0.1 and dist > 0.0:
                if s.status == 2:
                    self.target_speed = self.medium_speed
                elif s.status == 3:
                    self.target_speed = self.slow_speed
                     
#            visible = check_radial_enclosure(self.FOV, (self.view_dist/5280.0), self.position, orient, s.position)
#            if visible:
#                self.sensors_visible.append(s)
        
        # Check for vehicles
        for v in self.road.vehicles:
            dist = v.road_dist - self.road_dist
            if dist < 0.1 and dist > 0.0: # select only cars ahead of car
                self.target_speed = v.target_speed
                
        # Check for accidents
        for a in self.road.accidents:
            dist = a.road_dist - self.road_dist
            if dist < a.radius and dist > 0.0:
                self.target_speed = 25.0
                
    def pi_control(self, dt):
        Kp = 1.0
        Ki = 0.8
        Kd = 0.0
        error = self.target_speed - self.speed
        self.integral += error*dt
        deriv = (error - self.prev_error)/dt
        self.u = Kp*error + Ki*self.integral + Kd*deriv
        self.prev_error = error
        
    def update_dynamics(self, dt):
        accel = self.u - 0.1*self.speed
        self.speed += accel*dt
        
    def draw(self):
        glEnable(GL_LIGHTING)
        glPushMatrix()
        glTranslate(self.position[0], 0.0, self.position[1])
        glColor3f(1.0, 1.0, 1.0)
        glutSolidSphere(0.05, 10, 10)
        glDisable(GL_LIGHTING)
        
        glColor3f(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        orient = self.orient*(pi/180)
        x = cos(orient)*(self.view_dist/5280.0)
        y = sin(orient)*(self.view_dist/5280.0)
        glVertex3f(0, 0, 0)
        glVertex3f(x, 0.001, y)
        glEnd()
        glPopMatrix()