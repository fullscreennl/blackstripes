import numpy as np
import Image
import os
import settings

OUPUT_DIR = "www/images/"

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


class ColorOptions:

    def __init__(self,image_name):
        self.image_name = image_name
        im = Image.open(OUPUT_DIR+image_name+".jpg").convert("L")
        self.numpy_im = np.asarray(im)
        self.color_deltas = np.diff(settings.colors,axis=0)
        self.genPresets()

    def genPresets(self):
        for l in settings.levels:
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
        t.save(OUPUT_DIR+self.image_name+levels[1]+".png")



class Preview:

    def __init__(self,image_name):
        self.preview_name = image_name
        color_id = image_name.split("_")[1]
        image_name = image_name.split("_")[0]
        im = Image.open(OUPUT_DIR+image_name+".jpg").convert("L").resize((1000,1000),Image.BICUBIC)
        self.numpy_im = np.asarray(im)
        self.color_deltas = np.diff(settings.colors,axis=0)
        cid = int(color_id)
        self.preview(settings.levels[cid])

    def preview(self,levels):
        layers = []
        i = 0
        for l in levels[0]:
            cr = (self.numpy_im > l) * 255
            a = cr + settings.masks[i]
            a = np.clip(a,0,255)
            a = np.uint8(a)
            layers.append(a)
            # t = Image.fromarray(a)
            # t.save(str(i)+"_preview.png")
            i += 1

        layers.reverse()
        bg = layers[0]
        counter = 1
        for layer in layers[1:]:
            bg = np.where(layer != 255,layer,bg)
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
        t.save(OUPUT_DIR+self.preview_name+"_preview.png")


if __name__ == "__main__":
    #OutputFolder()
    Cropper("jimi-hendrix.jpg","image_crop")
    ColorOptions("image_crop1")
    Preview("image_crop1.jpg")



