import math
import os
import time
import traceback

from machine_settings import *

def posFromElbows(leftelbow,rightelbow):
        
    xleft = leftelbow[0]
    xright = rightelbow[0]
    deltax = xright - xleft
    h1 = leftelbow[1]
    h2 = rightelbow[1]
    deltay = h1 - h2
    
    l1 = l2 = LOWER_ARM_LENGTH
        
    d = math.sqrt(deltax*deltax + deltay*deltay)
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

        
    a = ( l1 * l1 - l2 * l2 + d * d ) / (2 * d);

    #Solve for h
    h = math.sqrt( l1 * l1 - a * a );

    #Calculate point p, where the line through the circle intersection points crosses the line between the circle centers.  

    x = xleft + ( a / d ) * ( xright - xleft );
    y = h2 + ( a / d ) * ( h1 - h2 );

    #1 soln , circles are touching
    if d == l1 + l2:
        return (x,y)


    #2solns    

    p1x = x + ( h / d ) * ( h2 - h1 )
    p1y = y - ( h / d ) * ( xright - xleft )

    p2x = x - ( h / d ) * ( h2 - h1 )
    p2y = y + ( h / d ) * ( xright - xleft )
    
    if p1y > p2y:
        return (p1x,p1y)
    else:
        return (p2x,p2y)
        
def findCircleCircleIntersections(cx0,cy0,radius0,cx1,cy1,radius1):

    # Find the distance between the centers.
    dx = cx0 - cx1;
    dy    = cy0 - cy1;
    dist = math.sqrt(dx * dx + dy * dy);
        
    # See how manhym solutions there are.
    if dist > radius0 + radius1:
        # No solutions, the circles are too far apart.
        return None;
    elif dist < abs(radius0 - radius1):
        #No solutions, one circle contains the other.
        return None;
    elif ((dist == 0) and (radius0 == radius1)):
        # No solutions, the circles coincide.
        return None;
    else:
        # Find a and h.
        a = (radius0 * radius0 - radius1 * radius1 + dist * dist) / (2 * dist);
        h = math.sqrt(radius0 * radius0 - a * a);

        # Find P2.
        cx2 = cx0 + a * (cx1 - cx0) / dist;
        cy2 = cy0 + a * (cy1 - cy0) / dist;
        
        # Get the points P3.
        intersection1 = [
                    (cx2 + h * (cy1 - cy0) / dist),
                    (cy2 - h * (cx1 - cx0) / dist)];
                    
        intersection2 = [
                    (cx2 - h * (cy1 - cy0) / dist),
                    (cy2 + h * (cx1 - cx0) / dist)];
        
        # See if we have 1 or 2 solutions.
        if (dist == radius0 + radius1): 
            return intersection1;
        else:
            return [intersection1,intersection2]

