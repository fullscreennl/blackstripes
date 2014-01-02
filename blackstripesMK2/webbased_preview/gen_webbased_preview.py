import numpy
import Image
import os

OUPUT_DIR = "output/"

class OutputFolder:
    def __init__(self):
        try:
            os.makedirs(OUPUT_DIR)
        except:
            print "folder OK"


class Cropper:

    W = 500
    H = 500

    def __init__(self,image_name,imid):

        self.imid = imid

        im = Image.open(image_name)
        w,h = im.size

        crops = None

        if w < h:

            zoom = int(round(w * 0.25))
            zoom_2 = int(round(w * 0.125))
            offset_1 = 0
            offset_2 = int(round((h-w)/2.0))
            offset_3 = int(round(h-w))
            crops = [
                (0,offset_1,w,w+offset_1),
                (0,offset_2,w,w+offset_2),
                (0,offset_3,w,w+offset_3),
                #zoomed
                (zoom,offset_1+zoom,w-zoom,w+offset_1-zoom),
                (zoom,offset_2+zoom,w-zoom,w+offset_2-zoom),
                (zoom,offset_3+zoom,w-zoom,w+offset_3-zoom),

                (zoom_2,offset_1+zoom_2,w-zoom_2,w+offset_1-zoom_2),
                (zoom_2,offset_2+zoom_2,w-zoom_2,w+offset_2-zoom_2),
                (zoom_2,offset_3+zoom_2,w-zoom_2,w+offset_3-zoom_2)
            ]

            
        else:

            zoom = int(round(h * 0.25))
            zoom_2 = int(round(h * 0.125))
            offset_1 = 0
            offset_2 = int(round((w-h)/2.0))
            offset_3 = int(round(w-h))
            crops = [
                (offset_1,0,h+offset_1,h),
                (offset_2,0,h+offset_2,h),
                (offset_3,0,h+offset_3,h),
                #zoomed
                (offset_1+zoom,zoom,h+offset_1-zoom,h-zoom),
                (offset_2+zoom,zoom,h+offset_2-zoom,h-zoom),
                (offset_3+zoom,zoom,h+offset_3-zoom,h-zoom),

                (offset_1+zoom_2,zoom_2,h+offset_1-zoom_2,h-zoom_2),
                (offset_2+zoom_2,zoom_2,h+offset_2-zoom_2,h-zoom_2),
                (offset_3+zoom_2,zoom_2,h+offset_3-zoom_2,h-zoom_2)
            ]

        cr_count = 0
        for cr in crops:
            crim = im.crop(cr)
            _s = int(self.W),int(self.H)
            crim = crim.resize(_s,Image.BICUBIC)
            crim.save(OUPUT_DIR+self.imid+str(cr_count)+".jpg")
            cr_count += 1


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

                print str(levels).strip("[]").replace(", ","_")

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
                t.save(OUPUT_DIR+str(c)+"_"+str(cs)+".png")


if __name__ == "__main__":
    OutputFolder()
    #Cropper("photo.jpg","one")
    Cropper("cliff-burton.jpg","image_crop")
    WebBasedPreviews(OUPUT_DIR+"image_crop5.jpg")



