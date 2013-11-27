import json
import math
import Image
import ImageDraw

from driver import Driver
from builder import *
#from printer import Printer
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
        #print 'cmds string: ',cmds
        for cmd in cmds:
            if(self.stopped==1):
                return
            self.executeInstruction(cmd)
    
    def executeInstruction(self,cmd):
        #print 'executeInstruction',cmd
        ticks0 = self.ticks[0] + cmd[0]
        ticks1 = self.ticks[1] + cmd[1]
        self.ticks = (ticks0,ticks1) 
        #if(cmd[1]<0):
        #   print 'incoming cmd',cmd
        #   print 'ticks',self.ticks
        try:
            x,y  = posFromLengths(float(self.ticks[0])/STEPS_PER_MM_PREVIEW,float(self.ticks[1])/STEPS_PER_MM_PREVIEW)
        except:
            self.stopped = 1
            x,y = (500,500)
            #self.show()
                
        if cmd[2]==-1 or self.penstate == 0:
            self.penstate = 0
            #self.draw.ellipse((x-1,y-1,x+1,y+1),fill=(255,220,255,255))
            self.draw.rectangle((x,y,x+1,y+1),fill=(255,220,255,255))
    
        if cmd[2]==1 or self.penstate == 1:
            self.penstate = 1
            #print 'executeInstruction',cmd
            #self.draw.ellipse((x-1,y-1,x+1,y+1),fill=(255,0,255,255))
            self.draw.rectangle((x,y,x+1,y+1),fill=(255,0,255,255))
        
    def show(self):
        #self.im.show()
        self.im.save(self.outputfile)               
        
