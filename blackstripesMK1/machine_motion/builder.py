import math
import json
import os
import time
from PIL import Image as Image
#import Image
#import ImageDraw

from machine_settings import *



##### top level functions #####

def lengthFromPos(x,y):

    ldx = x-LEFT_STEPPER_POS[0] 
    ldy = y-LEFT_STEPPER_POS[1]
    ll = math.sqrt((ldx*ldx)+(ldy*ldy)) 

    rdx = x-RIGHT_STEPPER_POS[0] 
    rdy = y-RIGHT_STEPPER_POS[1]
    rl = math.sqrt((rdx*rdx)+(rdy*rdy)) 
    
    return (ll,rl)

def posFromLengths(l1,l2):        
    d = float(LEFT_STEPPER_POS[0] + RIGHT_STEPPER_POS[0])
    m = float(l1) + float(l2)
    n = float(l1) - float(l2)
    if n < 0:
        n = n * -1

    if d > m:
        return None

    #Circle are contained within each other
    if d < n:
        return None

    #Circles are the same
    if d == 0 and l1 == l2:
        return None
        
    a = (l1*l1 - l2*l2 + d*d) / (2*d)

    #Solve for h
    h = math.sqrt(l1*l1 - a*a);

    #Calculate point p, where the line through the circle intersection points crosses the line between the circle centers.  

    x = LEFT_STEPPER_POS[0] + (a/d)*( RIGHT_STEPPER_POS[0] - LEFT_STEPPER_POS[0] )
    y = LEFT_STEPPER_POS[1] + (a/d)*( RIGHT_STEPPER_POS[1] - LEFT_STEPPER_POS[1] )

    #1 soln , circles are touching
    if d == l1 + l2:
        return (x,y)


    #2solns 

    p1x = x + ( h/d ) * ( RIGHT_STEPPER_POS[1] - LEFT_STEPPER_POS[1] )
    p1y = y - ( h/d ) * ( RIGHT_STEPPER_POS[0] - LEFT_STEPPER_POS[0] )

    p2x = x - ( h/d ) * ( RIGHT_STEPPER_POS[1] - LEFT_STEPPER_POS[1] )
    p2y = y + ( h/d ) * ( RIGHT_STEPPER_POS[0] - LEFT_STEPPER_POS[0] )
    
    if p1y < 0:
        return (p2x, p2y)
    else:
        return (p1x, p1y)
        


class Builder:

    def __init__(self,input_image):
        #self.jabname = input_image
        print 'input_image>>>>>>>>>>>>'+input_image
        self.input_image = Image.open(input_image)
        self.input_image = self.input_image.resize(CANVAS_SIZE,Image.BICUBIC)
        
    def doDraw(self,pos3,**kwargs):
        pos3 = posFromLengths(pos3[0],pos3[1])
        x,y = pos3
        x = int(math.floor(x))-g_Offset
        y = int(math.floor(y))-g_Offset
        try:
            level = self.input_image.getpixel((x,y))[0]
        except:
            return -1 #different handling per layer
        if pos3:
            if level < kwargs['level']:
                return 1
        return 0
        
    def buildLayerData(self,filename,separated,levels):
    
        ####################################################################
        #first non lineair hi contrast division 200, 100, 50, 25
        #levels = [200,100,50,25]
        #levels = [150,75,50,25]
        #levels = []
        #levels_strings = self.jabname.split("_")[1:]
        #for l in levels_strings:
            #levels.append(int(l))
        #255/5 = 51.2 => 4*51.2 = 204.8, *3 = 153.6, *2 - 102.4, *1 51.2 => 205, 154, 102, 51
        #levels = [204,154,102,51]
        #curved bars (left)
        
        
        comp = Composition()
        print 'generating layer 1'
        layer1 = Layer()
        for offset in range(CURVED_ITERATIONS):
            line = Line()
            offset = offset*LINE_SPACING
            bl1,bl2 = lengthFromPos(-PADDING + offset, g_Offset)
            el1,el2 = lengthFromPos(g_MachineWidth-g_Offset, g_MachineWidth +PADDING- offset)
            dot_found = False
            for d in range(int(round(el1 - bl1))):
                x,y = posFromLengths(bl1 + d, el2)
                if x > g_Offset and y < g_MachineWidth - g_Offset:
                    up = self.doDraw((bl1 + d, el2), mode="l", line=0,
                                     level=levels[0], color=(0,0,0,255))
                    if up > -1:
                        line.addDot((bl1+d,el2,up))
                    if up==1:
                        dot_found = True
            if dot_found:
                layer1.addLine(line)
        layer1.addLine("layer1 end")        
        comp.addLayer(layer1)
        
        ####################################################################
        #curved bars (right)
        print 'generating layer 2'
        layer2 = Layer()
        
        for offset in range(CURVED_ITERATIONS):
            line = Line()
            offset = offset*LINE_SPACING
            bl1,bl2 = lengthFromPos(g_MachineWidth+PADDING - offset,g_Offset)
            el1,el2 = lengthFromPos(g_Offset,g_MachineWidth+PADDING- offset)
            dot_found = False
            for d in range(int(round(el2-bl2))):
                x,y = posFromLengths(bl1,bl2+d)
                if x > g_Offset and y < g_MachineWidth - g_Offset:
                    up = self.doDraw((bl1,bl2+d), mode="l", line=0, 
                                     level=levels[1], color=(0,0,0,255))
                    if up > -1:
                        line.addDot((bl1,bl2+d,up))
                    if up==1:
                        dot_found = True
            if dot_found:
                layer2.addLine(line)
        layer2.addLine("layer2 end")        
        comp.addLayer(layer2)
        
        ####################################################################
        #straight horizontal bars
        print 'generating layer 3'  
        layer3 = Layer()
        
        #10 cm te laat aan de bovenkant
        # 100/LINE_SPACING = extra iterations
        EXTRA_ITERATIONS = int(round(100.0 / LINE_SPACING))
        
        for offset in range(STRAIGHT_ITERATIONS + EXTRA_ITERATIONS):
            line = Line()
            offset = offset*LINE_SPACING - 100.0
            #startpoint
            x,y = g_Offset,g_Offset + offset
            l,r = lengthFromPos(x,y)
            #endpoint
            x2,y2 = g_MachineWidth-g_Offset,g_Offset+offset
            l2,r2 = lengthFromPos(x2,y2)
            dot_found = False
            for d in range(int(round(r - r2))):
                x,y = posFromLengths(r-d, l+d)
                if x > g_Offset and y < g_MachineWidth and y > g_Offset:
                    up = self.doDraw((r-d,l+d),mode="l",line=0, level=levels[2],color=(0,0,0,255))
                    if up == -1:
                        up = 0
                    line.addDot((r-d,l+d,up))
                    if up==1:
                        dot_found = True
            if dot_found:
                layer3.addLine(line)
        layer3.addLine("layer3 end")        
        comp.addLayer(layer3)
        
        ####################################################################
        #straight vertical bars
        
        print 'generating layer 4'
        layer4 = Layer()
        
        for offset in range(STRAIGHT_ITERATIONS):
            line = Line()
            offset = offset*LINE_SPACING
            #startpoint
            x,y = g_Offset+offset,g_Offset
            l,r = lengthFromPos(x,y)
            #endpoint
            x2,y2 = g_Offset+offset,g_MachineWidth - g_Offset
            l2,r2 = lengthFromPos(x2,y2)
            dot_found = False
            #print 'calculated range: ',round(r2-r),round(l2-l)
            for d in range(max(int(round(r2-r)),int(round(l2-l)))):
                x,y = posFromLengths(r+d, l+d)
                if x > g_Offset and y < (g_MachineWidth - g_Offset) and x < (g_MachineWidth - g_Offset):
                    up = self.doDraw((r+d, l+d),mode="l",line=0, level=levels[3],color=(0,0,0,255))
                    if up == -1:
                        up = 0
                    line.addDot((r+d, l+d,up))
                    if up==1:
                        dot_found = True
            if dot_found:
                layer4.addLine(line)
        
        l,r = lengthFromPos(g_Offset + CANVAS_SIZE[0]-180,g_Offset+CANVAS_SIZE[1]+50)
        line = Line()
        line.addDot((l,r,up))
        layer4.addLine(line)
        layer4.addLine("layer4 end")
        comp.addLayer(layer4)
        #if separated==0:
        comp.save(filename+".json")
        #else:
        comp.saveToJsonBlob(filename+"_sep.json")


