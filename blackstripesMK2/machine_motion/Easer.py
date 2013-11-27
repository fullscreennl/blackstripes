import Coder
import struct

class Easer:


	def __init__(self,filename,output_filename ="motiondata"):
	
		self.TXT_VERSION = 1
		
		print "-> reading input file .."
	
		f = open(filename,'r')
		lines = f.readlines()
		
		if self.TXT_VERSION:
			outputfile = open(output_filename+".dat","w")
		
		binfile = open(output_filename+".bin","wb")
		
		numsteps = 0
		targetspeed = 0
		beginspeed = 0
		
		currentspeed = 0.0
		
		prev_result = 0
		
		eased_in_array = []
		eased_out_array = []
		resulting_speed_array = []
		
		print "-> easing in .."
		
		for l in lines:
			if l[0] == "(":
				if "BEGIN_LINE" in l:
					beginspeed = int(l.split(",")[1])
					targetspeed = int(l.split(",")[2])
					numsteps = int(l.split(",")[3].replace(")\n",""))
					speed_incr = float(targetspeed-beginspeed)/float(numsteps)
					currentspeed = beginspeed
			else:
				if currentspeed < targetspeed:
					currentspeed += speed_incr
				
				eased_in_array.append(int(round(currentspeed)))
		
		print "-> easing out .."
		
		poscounter = 0L
		for p in reversed(lines):
			if p[0] == "(":
				if "END_LINE" in p:
					beginspeed = int(p.split(",")[1])
					numsteps = int(p.split(",")[2].replace(")\n",""))
					index = len(eased_in_array) - numsteps - 1 - poscounter
					targetspeed = eased_in_array[index]
					speed_decr = float(targetspeed-beginspeed)/float(numsteps)

					currentspeed = beginspeed
			else:
				if currentspeed < targetspeed:
					currentspeed += speed_decr
					
				eased_out_array.append(int(round(currentspeed)))
				
				poscounter += 1
			
		print "-> calculating speed profile .." 
		
		counter = 0L
		error_counter = 0
		for speed in reversed(eased_out_array):
			ease_in_value = eased_in_array[counter]
			ease_out_value = speed
			resulting_speed = min(499,ease_in_value,ease_out_value)
			delta = abs(prev_result - resulting_speed)
			if delta > 1:
				error_counter += 1
				print "WARNING STEPPER JAM ERROR NO.",error_counter ,"DELTA : ",delta,"SPEED ",resulting_speed ,"LINE : ",counter,"IN-OUT",ease_in_value,"-",ease_out_value
			prev_result = resulting_speed
			resulting_speed_array.append(str(resulting_speed))
			counter += 1
		
		
		print "-> encoding binary .."
		
		linecounter = 0L
		for l in lines:
			if l[0] == "(":
				continue
			else:
								
				elems = l.split(",")
				left_engine = int(elems[0])
				right_engine = int(elems[1])
			
				sol1 = int(elems[2])
				sol2 = int(elems[3])
				sol3 = int(elems[4])

				p1 = int(elems[5])
				p2 = int(elems[6])
				p3 = int(elems[7])

				even = int(elems[8])
				speed = int(resulting_speed_array[linecounter])

				SAMPLE = struct.pack('=LLLL',Coder.encode(left_engine,right_engine,p1,p2,p3,even,speed),sol1,sol2,sol3)
				binfile.write(SAMPLE)
				
				if self.TXT_VERSION:
					outputfile.write(l.replace("#",resulting_speed_array[linecounter]))

				linecounter += 1
		
		if self.TXT_VERSION:	
			outputfile.close()
			
		binfile.close()
				
if __name__ == "__main__":
	pass

