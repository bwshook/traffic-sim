'''
Created on Mar 7, 2013

@author: bxs003
'''

from math import sqrt
import numpy as np

def find_pos_from_segments(dist, segments):
    ''' Finds a position based on arc distance along a list of segments 
        Keyword Arguments:
        dist - float - total arc dist along segments
        segments - tuple - (beg_arc_dist, end_arc_dist, beg_point, end_point)
    '''
    cur_seg = None
    for seg in segments:
        if dist >= seg[0] and dist <= seg[1]:
            cur_seg = seg
            break
    
    if cur_seg is not None:
        # find how point has traveled on seg
        trav = dist - cur_seg[0]
        # make translation vector
        trans = np.array([cur_seg[3][0]-cur_seg[2][0], cur_seg[3][1]-cur_seg[2][1]])
        trans = trans/np.linalg.norm(trans)
        trans *= trav
        # translate point from beg of cur_seg by trans
        return ((cur_seg[2][0]+trans[0], cur_seg[2][1]+trans[1]), cur_seg)
    else:
        return None
    
def check_radial_enclosure(fov, vdist, pos, orient, pt):
    ''' Check if point is within a 2D radial viewing range 
        Keyword Arguments:
        fov - float : field of view in degrees
        vdist - float : viewing distance
        pos - (float, float) : position of observer
        orient - float : orientation of observer
        pt - (float, float) : point to be tested
    '''
    # Check radial range
    r = sqrt(pow(pt[0] - pos[0], 2) + pow(pt[1] - pos[1], 2))
    r_range = False
    if r <= vdist:
        r_range = True
        
    # Check angular range
    fov2 = fov/2.0
    a1 = orient-fov2
    a2 = orient+fov2
    ang = np.angle(pt[0]+pt[1]*1j, deg=True)
    
    a_range = False
    if ang >= a1 and ang <= a2:
        a_range = True
    
    return (r_range and a_range)