
import struct
import Coder
from machine_settings import *
from Model import Blackstripes_MKII
import Image,ImageDraw
import sys

PIX_PER_MM = 3
HALF_MARKER_PIXEL_SIZE = int(round((MARKER_NIB_SIZE_MM * PIX_PER_MM)/2.0))

class Progress:

    def __init__(self):
        pass

    def setProgress(self,progress):
        sys.stdout.write("\rSimulating output: %d%%\t" %progress)    # or print >> sys.stdout, "\r%d%%" %i,
        sys.stdout.flush()

class Simulator:

    def __init__(self,motiondata,imagedata,numInstructions=None):

        self.leftangle = 90
        self.rightangle = 90

        self.progressUI = Progress()

        self.prev_x = -1
        self.prev_y = -1
        self.progress = -1

        self.levels = [217, 180, 144, 108, 72, 36]

        self.canvas = Image.new("RGBA",(1000*PIX_PER_MM,1200*PIX_PER_MM),color=(255,255,255,255))
        self.draw = ImageDraw.Draw(self.canvas)

        self.redlayer = Image.new("RGBA",(1000*PIX_PER_MM,1200*PIX_PER_MM),color=(255,255,255,0))
        self.draw2 = ImageDraw.Draw(self.redlayer)

        self.blacklayer = Image.new("RGBA",(1000*PIX_PER_MM,1200*PIX_PER_MM),color=(255,255,255,0))
        self.draw3 = ImageDraw.Draw(self.blacklayer)

        self.model = Blackstripes_MKII()

        self.instructionsExecuted = 0.0
        self.numInstructions = float(numInstructions)

        self.pixels = []
        self.imagedata = open(imagedata,'rb')
        try:
            byte = self.imagedata.read(1)
            while byte != "":
                sample = struct.unpack('B',byte)
                self.pixels.append(sample[0])
                byte = self.imagedata.read(1)
        finally:
            self.imagedata.close()

        self.motiondata = open(motiondata,'rb')
        try:
            byte = self.motiondata.read(16)
            while byte != "":
                sample = struct.unpack('=LLLL',byte)
                left_engine,right_engine,p1,p2,p3,even,speed = Coder.decode(sample[0])
                sol1 = sample[1]
                sol2 = sample[2] 
                sol3 = sample[3]
                self._draw(left_engine,right_engine,p1,p2,p3,even,speed,sol1,sol2,sol3)
                byte = self.motiondata.read(16)
        finally:
            self.canvas.paste(self.redlayer,self.redlayer)
            self.canvas.paste(self.blacklayer,self.blacklayer)
            self.canvas.save("blackstripes_preview.png")
            self.motiondata.close()

    def controlMarker(self,x,y,sol,p,levels_tup,even,color,draw):
        x = x*PIX_PER_MM
        y = y*PIX_PER_MM
        pix = (x-HALF_MARKER_PIXEL_SIZE,y-HALF_MARKER_PIXEL_SIZE,x+HALF_MARKER_PIXEL_SIZE,y+HALF_MARKER_PIXEL_SIZE)
        if p == 1:
            if sol < 1000000 and self.pixels[sol+6] < self.levels[levels_tup[0]] and even == 1:
                draw.ellipse(pix, fill=color)
            elif sol < 1000000 and self.pixels[sol+6] < self.levels[levels_tup[1]] and even == 0:
                draw.ellipse(pix, fill=color)
        elif p == 2:
            draw.ellipse(pix, fill=color)

    def _draw(self,left_engine,right_engine,p1,p2,p3,even,speed,sol1,sol2,sol3):

        self.instructionsExecuted += 1
        progress = (self.instructionsExecuted / self.numInstructions) * 100.0

        if self.progress != int(round(progress)):
            self.progress = int(round(progress))
            self.progressUI.setProgress(self.progress)

        if left_engine < 1:
            self.leftangle -= ANGLE_PER_STEP
        elif left_engine > 1:
            self.leftangle += ANGLE_PER_STEP

        if right_engine < 1:
            self.rightangle -= ANGLE_PER_STEP
        elif right_engine > 1:
            self.rightangle += ANGLE_PER_STEP

        mx1,my1,mx2,my2,mx3,my3 = self.model.calculateMarkerPositions(self.leftangle,self.rightangle)

        x,y = self.model.getXYonCanvas(mx1,my1)

        x = int(round(x))
        y = int(round(y))

        if x == self.prev_x and y == self.prev_y:
            return;

        self.controlMarker(x,y,sol1,p1,(0,1),even,(150,150,150,255),self.draw)

        x2,y2 = self.model.getXYonCanvas(mx2,my2)
        self.controlMarker(x2,y2,sol2,p2,(2,3),even,(255,0,0,255),self.draw2)

        x3,y3 = self.model.getXYonCanvas(mx3,my3)
        self.controlMarker(x3,y3,sol3,p3,(4,5),even,(0,0,0,255),self.draw3)

        self.prev_x = x
        self.prev_y = y




if __name__ == "__main__":
    Simulator("spiral.bin","../image_input/output/jasmijn.bsi",8000000)
    #Simulator("scanlines.bin","../image_input/output/frank.bsi",8239711)
    

