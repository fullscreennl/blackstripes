import math
from machine_settings import *

class ScanLines:

    def __init__(self,s,nib_size_mm=0.5):

        self.BOTTOM_SPEED = 0
        self.TOP_SPEED = 475

        x = 0
        y = 0

        self.center = (500,500)
        self.start = (x, y)
        self.s = s
        self.s.setEven(0)
        self.s.setBoundsFunction(self.inBbox)
        self.nib_size_mm = nib_size_mm  
        self.generate()

    def inBbox(self,x, y):
        xnull = CENTER - 500.0
        ynull = SHOULDER_HEIGHT+CANVAS_Y
        padding = 25
        return int(x >= xnull+padding and x<= xnull+1000-padding and y >= ynull+padding and y <= ynull+1000-padding)

    def toradians(self,deg):
        return deg * math.pi/180.0

    def sign(self):
        import json
        f = open("assets/signature_data.json","r") 
        data = json.loads(f.read())

        self.s.releaseMoveMode()

        x_offset,y_offset = data[0]
        for pos in data:
            x,y = pos
            x = (x - x_offset ) / 10.0 + 780
            y = (y - y_offset ) / 10.0 + 970
            a1,a2 = self.s.getStateFromXYonCanvas(x,y)
            xy = self.s.appendAngles(a1,a2)

        return xy

    def saveEnding(self):
        self.s.endLine(self.BOTTOM_SPEED,1000)
        self.s.beginLine(self.BOTTOM_SPEED,self.TOP_SPEED,1000)

    def generate(self): 
    
        self.s.setMoveMode()
        self.s.drawLineFromTo(HOME, self.start,-1,beginspeed=0,endspeed=0)
        self.s.releaseMoveMode()

        x,y = self.start

        self.s.beginLine(self.BOTTOM_SPEED,self.TOP_SPEED,500)

        for scan in range(125):

            self.s.setEven(0)
            for i in range(1000):
                x += 1
                self.s.drawStateFromXYonCanvas(x,y)
        
            self.saveEnding()
            for ypos in range(4):
                y += 1
                self.s.drawStateFromXYonCanvas(x,y)
            self.saveEnding()
            
            self.s.setEven(1)
            for i in range(1000):
                x -= 1
                self.s.drawStateFromXYonCanvas(x,y)
                
            self.saveEnding()
            for ypos in range(4):
                y += 1
                self.s.drawStateFromXYonCanvas(x,y)
            self.saveEnding()
        
        self.s.endLine(0,500)

        self.s.setMoveMode()
        self.s.drawLineFromTo((x,y),(780,970),-1)
        self.s.releaseMoveMode()

        self.s.beginLine(0,35,500)
        x,y = self.sign()
        self.s.endLine(0,500)

        self.s.setMoveMode()
        self.s.drawLineFromTo((x,y),HOME,-1)
        self.s.releaseMoveMode()
        
if __name__ == "__main__":
    pass
    



    
    
    
    
    
    
    
    
    
    
    