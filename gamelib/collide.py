import vector
import math
    
def point_to_AABB(a, b, b_width, b_height):
    if a.x < b.x: return False
    if a.x > b.x + b_width: return False
    if a.y < b.y: return False
    if a.y > b.y + b_height: return False
    return True
    
def circle_to_AABB(a, a_radius, b, b_width, b_height):
    #todo: this needs to handle collisions with vertecies better
    # test for voroni regions
    if a.x + a_radius < b.x: return False
    if a.x - a_radius > b.x + b_width: return False
    if a.y + a_radius < b.y: return False
    if a.y - a_radius > b.y + b_height: return False
    
    return True    
    
def AABB_to_AABB(a, a_width, a_height, b, b_width, b_height):
    if a.x > b.x + b_width: return False
    if b.x > a.x + a_width: return False
    if a.y > b.y + b_height: return False
    if b.y > a.y + a_height: return False
    return True
            
def circle_to_circle(a, a_radius, b, b_radius):
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2 < (a_radius + b_radius) ** 2
    
def inv_circle_to_circle(a, a_radius, b, b_radius):
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2 > abs(a_radius - b_radius) ** 2    


# def AABB_to_segment(aabb, line): 

#     #line direction
#     mid = # midpoint of the line segment
#     hl = # segment half-length
#     #box

#     # ALGORITHM: Use the separating axis 
#     # theorem to see if the line segment 
#     # and the box overlap. A line 
#     # segment is a degenerate OBB. */

#     const VECTOR T = b.P - mid;
#     # VECTOR v;
#     # SCALAR r;

#     #do any of the principal axes
#     #form a separating axis?

#     if abs(T.x) > b.E.x + hl * abs(line.x):
#         return false

#     if abs(T.y) > b.E.y + hl * abs(line.y):
#         return false

#     # NOTE: Since the separating axis is
#     # perpendicular to the line in these
#     # last four cases, the line does not
#     # contribute to the projection. */

#     #l.cross(x-axis)?

#     r = b.E.y * abs(line.z) + b.E.z * abs(line.y)

#     if abs(T.y*l.z - T.z*l.y) > r:
#         return False

#     #l.cross(y-axis)?

#     r = b.E.x * abs(line.z) + b.E.z * abs(line.x)

#     if abs(T.z*l.x - T.x*l.z) > r:
#         return False

#     return True

