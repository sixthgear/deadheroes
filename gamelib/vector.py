import math

class Vec2d(object):
    
    __slots__ = ['x', 'y']
    
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other):
        return Vec2d(self.x+other.x, self.y+other.y)
    
    def __sub__(self, other):
        return Vec2d(self.x-other.x, self.y-other.y)
    
    def __mul__(self, scalar):
        return Vec2d(self.x*scalar, self.y*scalar)
    
    def __div__(self, scalar):
        return Vec2d(self.x/scalar, self.y/scalar)
    
    def __rmul__(self, scalar):
        return Vec2d(self.x*scalar, self.y*scalar)
        
    def __rdiv__(self, scalar):
        return Vec2d(self.x/scalar, self.y/scalar)
        
    @property
    def magnitude(self):
        return math.hypot(self.x, self.y)

    @property
    def magnitude_sq(self):
        return self.x ** 2 + self.y ** 2
        
    @property
    def angle(self):
        return math.degrees(math.atan2(self.x, self.y))
        
    def zero(self):
        self.x = 0
        self.y = 0
        
    def normalize(self):
        l = self.magnitude
        if l == 0: return self
        self.x /= l
        self.y /= l

    @property
    def normal(self):
        l = self.magnitude
        if l == 0: return Vec2d()
        return Vec2d(self.x / l, self.y / l)
    
    def rotate(self, angle):
        angle = math.radians(angle)
        l = self.magnitude
        self.x = math.sin(angle) * l
        self.y = math.cos(angle) * l
        
    def rotated(self, angle):
        angle = math.radians(angle)
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        s = Vec2d()
        s.x = (self.x * cos_a) - (self.y * sin_a)
        s.y = (self.y * cos_a) + (self.x * sin_a)
        return s
    
    def copy(self):
        return Vec2d(self.x, self.y)
    
    def __repr__(self):
        return 'Vec2d(%.2f, %.2f)' % (self.x, self.y)


class Vec3d(object):
    
    __slots__ = ['x', 'y', 'z']
    
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __add__(self, other):
        return Vec3d(self.x+other.x, self.y+other.y, self.z+other.z)
    
    def __sub__(self, other):
        return Vec3d(self.x-other.x, self.y-other.y, self.z-other.z)
    
    def __mul__(self, scalar):
        return Vec3d(self.x*scalar, self.y*scalar, self.z*scalar)
    
    def __div__(self, scalar):
        return Vec3d(self.x/scalar, self.y/scalar, self.z/scalar)
    
    def __rmul__(self, scalar):
        return Vec3d(self.x*scalar, self.y*scalar, self.z*scalar)
        
    def __rdiv__(self, scalar):
        return Vec3d(self.x/scalar, self.y/scalar, self.z/scalar)
        
    @property
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    @property
    def magnitude_sq(self):
        return self.x**2 + self.y**2 + self.z**2

    # @property
    # def angle(self):
    #     return math.degrees(math.atan2(self.x, self.y))
    

    def zero(self):
        self.x = 0
        self.y = 0
        self.z = 0
        
    def normalize(self):
        l = self.magnitude
        if l == 0: return self
        self.x /= l
        self.y /= l
        self.z /= l

    @property
    def normal(self):
        l = self.magnitude
        if l == 0: return Vec3d()
        return Vec3d(self.x/l, self.y/l, self.z/l)
    
    def cross(self, other):            
        return Vec3d(self.y*other.z - self.z*other.y, self.z*other.x - self.x*other.z, self.x*other.y - self.y*other.x)
    
    # def rotate(self, angle):
    #     angle = math.radians(angle)
    #     l = self.magnitude
    #     self.x = math.sin(angle) * l
    #     self.y = math.cos(angle) * l
        
    # def rotated(self, angle):
    #     angle = math.radians(angle)
    #     sin_a = math.sin(angle)
    #     cos_a = math.cos(angle)
    #     s = Vec2d()
    #     s.x = (self.x * cos_a) - (self.y * sin_a)
    #     s.y = (self.y * cos_a) + (self.x * sin_a)
    #     return s
    
    def copy(self):
        return Vec3d(self.x, self.y, self.z)
    
    def __repr__(self):
        return 'Vec3d(%.2f, %.2f, %.2f)' % (self.x, self.y, self.z)        