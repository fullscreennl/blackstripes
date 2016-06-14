import numpy as np
from PIL import Image as Image
from PIL import ImageStat as ImageStat
from PIL import ImageDraw as ImageDraw
from PIL import ImageFont as ImageFont
from PIL import ImageEnhance as ImageEnhance
import os
import settings
import json
import struct
import string
import shutil

OUPUT_DIR = "www/images/"

class OutputFolder:
    def __init__(self):
        try:
            os.makedirs(OUPUT_DIR) 
        except:
            print "folder OK"


class Response:

    def __init__(self):
        self.data = {}
        self.data['endpoint'] = "http://127.0.0.1:8000/"
        self.data['imagepath'] = "images/"
        self.data['version'] = "v2/"
        self.data['next'] = ""
        self.data['options'] = []
        self.data['imtype'] = ".png"
        self.data['id'] = ""

    def setID(self,anid):
        self.data['id'] = anid

    def setVersion(self,version):
        self.data['version'] = version+"/"

    def setImageType(self,imtype):
        self.data['imtype'] = imtype

    def setNextStep(self,next_url):
        self.data['next'] = next_url

    def addOption(self,iid):
        self.data['options'].append(iid) 

    def produce(self):
        return json.dumps(self.data)


class Cropper:

    W = 500
    H = 500

    def __init__(self,image_name,imid,version):

        self.imid = imid
        self.response = Response()
        self.response.setNextStep("color/")
        self.response.setImageType(".jpg")
        self.response.setVersion(version)
        self.response.setID("crops")

        im = Image.open(image_name)

        try:
            rot = im._getexif()[274]
            if rot == 6:
                im = im.rotate(-90)
        except:
            print "no rotation exif"

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
            iid = self.imid+str(cr_count)
            self.response.addOption(iid)
            cr_count += 1

    def getJSON(self):
        return self.response.produce()


class ColorOptions:

    def __init__(self,image_name,version):
        self.version = version
        self.response = Response()
        self.response.setNextStep("preview/")
        self.response.setVersion(version)
        self.response.setID("colors")
        self.image_name = image_name
        im = Image.open(OUPUT_DIR+image_name+".jpg").convert("L")
        self.numpy_im = np.asarray(im)
        self.color_deltas = np.diff(settings.colors(version),axis=0)
        self.genPresets()

    def genPresets(self):
        for l in settings.levels(self.version):
            self.preview(l)

    def preview(self,levels):
        r = self.numpy_im * 0
        g = self.numpy_im * 0
        b = self.numpy_im * 0
        i = 0
        for l in levels[0]:
            cr = (self.numpy_im > l) * self.color_deltas[i][0]
            cg = (self.numpy_im > l) * self.color_deltas[i][1]
            cb = (self.numpy_im > l) * self.color_deltas[i][2]
            r = r + cr
            g = g + cg
            b = b + cb
            i += 1

        a = np.dstack((r,g,b))
        a = np.uint8(a)
        t = Image.fromarray(a)
        iid = self.image_name+levels[1]
        self.response.addOption(iid)
        t.save(OUPUT_DIR+self.image_name+levels[1]+".png")

    def getJSON(self):
        return self.response.produce()

class Preview:

    def __init__(self,image_name,version):
        self.version = version
        self.response = Response()
        self.response.setNextStep("")
        self.response.setVersion(version)
        self.response.setID("preview")
        self.preview_name = image_name
        color_id = image_name.split("_")[1]
        image_name = image_name.split("_")[0]
        im = Image.open(OUPUT_DIR+image_name+".jpg").convert("L").resize((1000,1000),Image.BICUBIC)
        self.numpy_im = np.asarray(im)
        self.color_deltas = np.diff(settings.colors(version),axis=0)
        cid = int(color_id)
        self.preview(settings.levels(version)[cid])

    def preview(self,levels):
        layers = []
        i = 0
        for l in levels[0]:
            cr = (self.numpy_im > l) * 255
            a = cr + settings.masks(self.version)[i]
            a = np.clip(a,0,255)
            a = np.uint8(a)
            layers.append(a)
            i += 1

        layers.reverse()
        bg = layers[0]
        counter = 1
        for layer in layers[1:]:
            bg = np.where(layer != 255,layer,bg)
            if self.version == "v2":
                if counter < 2:
                    bg[bg==0] = 200
                elif counter < 4:
                    bg[bg==0] = 23
            counter += 1

        r = np.copy(bg)
        g = bg
        b = bg

        r[r==23] = 219

        a = np.dstack((r,g,b))
        a = np.uint8(a)
        t = Image.fromarray(a)
        t = t.resize((500,500),Image.ANTIALIAS)
        self.response.addOption(self.preview_name+"_preview")
        t.save(OUPUT_DIR+self.preview_name+"_preview.png")

    def getJSON(self):
        return self.response.produce()

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

class SketchyColorOptions:

    def __init__(self,image_name,version):
        self.version = version
        self.response = Response()
        self.response.setNextStep("preview/")
        self.response.setVersion(version)
        self.response.setID("colors")
        self.preview_name = image_name
        image_name = image_name
        im = Image.open(OUPUT_DIR+image_name+".jpg").convert("L").resize((1000,1000),Image.BICUBIC)
        self.numpy_im = np.asarray(im)
        self.color_deltas = np.diff(settings.colors(version),axis=0)
        self.generate(OUPUT_DIR+image_name+".jpg")

    def generate(self,image):
        W = 1000
        H = 1000

        if ".png" in image or ".jpg" in image:

            print "processing :",image

            levels = LevelThresholds(image).get()

            im = Image.open(image)
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

            #enhancer = ImageEnhance.Contrast(im)
            #im = enhancer.enhance(2.0)

            I = np.asarray(im)
            I = I.flatten()
            outputname = image.split(".")[0]
            f = open("./image.bsi",'wb')

            for l in levels:
                SAMPLE = struct.pack('B',l)
                f.write(SAMPLE)

            for p in I:
                SAMPLE = struct.pack('B',p)
                f.write(SAMPLE)

            f.close()

            self.preview(image,im)

    def preview(self,image_name,im):
        command = ["./sketchy-driver ./manifest.ini "+OUPUT_DIR+self.preview_name]
        command = string.join(command)

        try:
            bs = os.popen(command, "r")
            status = bs.close()
            if status:
                raise IOError("sketchy_driver failed (status %d)" % status)
        except: 
            raise Exception("oops, sketchy_driver can not create preview")

        for l in range(7):
            iid = self.preview_name+"_"+str(l)
            print iid
            self.response.addOption(iid) 

    def getJSON(self):
        return self.response.produce()


if __name__ == "__main__":
    #OutputFolder()

    # test the simple api
    print Cropper("jimi-hendrix.jpg","imagecrop","v1").getJSON()
    print ColorOptions("imagecrop1","v1").getJSON()
    print Preview("imagecrop1_0","v1").getJSON()

    print Cropper("jimi-hendrix.jpg","imagecrop","v2").getJSON()
    print ColorOptions("imagecrop1","v2").getJSON()
    print Preview("imagecrop1_0","v2").getJSON()





