import json
import math

from printer import Printer
from machine_settings import *

class Driver:

    def __init__(self,file):
        self.file = file
        self.f = open(file+"_sep.json","r")
        print 'opening file: ',file

    def run(self, lineToStart, start):
        self.left_accumulator = 0.0
        self.right_accumulator = 0.0
        self.up_accumulator = 0.0
        printer = Printer(self.file)
        printer.executeInstruction([0,0,-1],0)
        if lineToStart==0  or start ==0:
            l,r = g_NullPosition
            x = 0
        else:
            l,r,x = self.findPreviouslinePos(lineToStart-1,self.file)
        self.currentPos = (int(round(l)),int(round(r)),x)
        counter = 0
        linecounter = 0
        layercounter = 0
        for line in self.f:
            if linecounter >= lineToStart:
                if line[1:6]=='layer':
                    printer.saveLayer()
                    print 'line is a label',line
                    linecounter +=1
                    continue
                lineData2 = json.loads(line)
                sublines = self.analyseLine(lineData2)
                print 'line: ',linecounter
                for lineData in sublines:
                    counter = 0
                    length = len(lineData)
                    for dot in lineData:
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
        previousPenPos = 0
        previousCounter = 0
        sublines=[]
        for millimeter in data:
            penpos = millimeter[2]
            if(penpos!=previousPenPos):
                currentIndex = counter  
                sublines.append(data[previousCounter:currentIndex])
                previousCounter = currentIndex
            
            previousPenPos = penpos
            counter +=1
        return sublines 

    def findPreviouslinePos(self, prevline,file):
        f = open(file,"r")
        linecounter=0
        for line in f:
            if linecounter == prevline:
                print 'found previous line', linecounter
                lineData = json.loads(line)
                break
            linecounter +=1
        dot = lineData[len(lineData)-1]
        print 'last dot in prev line',dot
        l,r,x = dot
        pos = (l,r,x)
        f.close()
        return pos
        
    def transition(self,command, stepSetting):
        #print 'current step', stepSetting
        # calculate deltas.
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
        numStepsLeft = deltaLeft * stepSetting
        numStepsRight = deltaRight * stepSetting
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
        r_numStepsLeft = r_numStepsLeft +leftoff
        r_numStepsRight = r_numStepsRight +rightoff
        
        #determine max
        steps = abs(r_numStepsLeft), abs(r_numStepsRight), abs(r_numStepsUP)
        maxSteps = max(steps)
        
        left_dir,right_dir,up_dir = self.createDirs(deltaLeft, deltaRight, deltaUP) 
       
        #applied steps
        batches = []
        sharedSteps = min(abs(r_numStepsLeft),abs(r_numStepsRight))
        

        batch = self.createBatch(sharedSteps, r_numStepsLeft, r_numStepsRight, r_numStepsUP, left_dir, right_dir, up_dir) 
        batches.append(batch)
    
        leftStepsSurplus = int(abs(r_numStepsLeft)-sharedSteps)
        if leftStepsSurplus > 0:
            batch = self.createBatch(leftStepsSurplus, r_numStepsLeft, 0, r_numStepsUP, left_dir, right_dir, up_dir) 
            batches.append(batch)

        rightStepsSurplus = int(abs(r_numStepsRight)-sharedSteps)
        if rightStepsSurplus > 0:
            batch = self.createBatch(rightStepsSurplus, 0, r_numStepsRight, r_numStepsUP, left_dir, right_dir, up_dir) 
            batches.append(batch)
       
        self.currentPos = command[0], command[1], command[2]
        if deltaLeft>0 and deltaRight>0:
            batches.reverse()
        return batches
                            
    def drive(self,command, stepSetting):
        if(command[2]>1):
            command[2] = 0
        # calculate deltas
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
        numStepsLeft = deltaLeft * stepSetting
        numStepsRight = deltaRight * stepSetting
        numStepsUP = 1
        
        #round to whole steps
        r_numStepsLeft = math.ceil(numStepsLeft)
        r_numStepsRight = math.ceil(numStepsRight)
        r_numStepsUP = round(numStepsUP)
        
        #calc leftovers
        self.left_accumulator +=  numStepsLeft - r_numStepsLeft
        self.right_accumulator +=  numStepsRight - r_numStepsRight
        #self.up_accumulator = numStepsUP - r_numStepsUP
        
        r_numStepsLeft = r_numStepsLeft +leftoff
        r_numStepsRight = r_numStepsRight +rightoff
        
        #determine max
        steps = abs(r_numStepsLeft), abs(r_numStepsRight), abs(r_numStepsUP)
        maxSteps = max(steps)
        
        #prep batch/command
       
        left_dir,right_dir,up_dir = self.createDirs(deltaLeft, deltaRight, deltaUP)    
        batch = self.createBatch(maxSteps, r_numStepsLeft, r_numStepsRight, r_numStepsUP, left_dir, right_dir, up_dir)       
        self.currentPos = command[0], command[1], command[2]
        batches = []
        batches.append(batch)
        return batches

    def createBatch(self, nrSteps, r_numStepsLeft, r_numStepsRight, r_numStepsUP, left_dir, right_dir, up_dir):
        a_numStepsLeft = 0
        a_numStepsRight = 0
        a_numStepsUP = 0
        batch = []    
        for st in range(int(nrSteps)):
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
        return batch

    def createDirs(self, deltaLeft, deltaRight, deltaUP):
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
        return (left_dir,right_dir,up_dir)    

if __name__ == '__main__':
    basepath = "generated_data/testies/"
    order_id = "testies"
    driver = Driver(basepath+order_id)
    linenr = 0
    start = 0
    driver.run(int(linenr),start)        