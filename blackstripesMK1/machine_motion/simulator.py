import json
import math
import Image
import ImageDraw

from driver import Driver
from builder import *
from machine_settings import *

#this Realsimulator acts like the real printer
class RealSimulator:
    def __init__(self,file):
        self.im = Image.new('RGBA',(g_MachineWidth,g_MachineWidth),(255,255,255,255))
        self.draw = ImageDraw.Draw(self.im)
        self.l ,self.r = g_NullPosition
        self.ticks = (round(self.l*STEPS_PER_MM_PREVIEW),round(self.r*STEPS_PER_MM_PREVIEW))
        x,y  = posFromLengths(self.l,self.r)
        self.draw.ellipse((x-2,y-2,x+2,y+2),fill=(255,0,255,255))
        print "length_left", self.l, "length_right", self.r, 'ticks on motors l,r :', self.ticks
        self.penstate = 0
        self.outputfile = file
        self.im.save(self.outputfile)
        self.stopped=0
    
    def printBatch(self,cmds):
        if(self.stopped==1):
            return
        for cmd in cmds:
            if(self.stopped==1):
                return
            self.executeInstruction(cmd)
    
    def executeInstruction(self,cmd):
        ticks0 = self.ticks[0] + cmd[0]
        ticks1 = self.ticks[1] + cmd[1]
        self.ticks = (ticks0,ticks1) 
        try:
            x,y  = posFromLengths(float(self.ticks[0])/STEPS_PER_MM_PREVIEW,float(self.ticks[1])/STEPS_PER_MM_PREVIEW)
        except:
            self.stopped = 1
            x,y = (500,500)
                
        if cmd[2]==-1 or self.penstate == 0:
            self.penstate = 0
            self.draw.rectangle((x,y,x+1,y+1),fill=(255,220,255,255))
    
        if cmd[2]==1 or self.penstate == 1:
            self.penstate = 1
            self.draw.rectangle((x,y,x+1,y+1),fill=(255,0,255,255))
        
    def show(self):
        self.im.save(self.outputfile)               
        
class SimuDriver(Driver):

    def __init__(self,file):
        self.file_base_name = file
        f = open(self.file_base_name+".json","r")
        jsonstring = f.read()
        self.data = json.loads(jsonstring)
        print 'json loaded: ',self.file_base_name+".json"
        
    def simulate(self):
        s = Simulator()
        counter = 0
        for layer in self.data:
            s.createSeperation(self.file_base_name+"_sep_"+str(counter)+".png")
            for line in layer:
                for dot in line:
                    try:
                        s.doDraw(dot)
                    except:
                        pass
            counter += 1
            
        s.createSeperation(self.file_base_name+"_sep_"+str(counter)+".png")
        s.save(self.file_base_name+"_poster.png")
    

    def run(self):
        print 'STEPS_PER_MM', STEPS_PER_MM
        print 'STEPS_PER_MM_PREVIEW', STEPS_PER_MM_PREVIEW
        self.left_accumulator = 0.0
        self.right_accumulator = 0.0
        self.up_accumulator = 0.0
        realSim = RealSimulator(self.file_base_name+'_realoutput.png')
        l,r = g_NullPosition
        self.currentpos = (int(round(l)),int(round(r)),0)
        counter = 0
        linecounter = 0
        layercounter = 0
        for layer in self.data:
            print 'layer: ',layercounter
            linecounter = 0
            layercounter +=1
            for line in layer:
                if line[0:5]=='layer':
                    linecounter +=1
                    continue    
                linecounter +=1
                counter = 0
                for dot in line:
                    if dot[2]==2:
                        batches = self.transition(dot, STEPS_PER_MM_PREVIEW)
                    else:
                        batches = self.drive(dot, STEPS_PER_MM_PREVIEW)
                    for batch in batches:   
                        realSim.printBatch(batch)
                        counter += 1
        
        realSim.show()

class Simulator:

    def __init__(self):
        self.sep = None
        self.im = Image.new('RGBA',(g_MachineWidth,g_MachineWidth),(255,255,255,255))
        self.draw = ImageDraw.Draw(self.im)
        self.draw.ellipse((LEFT_STEPPER_POS[0]-50,LEFT_STEPPER_POS[1]-50,LEFT_STEPPER_POS[0]+50,LEFT_STEPPER_POS[1]+50),fill=(255,0,0,255))
        self.draw.ellipse((RIGHT_STEPPER_POS[0]-50,RIGHT_STEPPER_POS[1]-50,RIGHT_STEPPER_POS[0]+50,RIGHT_STEPPER_POS[1]+50),fill=(255,0,0,255))

    def createSeperation(self,name):
        if self.sep:
            self.sep.save(self.sep_name)
        self.sep = Image.new('RGBA',(g_MachineWidth,g_MachineWidth),(255,255,255,255))
        self.sep_draw = ImageDraw.Draw(self.sep)
        self.sep_draw.ellipse((LEFT_STEPPER_POS[0]-50,LEFT_STEPPER_POS[1]-50,LEFT_STEPPER_POS[0]+50,LEFT_STEPPER_POS[1]+50),fill=(255,0,0,255))
        self.sep_draw.ellipse((RIGHT_STEPPER_POS[0]-50,RIGHT_STEPPER_POS[1]-50,RIGHT_STEPPER_POS[0]+50,RIGHT_STEPPER_POS[1]+50),fill=(255,0,0,255))
        self.sep_name = name

    def doDraw(self,dot):
        pos = posFromLengths(dot[0],dot[1])
        if dot[2] == 1:
            self.draw.ellipse((pos[0]-DOTSIZE,pos[1]-DOTSIZE,pos[0]+DOTSIZE,pos[1]+DOTSIZE),fill=(0,0,0,LINE_ALPHA))
            if self.sep:
                self.sep_draw.ellipse((pos[0]-DOTSIZE,pos[1]-DOTSIZE,pos[0]+DOTSIZE,pos[1]+DOTSIZE),fill=(0,0,0,255))
        elif dot[2] == 2:
            self.draw.ellipse((pos[0]-TRANSITION_DOTSIZE,pos[1]-TRANSITION_DOTSIZE,pos[0]+TRANSITION_DOTSIZE,pos[1]+TRANSITION_DOTSIZE),fill=(255,0,0,100))
            if self.sep:
                self.sep_draw.ellipse((pos[0]-TRANSITION_DOTSIZE,pos[1]-TRANSITION_DOTSIZE,pos[0]+TRANSITION_DOTSIZE,pos[1]+TRANSITION_DOTSIZE),fill=(255,0,0,100))
        elif dot[2] == 3:
            self.draw.ellipse((pos[0]-TRANSITION_DOTSIZE,pos[1]-TRANSITION_DOTSIZE,pos[0]+TRANSITION_DOTSIZE,pos[1]+TRANSITION_DOTSIZE),fill=(0,255,0,100))
            if self.sep:
                self.sep_draw.ellipse((pos[0]-TRANSITION_DOTSIZE,pos[1]-TRANSITION_DOTSIZE,pos[0]+TRANSITION_DOTSIZE,pos[1]+TRANSITION_DOTSIZE),fill=(0,255,0,100))
    def save(self,name):
        self.im.save(name)


if __name__ == '__main__':
    basepath = "generated_data/testies/"
    order_id = "testies"

    drivr = SimuDriver(basepath+order_id)
    drivr.simulate()
    
    #this is for the real simulated output with all printer paths visialized in light magenta, saved in realoutput.png
    drivr.run()    
