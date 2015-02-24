'''
Created on Jan 20, 2013

@author: shook
'''

import os
from math import sqrt, pow, sin, cos, pi
from random import uniform, seed

import numpy as np
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.extensions import *

from trafficsim.camera import Camera
from traffic.road import Road
from traffic.vehicle import Vehicle
from traffic.sensor import SensorNode 
from traffic.accident import AccidentField

class TrafficSim(object):
    fps = 60
    win_res = (1024, 768)
    
    keys_held = {pygame.K_w: False,
                 pygame.K_a: False,
                 pygame.K_s: False,
                 pygame.K_d: False}
    
    CAM_FREE = 1
    CAM_FPS = 2
    cam_mode = CAM_FREE

    def __init__(self):
        seed(1337)
        self.free_cam = Camera([2.0, 1.0, 2.0])
        self.free_cam.set_rotation(45.0, 100.0)
        
        self.init_window()
        self.init_gl()
        self.resize_gl(self.win_res)
        
        points = [(4.732657104, 0.0), \
                (4.811864754, 0.188118169), \
                (5.049487705, 1.841577869), \
                (5.16829918, 2.148507514), \
                (5.188101093, 3.861372951), \
                (4.782161885, 4.405925546), \
                (4.762359973, 5.049487705), \
                (4.940577186, 5.851465164), \
                (4.910874317, 6.910867486), \
                (4.841567623, 7.2475)]
        
        self.road = Road(points)
        
        for i in xrange(30):
            v1 = Vehicle(uniform(95.0, 140.0), self.road, uniform(0.1, 7.0))
            self.road.vehicles.append(v1)
        
        sep = 0.25
        for i in xrange(int(6.25/sep)):
            n1 = SensorNode(sep*i+0.25, self.road, i)
            self.road.sensors.append(n1)
            
        af = AccidentField(5.0, 0.25, self.road)
        self.road.accidents.append(af)
        
        self.clock = pygame.time.Clock()
        
    def init_window(self):
        glutInit()
        pygame.init()
        self.screen = pygame.display.set_mode(self.win_res, pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
        pygame.display.set_caption('TrafficSim - Press Enter for mouse control of camera')

    def init_gl(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        
        glFrontFace(GL_CW)
        glCullFace(GL_BACK)
        #glEnable(GL_CULL_FACE)
        glShadeModel(GL_SMOOTH)
        
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LIGHT0)
        glLineWidth(2.0)
        
        glEnable(GL_TEXTURE_2D)
        self.map_tex = self.load_image("../../img/540.PNG")[0]
        glDisable(GL_TEXTURE_2D)
        
    def load_image(self, image_path):
        textureSurface = pygame.image.load(image_path)
     
        textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
     
        width = textureSurface.get_width()
        height = textureSurface.get_height()
     
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
        
        if hasGLExtension("GL_EXT_texture_filter_anisotropic"):
            max_aniso = glGetFloat(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, max_aniso)
        else:
            print 'Anisotropic filtering not supported.'
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
     
        return tex_id, width, height
        
    def resize_gl(self, res):
        if res[1] == 0:
            res[1] = 1
    
        glViewport(0, 0, res[0], res[1])
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(res[0])/float(res[1]), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
    def update_cam(self):
        delta = self.clock.get_time()*2e-3
        if self.keys_held[pygame.K_w]:
            self.free_cam.move(delta)
        if self.keys_held[pygame.K_s]:
            self.free_cam.move(-delta)
        if self.keys_held[pygame.K_d]:
            self.free_cam.strafe(-delta)
        if self.keys_held[pygame.K_a]:
            self.free_cam.strafe(delta)
            
        self.free_cam.update()

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.update_cam()
        
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)
        glColor3f(1, 1, 1)
        self.draw_textured_quad(7.2475, 7.2475, self.map_tex)
        glEnable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        
        dt = self.clock.get_time()*0.001
        self.road.update(dt)
        self.draw_axes()
        self.road.draw()
        
        pygame.display.flip()
        
    def draw_axes(self, size=1.0):
        glColor3f(1, 1, 0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(size, 0, 0)
        
        glVertex3f(0, 0, 0)
        glVertex3f(0, size, 0)
        
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, size)
        glEnd()
        
    def draw_textured_quad(self, w, h, tex_id, repeat=1.0):
        glBindTexture(GL_TEXTURE_2D, tex_id)
        
        aspect = w/h
        glBegin(GL_TRIANGLES)
        glNormal3f(0.0, 1.0, 0.0)
        glTexCoord2f(repeat*aspect, 0.0); glVertex3f(0.0, 0.0, 0.0);
        glTexCoord2f(0.0, 0.0); glVertex3f(w, 0.0, 0.0);
        glTexCoord2f(0.0, repeat); glVertex3f(w, 0.0, h);
        
        glTexCoord2f(repeat*aspect, 0.0); glVertex3f(0.0, 0.0, 0.0);
        glTexCoord2f(0.0, repeat); glVertex3f(w, 0.0, h);
        glTexCoord2f(repeat*aspect, repeat); glVertex3f(0.0, 0.0, h);
        glEnd()
        
    def _key_down(self, key):
        self._check_keys_held(key, True)
        if (key == pygame.K_ESCAPE):
            self._running = False
        elif (key == pygame.K_RETURN):
            if self.cam_mode == self.CAM_FREE:
                self.cam_mode = self.CAM_FPS
                pygame.mouse.set_visible(False)
            else:
                self.cam_mode = self.CAM_FREE
                pygame.mouse.set_visible(True)

    def _key_up(self, key):
        self._check_keys_held(key, False)
            
    def _check_keys_held(self, key, key_down):
        if key_down:
            if key in self.keys_held:
                self.keys_held[key] = True
        else: # Key Up
            if key in self.keys_held:
                self.keys_held[key] = False
                
    def _mouse_move(self, pos):
        if self.cam_mode == self.CAM_FPS:
            hw = self.screen.get_width()>>1
            hh = self.screen.get_height()>>1
            dx = 0.05*(pos[0]-hw)
            dy = 0.05*(pos[1]-hh)
            self.free_cam.mouse_rotate(dx, dy)
            pygame.mouse.set_pos([hw, hh])

    def doEvents(self):
        events = pygame.event.get()
        
        for e in events:
            if (e.type == pygame.QUIT):
                self._running = False
            elif (e.type == pygame.KEYDOWN):
                self._key_down(e.key)
            elif (e.type == pygame.KEYUP):
                self._key_up(e.key)
            elif (e.type == pygame.VIDEORESIZE):
                self.resize_gl(e.size)
            elif (e.type == pygame.MOUSEMOTION):
                self._mouse_move(e.pos)

    def run(self):
        self._running = True
        
        while self._running:
            self.clock.tick(self.fps)
            self.doEvents()
            self.render()
            pygame.display.set_caption(str(self.free_cam.pos)+' '+str(self.free_cam.rot))
    
if __name__ == '__main__':
    tsim = TrafficSim()
    tsim.run()
