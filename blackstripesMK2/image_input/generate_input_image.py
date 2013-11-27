import Image
import numpy
import struct
import os


class LevelThresholds:

	def __init__(self,filename):
		try:
			str_levels = filename.split("_")[:-1]
			if len(str_levels) == 0:
				raise Exception("bad filename")
			self.levels = []
			for l in str_levels:
				self.levels.append(int(l))
		except:
			self.levels = [217, 180, 144, 108, 72, 36]


	def get(self):
		return self.levels




class Preview:

	def __init__(self):
		pass


	def generate(self):
		W = 200
		H = 200
		for image in os.listdir("./input"):
			if ".png" in image or ".jpg" in image:

				print "processing preview :",image

				levels = LevelThresholds(image).get()

				im = Image.open("./input/"+image)
				w,h = im.size

				if w < h:
					offset = int(round((h-w)/2.0))
					im = im.crop((0,offset,w,w+offset))
				else:
					offset = int(round((w-h)/2.0))
					im = im.crop((offset,0,h+offset,h))

				_s = int(W),int(H)
				im = im.resize(_s,Image.BICUBIC)

				counter = 0
				row = 0
				col = 0
				preview = im.convert("RGB")
				preview_data = numpy.asarray(preview)
				preview_data.flags.writeable = True

				im = im.convert("L")

				I = numpy.asarray(im)
				I = I.flatten()
				outputname = image.split(".")[0]
				for p in I:
					if p > levels[0]:
						r,g,b = 255,255,255
					elif p > levels[1]:
						r,g,b = 220,220,220
					elif p > levels[2]:
						r,g,b = 170,170,170
					elif p > levels[3]:
						r,g,b = 255,100,100
					elif p > levels[4]:
						r,g,b = 255,0,0
					elif p > levels[5]:
						r,g,b = 80,30,30
					else:
						r,g,b = 0,0,0

					preview_data[row][col][0] = r
					preview_data[row][col][1] = g
					preview_data[row][col][2] = b

					counter += 1
					col += 1
					if counter%(W) == 0:
						row += 1
						col = 0

				t = Image.fromarray(preview_data)

				mask = Image.open("assets/mask.png")
				t.paste(mask,(0,0),mask)

				t.save("./output/preview_"+outputname+".png",)

class BlackstripesData:

	def __init__(self):
		pass

	def generate(self):
		W = 1000
		H = 1000
		for image in os.listdir("./input"):
			if ".png" in image or ".jpg" in image:

				print "processing :",image

				levels = LevelThresholds(image).get()

				im = Image.open("./input/"+image)
				w,h = im.size

				if w < h:
					offset = int(round((h-w)/2.0))
					im = im.crop((0,offset,w,w+offset))
				else:
					offset = int(round((w-h)/2.0))
					im = im.crop((offset,0,h+offset,h))

				_s = int(W),int(H)
				im = im.resize(_s,Image.BICUBIC)
				im = im.convert("L")

				I = numpy.asarray(im)
				I = I.flatten()
				outputname = image.split(".")[0]
				f = open("./output/"+outputname+".bsi",'wb')

				for l in levels:
					SAMPLE = struct.pack('B',l)
					f.write(SAMPLE)

				for p in I:
					SAMPLE = struct.pack('B',p)
					f.write(SAMPLE)

				f.close()



if __name__ == "__main__":
	Preview().generate()
	BlackstripesData().generate()