class SimuDriver(Driver):

    def __init__(self,file):
        self.file_base_name = file
        f = open(self.file_base_name+".json","r")
        print self.file_base_name+".json"
        jsonString = f.read()
        self.data = json.loads(jsonString)
        print 'loading json done: ',file
        
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
                        print "invalid dot ",dot
            counter += 1
            #s.save("layer_"+str(counter)+".png")
            
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
        self.currentPos = (int(round(l)),int(round(r)),0)
        counter = 0
        linecounter = 0
        layercounter = 0
        for layer in self.data:
            print 'layer: ',layercounter
            linecounter = 0
            layercounter +=1
            for line in layer:
                #print 'line: ',line[0:5]
                if line[0:5]=='layer':
                    print 'line is a label',line
                    linecounter +=1
                    continue    
                linecounter +=1
                counter = 0
                for dot in line:
                    #print 'dotcounter', counter
                    #print "GPIO ",counter," -> command : ",dot
                    if dot[2]==2:
                        #print self.transition
                        batches = self.transition(dot, STEPS_PER_MM_PREVIEW)

                        #batches = self.drive(dot)
                    else:
                        batches = self.drive(dot, STEPS_PER_MM_PREVIEW)
                    for batch in batches:   
                        realSim.printBatch(batch)
                        #printer.printBatch(batch)
                        counter += 1
        
        realSim.show()

    """
    def transition(self,command):
    
        #print self.currentPos ," -> ", command
        #print 'pen command in drive: ', command[2]
        #calc deltas
        if(command[2]>1):
            command[2] = 0
        deltaLeft = command[0] - self.currentPos[0] 
        deltaRight = command[1] - self.currentPos[1] 
        deltaUP = command[2] - self.currentPos[2]
        leftoff = 0
        rightoff = 0
        if(abs(math.floor(self.left_accumulator))>=1.0):
            if( self.left_accumulator>0 ):
                self.left_accumulator = self.left_accumulator - 1.0
                leftoff = 1
            else:
                self.left_accumulator = self.left_accumulator + 1.0
                leftoff = -1
        
        if(abs(math.floor(self.right_accumulator))>=1.0):
            if( self.right_accumulator>0 ):
                self.right_accumulator = self.right_accumulator - 1.0
                rightoff = 1
            else:
                self.right_accumulator = self.right_accumulator + 1.0
                rightoff = -1
        #convert to steps
        numStepsLeft = deltaLeft * STEPS_PER_MM_PREVIEW
        numStepsRight = deltaRight * STEPS_PER_MM_PREVIEW
        numStepsUP = 1
        
        #round to whole steps
        r_numStepsLeft = math.ceil(numStepsLeft)
        r_numStepsRight = math.ceil(numStepsRight)
        r_numStepsUP = round(numStepsUP)
        
        
        #calc leftovers
        self.left_accumulator +=  numStepsLeft - r_numStepsLeft
        self.right_accumulator +=  numStepsRight - r_numStepsRight
        #self.up_accumulator = numStepsUP - r_numStepsUP
        
        #add leftover values of earlier steps
        
        #leftoff = 0
        #rightoff = 0
        r_numStepsLeft = r_numStepsLeft +leftoff
        r_numStepsRight = r_numStepsRight +rightoff
        
        #determine max
        steps = abs(r_numStepsLeft), abs(r_numStepsRight), abs(r_numStepsUP)
        maxSteps = max(steps)
        
        #prep batch/command
        
        
        #print "steps: ",steps," MAX : ",maxSteps
        
        #left_freq = maxSteps / r_numStepsLeft
        #right_freq = maxSteps / r_numStepsRight
        #up_freq = maxSteps / r_numStepsUP
        
        if deltaLeft > 0: 
            left_dir = 1 
        else: 
            left_dir = -1
            
        if deltaRight > 0: 
            right_dir = 1 
        else: 
            right_dir = -1
            
        if deltaUP > 0: 
            up_dir = 1 
        elif deltaUP == 0:
            up_dir = 0
        else: 
            up_dir = -1
                
        #applied steps
        a_numStepsLeft = 0
        a_numStepsRight = 0
        a_numStepsUP = 0
        
        batches = []
        batch = []
            
        sharedSteps = min(abs(r_numStepsLeft),abs(r_numStepsRight))
        
        for st in range(int(sharedSteps)):
            l = 0
            r = 0
            u = 0
            if a_numStepsLeft < abs(r_numStepsLeft): 
                l = 1*left_dir
                a_numStepsLeft += 1
            if a_numStepsRight < abs(r_numStepsRight): 
                r = 1*right_dir
                a_numStepsRight += 1
            if a_numStepsUP < abs(r_numStepsUP): 
                u = 1*up_dir
                #a_numStepsUP += 1
            batch.append((l,r,u))
        
        batches.append(batch)
        batch = []
    
        
        for st in range(int(abs(r_numStepsLeft)-sharedSteps)):
            l = 0
            r = 0
            u = 0
            if a_numStepsLeft < abs(r_numStepsLeft): 
                l = 1*left_dir
                a_numStepsLeft += 1
            if a_numStepsUP < abs(r_numStepsUP): 
                u = 1*up_dir
                #a_numStepsUP += 1
            batch.append((l,r,u))
        if len(batch)>0: 
            batches.append(batch)
        batch = []
        
        for st in range(int(abs(r_numStepsRight)- sharedSteps)):
            l = 0
            r = 0
            u = 0
            if a_numStepsRight < abs(r_numStepsRight): 
                r = 1*right_dir
                a_numStepsRight += 1
            if a_numStepsUP < abs(r_numStepsUP): 
                u = 1*up_dir
                #a_numStepsUP += 1
            batch.append((l,r,u))   
        #print "self.left_accumulator ",self.left_accumulator
        #print batch
        
        self.currentPos = command[0], command[1], command[2]
        
        if len(batch)>0: 
            batches.append(batch)
        
        if deltaLeft>0 and deltaRight>0:
            batches.reverse()   
        
        return batches
        #time.sleep(2) 
   
    def drive(self,command):
    
        #print self.currentPos ," -> ", command
        #print 'pen command in drive: ', command[2]
        if(command[2]>1):
            command[2] = 0
        #calc deltas
        deltaLeft = command[0] - self.currentPos[0] 
        deltaRight = command[1] - self.currentPos[1] 
        deltaUP = command[2] - self.currentPos[2]
        leftoff = 0
        rightoff = 0
        if(abs(math.floor(self.left_accumulator))>=1.0):
            if( self.left_accumulator>0 ):
                self.left_accumulator = self.left_accumulator - 1.0
                leftoff = 1
            else:
                self.left_accumulator = self.left_accumulator + 1.0
                leftoff = -1
        
        if(abs(math.floor(self.right_accumulator))>=1.0):
            if( self.right_accumulator>0 ):
                self.right_accumulator = self.right_accumulator - 1.0
                rightoff = 1
            else:
                self.right_accumulator = self.right_accumulator + 1.0
                rightoff = -1
        #convert to steps
        numStepsLeft = deltaLeft * STEPS_PER_MM_PREVIEW
        numStepsRight = deltaRight * STEPS_PER_MM_PREVIEW
        numStepsUP = 1
        
        #round to whole steps
        r_numStepsLeft = math.ceil(numStepsLeft)
        r_numStepsRight = math.ceil(numStepsRight)
        r_numStepsUP = round(numStepsUP)
        
        
        #calc leftovers
        self.left_accumulator +=  numStepsLeft - r_numStepsLeft
        self.right_accumulator +=  numStepsRight - r_numStepsRight
        #self.up_accumulator = numStepsUP - r_numStepsUP
        
        #add leftover values of earlier steps
       
        #leftoff = 0
        #rightoff = 0
        r_numStepsLeft = r_numStepsLeft +leftoff
        r_numStepsRight = r_numStepsRight +rightoff
        
        #determine max
        steps = abs(r_numStepsLeft), abs(r_numStepsRight), abs(r_numStepsUP)
        maxSteps = max(steps)
        
        #prep batch/command
        batch = []
        
        #print "steps: ",steps," MAX : ",maxSteps
        
        #left_freq = maxSteps / r_numStepsLeft
        #right_freq = maxSteps / r_numStepsRight
        #up_freq = maxSteps / r_numStepsUP
        
        if deltaLeft > 0: 
            left_dir = 1 
        else: 
            left_dir = -1
            
        if deltaRight > 0: 
            right_dir = 1 
        else: 
            right_dir = -1
            
        if deltaUP > 0: 
            up_dir = 1 
        elif deltaUP == 0:
            up_dir = 0
        else: 
            up_dir = -1
                
        #applied steps
        a_numStepsLeft = 0
        a_numStepsRight = 0
        a_numStepsUP = 0
        
        for st in range(int(maxSteps)):
            l = 0
            r = 0
            u = 0
            if a_numStepsLeft < abs(r_numStepsLeft): 
                l = 1*left_dir
                a_numStepsLeft += 1
            if a_numStepsRight < abs(r_numStepsRight): 
                r = 1*right_dir
                a_numStepsRight += 1
            if a_numStepsUP < abs(r_numStepsUP): 
                u = 1*up_dir
                a_numStepsUP += 1
            batch.append((l,r,u))
            
        #print "self.left_accumulator ",self.left_accumulator
        #print batch
        
        self.currentPos = command[0], command[1], command[2]
        batches = []
        batches.append(batch)
        return batches
        #time.sleep(2) 
        """


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
    #STEPS_PER_MM = STEPS_PER_MM_PREVIEW
    drivr = SimuDriver(basepath+order_id)
    drivr.simulate()
    
    #this is for the real simulated output with all printer paths visialized in light magenta, saved in realoutput.png
    drivr.run()    
