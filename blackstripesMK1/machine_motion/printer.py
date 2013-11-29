import time
 
class Printer:
    #drivers should work untill 400kHz
    #period is 1.0/400000.0
    #high duration = 1.0/800000.0
    #low duration  = 1.0/800000.0 = 0.00000125
    #MAXDELAY = 0.0005
    MAXDELAY = 500 #cycles in wait loop (BUSY WAIT)
    # 400 khz max MINDELAY = 0.00000125
    #MINDELAY = 0.000002
    MINDELAY = 1 #cycles in wait loop (BUSY WAIT)
    
    EASE_SIZE = 20 #equals 20 mm canvas space
    # tested to work MINDELAY = 0.0001

    
    def calculateDelays(self):
        for i in range(self.EASE_SIZE):
            delay = self.MAXDELAY*( 1 - (float(i)/float(self.EASE_SIZE))) + self.MINDELAY;
            self.delays.append(int(delay))
        self.delays.append(1)
        
        print 'delays',self.delays  
    
    def __init__(self,output_path = ""):
        self.delays = []
        self.output_path = output_path
        self.rawoutput = open(self.output_path+'layer0.dat', 'w')
        self.layercounter = 0
        L_clk = 5   #header pin 5 
        L_dir = 3   #header pin 3 
        R_dir = 7   #header pin 7
        R_clk  = 8   #header pin 8
        Solenoid = 10  #header pin 10
        self.leftchannel = [L_clk, L_dir]
        self.rightchannel = [R_clk,R_dir]
        self.printerhead = [Solenoid]
        self.lastdirs =[0,0]
        self.calculateDelays()  
        
    def saveLayer(self):
        self.finalize();
        self.layercounter +=1
        self.rawoutput = open(self.output_path+'layer'+str(self.layercounter)+'.dat', 'w')

    def printBatch(self, cmds, currentindex, totallength):
        if((totallength - currentindex) < currentindex):
            delta = totallength - currentindex
        else:
            delta = currentindex
        # currentindex is which mm in a total line of length totallength
        # cmds is all python generated from json stepping instructions to move a single mm on canvas
        
        # for long sweeps between layers speed remains low there is only one instruction currentindex = 0 for the whole sweep
        # create exception putting delta over ease size to max transport speed long generated sweep have manu more cmds than STEP_PER_MM value
        # 12.5 mm linespacing * 42.55 steps per mm is cmds generated btween lines these should be low speed to its the treshold to go fast or not
        #print 'len(cmds)',len(cmds)

        gencmds = len(cmds)
        CMDCOUNT=0
        if gencmds > 1000: #14*43 tunred out to be to low
            #all generated transison steps
            for cmd in cmds:
                if((gencmds - CMDCOUNT) < CMDCOUNT):
                    delta = int((gencmds - CMDCOUNT)/43.0)
                else:
                    delta = int(CMDCOUNT/43.0)
                CMDCOUNT = CMDCOUNT + 1
                self.logCmdsToFile(cmd, delta)
        else:
            for cmd in cmds:
                self.logCmdsToFile(cmd, delta)  
    
    def logCmdsToFile(self,cmd,delta):
        self.rawoutput.write(str(cmd[0])+','+str(cmd[1])+','+str(cmd[2])+','+str(delta)+'\n')
        
    def finalize(self):
        self.rawoutput.close() 
    
