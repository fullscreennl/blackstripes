import numpy
import Image


class WebBasedPreviews:


    def __init__(self,image_name):
        self.image_name = image_name
        self.gen()
        self.combine()
        
    def gen(self):
        self.level_data = []
        im = Image.open(self.image_name).convert("L")
        im = im.resize((250,250),Image.ANTIALIAS)
        w,h = im.size
        im_arr = numpy.asarray(im, numpy.uint8)

        for image in range(51):
            a = (im_arr > (image*(255/50.0))) * 255
            a = numpy.uint8(a)
            self.level_data.append(a)


    def combine(self,choice=25):

        centers = [15,20,25,30,35]
        contrast_settings = [1,2,3,4,5]

        for c in centers:
            for cs in contrast_settings:

                levels = [0]
                levels.append(c-cs*3)
                levels.append(c-cs*2)
                levels.append(int(round(c-cs/2.0)))
                levels.append(int(round(c+cs/2.0)))
                levels.append(c+cs*2)
                levels.append(c+cs*3)

                my_level_data = []

                for l in levels:
                    my_level_data.append(self.level_data[l])

                a = 0
                counter = 0
                for data in my_level_data:
                    ld = (data == 0) *1
                    counter += 1
                    a = a + ld

                colors = [

                    (255,255,255),
                    (220,220,220),
                    (170,170,170),
                    (255,100,100),
                    (255,0,0),
                    (80,30,30),
                    (0,0,0)

                ]

                _r = 0
                _g = 0
                _b = 0
                counter = 0
                for r in levels:
                    __r = (a == counter) * colors[counter][0]
                    __g = (a == counter) * colors[counter][1]
                    __b = (a == counter) * colors[counter][2]

                    _r = _r + __r
                    _g = _g + __g
                    _b = _b + __b

                    counter += 1

                a = numpy.dstack((_r,_g,_b))

                a = numpy.uint8(a)
                t = Image.fromarray(a)
                t.save(str(c)+"_"+str(cs)+".png")


if __name__ == "__main__":
    WebBasedPreviews("miles.jpg")