#builder objects

class Composition:
    def __init__(self):
        self.layers = []
    
    def addLayer(self,layer):
        self.layers.append(layer)
    
    def log(self):
        for l in self.layers:
            print "Layer : ",l
            l.log()
    
    def toData(self):
        data = []
        for l in self.layers:
            data.append(l.toData())
        return data
    
    def save(self,filename):
        f = open(filename,"w")
        f.write(json.dumps(self.toData()))
        f.close()

    def saveToJsonBlob(self,filename):
        f =open(filename,"w")
        for layer in self.layers:
            for line in layer.data:
                # done in save assuming save is called before savetojsonblob 
                f.write(json.dumps(line)+"\n")
        f.close()                   
        
class Layer:
    def __init__(self):
        self.lines = []
        self.data = []
    def log(self):
        for line in self.lines:
            print "\tLine : ",line
            line.log()
    def toData(self):
        #data = []
        counter = 0
        _end = None
        for l in self.lines:
            try:
                d = l.toData()
            except:
                d = l
                self.data.append(d)
                continue
            if counter%2 == 0:
                d.reverse()
            if len(d) > 0:
                # add in / out points
                first = d[:1][0]
                last = d[-1:][0]
                first = first[0],first[1],2
                last = last[0],last[1],3
                d.append(last)
                d.insert(0,first)
                self.data.append(d)
            counter += 1
        return self.data
    def addLine(self,line):
        self.lines.append(line)
        
class Line:
    def __init__(self):
        self.dots = []
    def log(self):
        print "\t\t",len(self.dots)
    def toData(self):
        return self.dots
    def addDot(self,dot):
        if dot[2] != None:
            dot = int(round(dot[0])), int(round(dot[1])) , dot[2]
            self.dots.append(dot)



class OrderProcessor:

    def __init__(self,order):
        self.filename = order = str(order)
        data = order.split(".")[0].split("_")
        self.orderid = data[0]
        self.basepath = "generated_data/"+self.orderid+"/"
        self.levels = []
        levels_strings = data[1:]
        for l in levels_strings:
            self.levels.append(int(l))
            
        if len(self.levels) < 4:
            print "to few levels!"
            os._exit(1)
        if len(self.levels) > 4:
            print "to many levels!"
            os._exit(1)
        if ".png" not in self.filename:
            print "no .png file!"
            os._exit(1)


    def getFileName(self):
        return self.filename

    def getOrderId(self):
        return self.orderid
        
    def getLevels(self):
        return self.levels
        
    def getbasepath(self):
        return self.basepath


if __name__ == '__main__':
    order = 'testies_210_180_120_50.png'
    job = OrderProcessor(order)
    filename = job.getFileName()
    basepath = job.getbasepath()
    levels = job.getLevels()
    order_id = job.getOrderId() 
    
    try:
        os.makedirs(basepath)
    except:
        pass

    builder = Builder(filename)
    builder.buildLayerData(basepath+order_id,0,levels)        