class Blackstripes_MKII:

    def __init__(self):
        self.even = 0
        
        offset = SHOULDER_DIST / 2.0;
                
        self.leftshoulder = left_axis = LEFT_SHOULDER_POS
        self.rightshoulder = right_axis = RIGHT_SHOULDER_POS
        
        self.angles = []
        self.movemode = 0

    #inBoundsFunction should return false if out of bounds
    def setBoundsFunction(self,inBoundsFunction):
        self.inBounds = inBoundsFunction

    def setMoveMode(self):
        self.movemode = 1

    def releaseMoveMode(self):
        self.movemode = 0
        
    def setEven(self,is_even):
        self.even = is_even
            
    def getAngles(self):
        return self.angles
        
    def radians(self,deg):
        return deg * (math.pi/180.0)

    def calculateMarkerPositions(self,left,right):
        
        left = left - 90.0 - 180
        right = -right + 90.0
        
        left = round(left / ANGLE_PER_STEP) * ANGLE_PER_STEP
        right = round(right / ANGLE_PER_STEP) * ANGLE_PER_STEP

        left_axis = self.leftshoulder
        right_axis = self.rightshoulder
        
        lx = math.cos(self.radians(left)) * UPPER_ARM_LENGTH + left_axis[0];
        ly = math.sin(self.radians(left)) * UPPER_ARM_LENGTH + left_axis[1];
        
        rx = math.cos(self.radians(right)) * UPPER_ARM_LENGTH + right_axis[0];
        ry = math.sin(self.radians(right)) * UPPER_ARM_LENGTH + right_axis[1];
        
        markerx, markery =  posFromElbows((lx,ly),(rx,ry))
        
        angle_in_rad_left = math.atan2(markery - ly, markerx - lx)

        mx1 = math.cos(angle_in_rad_left) * (LOWER_ARM_LENGTH + EXENSION1) + lx;
        my1 = math.sin(angle_in_rad_left) * (LOWER_ARM_LENGTH + EXENSION1) + ly;
        
        mx2 = math.cos(angle_in_rad_left) * (LOWER_ARM_LENGTH + EXENSION2) + lx;
        my2 = math.sin(angle_in_rad_left) * (LOWER_ARM_LENGTH + EXENSION2) + ly;

        offset_3rd_marker = 1.04719755     #60 deg in radians
        bearing_space = 28.0        #bearings are 28mm diam.
        
        mx3 = math.cos(offset_3rd_marker+angle_in_rad_left) * bearing_space + mx1;
        my3 = math.sin(offset_3rd_marker+angle_in_rad_left) * bearing_space + my1;

        return (mx1,my1,mx2,my2,mx3,my3)

    def appendAngles(self,left,right):

        leftval = left
        rightval = right

        mx1,my1,mx2,my2,mx3,my3 = self.calculateMarkerPositions(left,right)
    
        draw1 = 0
        draw2 = 0
        draw3 = 2
                
        self.angles.append((leftval,rightval,draw1,draw2,draw3,0,0,2,0))
        return self.getXYonCanvas(mx1,my1)

    def appendAnglesWithMarkerProfile(self,left,right,marker_profile=(2,2,2)):

        leftval = left
        rightval = right

        mx1,my1,mx2,my2,mx3,my3 = self.calculateMarkerPositions(left,right)

        if not self.movemode:
            draw1,draw2,draw3 = marker_profile
            self.angles.append((leftval,rightval,draw1,draw2,draw3,draw1,draw2,draw3,0))
        else:
            self.angles.append((leftval,rightval,0,0,0,0,0,0,0))

        return self.getXYonCanvas(mx1,my1)

    def drawWithAngles(self,left, right,draw=0):

        leftval = left
        rightval = right
        
        mx1,my1,mx2,my2,mx3,my3 = self.calculateMarkerPositions(left,right)
                
        layer1_level = (int(round(mx1-self.xnull)), int(round(my1-self.ynull)))
        layer2_level = (int(round(mx2-self.xnull)), int(round(my2-self.ynull)))
        layer3_level = (int(round(mx3-self.xnull)), int(round(my3-self.ynull)))
        
        level1 = 999
        level2 = 999
        level3 = 999
                
        if not self.movemode:
            draw1 = self.getPixelIndexFromXY(layer1_level)
            draw2 = self.getPixelIndexFromXY(layer2_level)
            draw3 = self.getPixelIndexFromXY(layer3_level)


            self.angles.append((leftval,
                                rightval,

                                draw1,
                                draw2,
                                draw3,

                                self.inBounds(mx1,my1),
                                self.inBounds(mx2,my2),
                                self.inBounds(mx3,my3),

                                self.even))
        else:

            draw1 = self.getPixelIndexFromXY(layer1_level)
            draw2 = self.getPixelIndexFromXY(layer2_level)
            draw3 = self.getPixelIndexFromXY(layer3_level)


            self.angles.append((leftval,
                                rightval,

                                draw1,
                                draw2,
                                draw3,

                                0,
                                0,
                                0,

                                self.even))


        return self.getXYonCanvas(mx1,my1)

    def remap(self, x, y):
        # output should be 0 to 1000
        # input can be 100 to 900
        offset = (1000 - (1000.0*LOOKUP_CANVAS_BITMAP_SIZE))/2.0
        x = round((x-offset)*1000.0/(1000.0*LOOKUP_CANVAS_BITMAP_SIZE))
        y = round((y-offset)*1000.0/(1000.0*LOOKUP_CANVAS_BITMAP_SIZE)) 
        return (x,y)

    def getPixelIndexFromXY(self,xy):
        x,y = xy
        x,y = self.remap(x,y)
        if x > 999 or y > 999 or x < 0 or y < 0:
            #print xy
            #first pixel out of bounds
            #can still be encoded as unsigned long
            return 1000000
        w = 1000
        h = 1000
        return int(y*w + x)
        
    def mark(self,x,y):
        m = MARKER_NIB_SIZE / 2.0
        return (x-m,y-m,x+m,y+m)
    
    def getXYonCanvas(self,x,y):
        xnull = CENTER - 500.0
        ynull = SHOULDER_HEIGHT+CANVAS_Y
        return x-xnull,y-ynull
    
    def drawStateFromXYonCanvas(self,x,y):
        self.xnull = CENTER - 500.0
        self.ynull = SHOULDER_HEIGHT+CANVAS_Y
        return self.drawStateFromXY(self.xnull+x,self.ynull+y)

    def getStateFromXYonCanvas(self,x,y):
        self.xnull = CENTER - 500.0
        self.ynull = SHOULDER_HEIGHT+CANVAS_Y
        #mode = 3 prevents appending to angles
        return self.drawStateFromXY(self.xnull+x,self.ynull+y,mode=3)
        
    def beginLine(self,begin_speed,target_speed,numsteps):
        self.angles.append(("BEGIN_LINE",begin_speed,target_speed,numsteps))
    
    def endLine(self,target_speed,numsteps):
        self.angles.append(("END_LINE",target_speed,numsteps))
        
    def drawStateFromXY(self,x,y,mode=1):
    
        lsx, lsy = self.leftshoulder
        rsx, rsy = self.rightshoulder
        
        #angle_in_degrees_left = math.atan2(y - lsy, x - lsx)
        
        leftpoints = findCircleCircleIntersections(x,y,LOWER_ARM_LENGTH + EXENSION1,lsx,lsy,UPPER_ARM_LENGTH)
        if len(leftpoints) > 1:
            if leftpoints[0][0] < leftpoints[1][0]:
                leftelbow = leftpoints[0]
            else:
                leftelbow = leftpoints[1]
                
        x2,y2 = leftelbow
        angle_in_degrees_left = math.atan2(y2 - lsy, x2 - lsx) * 180.0 / math.pi
        angle_in_rad_left = math.atan2(y - y2, x - x2)
        
        mx = math.cos(angle_in_rad_left) * (LOWER_ARM_LENGTH) + x2;
        my = math.sin(angle_in_rad_left) * (LOWER_ARM_LENGTH) + y2;
            
        rightpoints = findCircleCircleIntersections(mx,my,LOWER_ARM_LENGTH,rsx,rsy,UPPER_ARM_LENGTH)
        if len(rightpoints) > 1:
            if rightpoints[0][0] > rightpoints[1][0]:
                rightelbow = rightpoints[0]
            else:
                rightelbow = rightpoints[1]
                
        x2,y2 = rightelbow
        angle_in_degrees_right = math.atan2(y2 - rsy, x2 - rsx) * 180.0 / math.pi
        
        angle_in_degrees_left = angle_in_degrees_left + 90.0 + 180.0 
        angle_in_degrees_left = round(angle_in_degrees_left,4)%360.0
        angle_in_degrees_right = -angle_in_degrees_right + 90.0
        angle_in_degrees_right = round(angle_in_degrees_right,4)%360.0

        if mode == 1:
            self.drawWithAngles(angle_in_degrees_left,angle_in_degrees_right)
        return (angle_in_degrees_left,angle_in_degrees_right)
        
    def write(self,msg):
        print msg
        
    def drawLineFromTo(self,start,end,draw,beginspeed=0,endspeed=0):
        
        numsteps = 1000
        numspaces = float(numsteps-1)
    
        startl, startr = start
        endl, endr = end
    
        deltal = startl-endl
        deltar = startr-endr
        
        leftstep = deltal/numspaces
        rightstep = deltar/numspaces
        
        l = startl
        r = startr
        
        self.beginLine(beginspeed,300,20000)
        
        for step in range(numsteps):
            try:
                self.drawStateFromXYonCanvas(l,r)
            except:
                traceback.print_exc(file=self)
            l = l - leftstep
            r = r - rightstep
            
        self.endLine(endspeed,2000)

    def drawVectorFromTo(self,start,end,draw,beginspeed=0,endspeed=0):
        
        numsteps = 1000
        numspaces = float(numsteps-1)
    
        startl, startr = start
        endl, endr = end
    
        deltal = startl-endl
        deltar = startr-endr
        
        leftstep = deltal/numspaces
        rightstep = deltar/numspaces
        
        l = startl
        r = startr
        
        for step in range(numsteps):
            try:
                a1,a2 = self.getStateFromXYonCanvas(l,r)
                xy = self.appendAnglesWithMarkerProfile(a1,a2,(2,2,2))
            except:
                traceback.print_exc(file=self)
            l = l - leftstep
            r = r - rightstep
            
