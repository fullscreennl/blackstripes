import json
import math
import os

from printer import Printer
from machine_settings_xlarge import *

class Driver:

    def __init__(self,file,tempdir=""):
        self.file = file
        self.tempdir = tempdir
        self.f = open(file+"_sep.json","r")
        print 'opening file: ',file

    def run(self, line_to_start, start):
        self.left_accumulator = 0.0
        self.right_accumulator = 0.0
        self.up_accumulator = 0.0
        printer = Printer(self.tempdir)
        #printer.executeInstruction([0,0,-1],0)
        if line_to_start == 0  or start == 0:
            l,r = g_NullPosition
            x = 0
        else:
            l,r,x = self.findPreviouslinePos(line_to_start-1,self.file)
        self.currentpos = (int(round(l)),int(round(r)),x)
        counter = 0
        linecounter = 0
        layercounter = 0
        for line in self.f:
            if linecounter >= line_to_start:
                if line[1:6]=='layer':
                    printer.saveLayer()
                    linecounter +=1
                    continue
                linedata_2 = json.loads(line)
                sublines = self.analyseLine(linedata_2)
                for linedata in sublines:
                    counter = 0
                    length = len(linedata)
                    for dot in linedata:
                        if dot[2]==2:
                            batches = self.transition(dot, STEPS_PER_MM)
                        else:
                            batches = self.drive(dot, STEPS_PER_MM)
                        for batch in batches:   
                            printer.printBatch(batch,counter, length)
                            counter += 1
            linecounter +=1
        self.f.close()  

    def analyseLine(self, data):
        counter = 0
        previouspos = 0
        previouscounter = 0
        sublines=[]
        for millimeter in data:
            penpos = millimeter[2]
            if(penpos!=previouspos):
                currentindex = counter  
                sublines.append(data[previouscounter:currentindex])
                previouscounter = currentindex
            previouspos = penpos
            counter +=1
        return sublines 

    def findPreviouslinePos(self, prevline,file):
        f = open(file,"r")
        linecounter=0
        for line in f:
            if linecounter == prevline:
                linedata = json.loads(line)
                break
            linecounter +=1
        dot = linedata[len(linedata)-1]
        l,r,x = dot
        pos = (l,r,x)
        f.close()
        return pos
        
    def transition(self,command, stepSetting):
        #print 'current step', stepSetting
        # calculate deltas.
        if(command[2]>1):
            command[2] = 0
        deltaleft = command[0] - self.currentpos[0] 
        deltaright = command[1] - self.currentpos[1] 
        delta_up = command[2] - self.currentpos[2]
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
        numstepsleft = deltaleft * stepSetting
        numstepsright = deltaright * stepSetting
        numsteps_up = 1
        
        #round to whole steps
        r_numstepsleft = math.ceil(numstepsleft)
        r_numstepsright = math.ceil(numstepsright)
        r_numsteps_up = round(numsteps_up)
        
        #calc leftovers
        self.left_accumulator +=  numstepsleft - r_numstepsleft
        self.right_accumulator +=  numstepsright - r_numstepsright
        #self.up_accumulator = numsteps_up - r_numsteps_up
        
        #add leftover values of earlier steps
        r_numstepsleft = r_numstepsleft +leftoff
        r_numstepsright = r_numstepsright +rightoff
        
        #determine max
        steps = abs(r_numstepsleft), abs(r_numstepsright), abs(r_numsteps_up)
        maxSteps = max(steps)
        
        left_dir,right_dir,up_dir = self.createDirs(deltaleft, deltaright, delta_up) 
       
        #applied steps
        batches = []
        sharedsteps = min(abs(r_numstepsleft),abs(r_numstepsright))
        

        batch = self.createBatch(sharedsteps, r_numstepsleft, r_numstepsright, r_numsteps_up, left_dir, right_dir, up_dir) 
        batches.append(batch)
    
        leftstep_surplus = int(abs(r_numstepsleft)-sharedsteps)
        if leftstep_surplus > 0:
            batch = self.createBatch(leftstep_surplus, r_numstepsleft, 0, r_numsteps_up, left_dir, right_dir, up_dir) 
            batches.append(batch)

        rightstep_surplus = int(abs(r_numstepsright)-sharedsteps)
        if rightstep_surplus > 0:
            batch = self.createBatch(rightstep_surplus, 0, r_numstepsright, r_numsteps_up, left_dir, right_dir, up_dir) 
            batches.append(batch)
       
        self.currentpos = command[0], command[1], command[2]
        if deltaleft>0 and deltaright>0:
            batches.reverse()
        return batches
                            
    def drive(self,command, stepSetting):
        if(command[2]>1):
            command[2] = 0
        # calculate deltas
        deltaleft = command[0] - self.currentpos[0] 
        deltaright = command[1] - self.currentpos[1] 
        delta_up = command[2] - self.currentpos[2]
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
        numstepsleft = deltaleft * stepSetting
        numstepsright = deltaright * stepSetting
        numsteps_up = 1
        
        #round to whole steps
        r_numstepsleft = math.ceil(numstepsleft)
        r_numstepsright = math.ceil(numstepsright)
        r_numsteps_up = round(numsteps_up)
        
        #calc leftovers
        self.left_accumulator +=  numstepsleft - r_numstepsleft
        self.right_accumulator +=  numstepsright - r_numstepsright
        #self.up_accumulator = numsteps_up - r_numsteps_up
        
        r_numstepsleft = r_numstepsleft +leftoff
        r_numstepsright = r_numstepsright +rightoff
        
        #determine max
        steps = abs(r_numstepsleft), abs(r_numstepsright), abs(r_numsteps_up)
        maxSteps = max(steps)
        
        #prep batch/command
       
        left_dir,right_dir,up_dir = self.createDirs(deltaleft, deltaright, delta_up)    
        batch = self.createBatch(maxSteps, r_numstepsleft, r_numstepsright, r_numsteps_up, left_dir, right_dir, up_dir)       
        self.currentpos = command[0], command[1], command[2]
        batches = []
        batches.append(batch)
        return batches

    def createBatch(self, nrSteps, r_numstepsleft, r_numstepsright, r_numsteps_up, left_dir, right_dir, up_dir):
        a_numstepsleft = 0
        a_numstepsright = 0
        a_numsteps_up = 0
        batch = []    
        for st in range(int(nrSteps)):
            l = 0
            r = 0
            u = 0
            if a_numstepsleft < abs(r_numstepsleft): 
                l = 1*left_dir
                a_numstepsleft += 1
            if a_numstepsright < abs(r_numstepsright): 
                r = 1*right_dir
                a_numstepsright += 1
            if a_numsteps_up < abs(r_numsteps_up): 
                u = 1*up_dir
                a_numsteps_up += 1
            batch.append((l,r,u)) 
        return batch

    def createDirs(self, deltaleft, deltaright, delta_up):
        if deltaleft > 0: 
            left_dir = 1 
        else: 
            left_dir = -1
            
        if deltaright > 0: 
            right_dir = 1 
        else: 
            right_dir = -1
            
        if delta_up > 0: 
            up_dir = 1 
        elif delta_up == 0:
            up_dir = 0
        else: 
            up_dir = -1
        return (left_dir,right_dir,up_dir)    

if __name__ == '__main__':
    basepath = "generated_data/testies/"
    order_id = "testies"
    driver = Driver(basepath+order_id)
    linenr = 0
    start = 0
    driver.run(int(linenr),start)        