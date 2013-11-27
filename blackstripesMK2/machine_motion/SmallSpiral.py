import math
from machine_settings import *

class Spiral:


	def __init__(self,s,nib_size_mm=0.5):
		#self.radius = 524.0
		#self.spiral_start = (1023.9980908, 499.085449876)
		self.radius = 489.0
		self.spiral_start = (989.0 ,500.0)
		self.center = (500,500)
		self.s = s
		self.s.setEven(0)
		self.s.setBoundsFunction(self.inCircle)
		self.nib_size_mm = nib_size_mm	
		self.generate()

	def inCircle(self,x, y):
		xnull = CENTER - 500.0
		ynull = SHOULDER_HEIGHT+CANVAS_Y
		center_x, center_y = (500 + xnull,500 + ynull)
		#radius = 500 
		radius = 465
		square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
		return int(square_dist <= radius ** 2)

	def toradians(self,deg):
		return deg * math.pi/180.0

	def sign(self):
		import json
		f = open("assets/signature_data.json","r") 
		data = json.loads(f.read())

		self.s.releaseMoveMode()

		x_offset,y_offset = data[0]
		for pos in data:
			x,y = pos
			#x = (x - x_offset ) / 10.0 + 810
			#y = (y - y_offset ) / 10.0 + 920
			x = (x - x_offset ) / 10.0 + 790
			y = (y - y_offset ) / 10.0 + 917
			a1,a2 = self.s.getStateFromXYonCanvas(x,y)
			xy = self.s.appendAngles(a1,a2)

		return xy

	def generate(self):	
	
		self.s.setMoveMode()
		self.s.drawLineFromTo(HOME, self.spiral_start,-1,beginspeed=0,endspeed=0)
		self.s.releaseMoveMode()
		
		num_cycles = int(round((self.radius+1.0)/self.nib_size_mm))
		
		sp = 0
		ease_speed = 0
		cycle_count = 0
		
		numiterations = 3600*num_cycles
		
		self.s.beginLine(0,483,1000)

		for ang in range(numiterations):
		
			x = math.cos(float(self.toradians(ang))/10.0) * self.radius + self.center[0]
			y = math.sin(float(self.toradians(ang))/10.0) * self.radius + self.center[1]
			
			self.radius -= (self.nib_size_mm/3600.0)
			
			if ang/3600 % 2 == 0:
				self.s.setEven(1)
			else:
				self.s.setEven(0)

			if ang%3600 == 0:
				cycle_count += 1
				#if cycle_count ==  128:
				if cycle_count ==  119:
					self.s.endLine(387,200000)
					self.s.beginLine(387,387,5)

			self.s.drawStateFromXYonCanvas(x,y)
		
		self.s.endLine(0,500)

		self.s.setMoveMode()
		#self.s.drawLineFromTo((x,y),(810,920),-1)
		self.s.drawLineFromTo((x,y),(790,917),-1)
		self.s.releaseMoveMode()

		self.s.beginLine(0,35,500)
		x,y = self.sign()
		self.s.endLine(0,500)

		self.s.setMoveMode()
		self.s.drawLineFromTo((x,y),HOME,-1)
		self.s.releaseMoveMode()
		
if __name__ == "__main__":
	pass
	



	
	
	
	
	
	
	
	
	
	
	