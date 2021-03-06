import math
from machine_settings import *

class BaseSpiral:

    def configure(self):
        msg = """

            please implement configure.

            example:
            
            def configure(self):
                self.radius = 489.0
                self.spiral_start = (989.0 ,500.0)
                self.bounding_radius = 465
                self.signature_pos = (790,917)
                self.max_cycles = 119

            """
        raise Exception(msg)

    def __init__(self,s,nib_size_mm=0.5,base_path=""):
        self.base_path = base_path
        self.configure()
        self.center = (500,500)
        self.s = s
        self.s.setEven(0)
        self.s.setBoundsFunction(self.inCircle)
        self.nib_size_mm = nib_size_mm  
        self.generate()

    def inCircle(self,x, y):
        xnull = CENTER - 500.0
        ynull = SHOULDER_HEIGHT+CANVAS_Y
        center_x, center_y = (500 + xnull,500 + ynull)
        square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
        return int(square_dist <= self.bounding_radius ** 2)

    def toradians(self,deg):
        return deg * math.pi/180.0

    def sign(self):
        import json
        f = open(self.base_path+"assets/signature_data.json","r") 
        data = json.loads(f.read())

        self.s.releaseMoveMode()

        x_offset,y_offset = data[0]
        for pos in data:
            x,y = pos
            x = (x - x_offset ) / 10.0 + self.signature_pos[0]
            y = (y - y_offset ) / 10.0 + self.signature_pos[1]
            a1,a2 = self.s.getStateFromXYonCanvas(x,y)
            xy = self.s.appendAngles(a1,a2)

        return xy

    def generate(self): 
    
        self.s.setMoveMode()
        self.s.drawLineFromTo(HOME, self.spiral_start,-1,beginspeed=0,endspeed=0)
        self.s.releaseMoveMode()
        
        num_cycles = int(round((self.radius+1.0)/self.nib_size_mm))
        
        sp = 0
        ease_speed = 0
        cycle_count = 0
        
        numiterations = 3600*num_cycles
        
        self.s.beginLine(0,483,1000)

        for ang in range(numiterations):
        
            x = math.cos(float(self.toradians(ang))/10.0) * self.radius + self.center[0]
            y = math.sin(float(self.toradians(ang))/10.0) * self.radius + self.center[1]
            
            self.radius -= (self.nib_size_mm/3600.0)
            
            if ang/3600 % 2 == 0:
                self.s.setEven(1)
            else:
                self.s.setEven(0)

            if ang%3600 == 0:
                cycle_count += 1
                if cycle_count ==  self.max_cycles:
                    self.s.endLine(387,200000)
                    self.s.beginLine(387,387,5)

            self.s.drawStateFromXYonCanvas(x,y)
        
        self.s.endLine(0,500)

        self.s.setMoveMode()
        self.s.drawLineFromTo((x,y),self.signature_pos,-1)
        self.s.releaseMoveMode()

        self.s.beginLine(0,35,500)
        x,y = self.sign()
        self.s.endLine(0,500)

        self.s.setMoveMode()
        self.s.drawLineFromTo((x,y),HOME,-1)
        self.s.releaseMoveMode()
        
if __name__ == "__main__":
    from Model import Blackstripes_MKII
    m = Blackstripes_MKII()
    BaseSpiral(m,MARKER_NIB_SIZE_MM)

    
