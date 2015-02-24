'''
Created on Jan 25, 2013

@author: shook
'''

import math
import numpy
from OpenGL.GLU import gluLookAt

from transformations import vector_product, rotation_matrix, unit_vector

class Camera(object):
    def __init__(self, pos=[0.0, 0.0, 0.0]):
        self.pos = pos # absolute position of camera
        self.ref = [0.0, 0.0, -1.0] # relative to camera position (always origin based)
        self.rot = [-90.0, 90.0]
        
    def mouse_rotate(self, dx, dy):
        self.rot[0] += dx
        self.rot[1] += dy
        
        if self.rot[1] > 179.9:
            self.rot[1] = 179.9
        elif self.rot[1] < 0.1:
            self.rot[1] = 0.1
        
        theta = self.rot[0]*(math.pi/180) # azimuth
        phi = self.rot[1]*(math.pi/180) # inclination
            
        self.ref[0] = math.sin(phi)*math.cos(theta)
        self.ref[1] = math.cos(phi)
        self.ref[2] = math.sin(phi)*math.sin(theta)
        
    def set_rotation(self, theta, phi):
        self.rot[0] = theta
        self.rot[1] = phi
        theta = self.rot[0]*(math.pi/180) # azimuth
        phi = self.rot[1]*(math.pi/180) # inclination
            
        self.ref[0] = math.sin(phi)*math.cos(theta)
        self.ref[1] = math.cos(phi)
        self.ref[2] = math.sin(phi)*math.sin(theta)
            
    def rotate(self, angle, axis):
        # Axis angle rotation of camera
        angle = angle*(math.pi/180)
        rotmat = rotation_matrix(angle, axis)
        self.ref = numpy.dot(rotmat[:3, :3], self.ref)
    
    def translate(self, dx, dy, dz):
        # Absolute translation of camera postion
        self.pos = [self.pos[0]+dx, self.pos[1]+dy, self.pos[2]+dz]
    
    def move(self, ds):
        # Move camera position along reference vector
        # Norm the ref vector
        x = self.pos[0] + self.ref[0]*ds
        y = self.pos[1] + self.ref[1]*ds
        z = self.pos[2] + self.ref[2]*ds
        self.pos = [x, y, z]
        
    def strafe(self, ds):
        strafe_vec = vector_product([0,1,0], self.ref)
        strafe_vec = unit_vector(strafe_vec)
        x = self.pos[0] + strafe_vec[0]*ds
        y = self.pos[1] + strafe_vec[1]*ds
        z = self.pos[2] + strafe_vec[2]*ds
        self.pos = [x, y, z]
        
    def update(self):
        # Set matrix via gluLookAt
        # Build reference point vector (absolute coords)
        rx = self.pos[0] + self.ref[0]
        ry = self.pos[1] + self.ref[1]
        rz = self.pos[2] + self.ref[2]
            
        # cam_pos, ref_pt, up_vec
        gluLookAt(self.pos[0], self.pos[1], self.pos[2], rx, ry, rz, 0.0, 1.0, 0.0)
        
if __name__=='__main__':
    vec = [1,0,0]
    axis = [0,0,1]
    angle = 45*(math.pi/180)
    rotmat = rotation_matrix(angle, axis)
    vec = numpy.dot(rotmat[:3, :3], vec)
    print vec
    vec = numpy.dot(rotmat[:3, :3], vec)
    print vec