import math
from machine_settings import *

class Generator:

    def write(self,msg):
        print msg

    def __init__(self,s,file_name):

        print "-> translating angles to steps .."
    
        self.f = open(file_name,"w")
    
        self.angles = s.getAngles()
        delta_steps_left = 0
        delta_steps_right = 0
        
        prev_left = 1
        prev_right = 1
                
        for a in self.angles:

            if a[0] == "BEGIN_LINE" or a[0] == "END_LINE":
                self.f.write(str(a)+'\n')
                continue

            if a[0] > 180.0 or a[1] > 180.0:
                print a[0]," : ",a[1]
                raise Exception("ILLEGAL ANGLE 1")
            if a[0] < 0.0 or a[1] < 0.0:
                print a[0]," : ",a[1]
                raise Exception("ILLEGAL ANGLE 2")
            if a[0]+a[1] > 200.0:
                print a[0]+a[1]
                raise Exception("ILLEGAL ANGLE 3")

            # angles translated to steps
            step_l = int(round((a[0]-90.0) / ANGLE_PER_STEP))
            step_r = int(round((a[1]-90.0) / ANGLE_PER_STEP))
                
            delta_steps_left = step_l - prev_left
            delta_steps_right = step_r - prev_right
            marker1 = a[2]
            marker2 = a[3]
            marker3 = a[4]

            d1 = a[5]
            d2 = a[6]
            d3 = a[7]

            even = a[8]

            largest = max(abs(delta_steps_left),abs(delta_steps_right)) 
            
            #create instructions
            
            if delta_steps_left < 0:
                left_inst = [0 for i in range(abs(delta_steps_left))]
            elif delta_steps_left > 0:
                left_inst = [2 for i in range(abs(delta_steps_left))]
            else:
                left_inst = [1 for i in range(abs(delta_steps_left))]
                
            if delta_steps_right < 0:
                right_inst = [0 for i in range(abs(delta_steps_right))]
            elif delta_steps_right > 0:
                right_inst = [2 for i in range(abs(delta_steps_right))]
            else:
                right_inst = [1 for i in range(abs(delta_steps_right))]
        
            right_length = len(right_inst)
            left_length = len(left_inst)
            
            #1 padding shortest set
            
            if right_length > left_length:
                left_inst = spaceArray(left_inst,right_length)
            elif right_length < left_length:
                right_inst = spaceArray(right_inst,left_length)
            
            for inst in range(largest): 
                l = left_inst[inst]
                r = right_inst[inst]
                self.f.write(str(l)+','+str(r)+','+str(marker1)+','+str(marker2)+","+str(marker3)+","+str(d1)+","+str(d2)+","+str(d3)+","+str(even)+",#"+'\n')
                
            
            prev_left = step_l
            prev_right = step_r
            
        self.f.close()
                
def spaceArray(arr,target_length):

    new_arr = []
    l = len(arr)
    if l == 0:
        return [1 for i in range(abs(target_length))]
    numspaces = target_length - l
    space_width = float(numspaces) / float(l)
    _space_width = int(math.floor(space_width))
    remain = target_length - (_space_width+1)*l
    space_arr = [1 for i in range(abs(_space_width))]
    remain_arr = [1 for i in range(abs(remain))]

    if _space_width == 0:
        spreadfactor = int(math.floor(float(l) / float(remain)))
        counter = 0
        remaincounter = 0
        for elem in arr:
            counter += 1
            new_arr = new_arr + [elem]
            if counter%spreadfactor == 0 and remaincounter < remain: 
                new_arr = new_arr + [1] 
                remaincounter += 1
                counter =0
    else:   
        for elem in arr:
            new_arr = new_arr + [elem] + space_arr
        new_arr = new_arr + remain_arr

    return new_arr


    
if __name__ == "__main__":
    print spaceArray([2,2,2,2],11)
    print spaceArray([2,2,2,2],20)
    
    
    
    
    
    
    
    
