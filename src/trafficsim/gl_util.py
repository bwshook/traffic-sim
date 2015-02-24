'''
Created on Mar 7, 2013

@author: bxs003
'''
from OpenGL.GLUT import *

def draw_text(text):
    for c in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, c)