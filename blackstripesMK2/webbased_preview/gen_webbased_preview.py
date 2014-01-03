import numpy as np
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


class ColorOptions:

    colors = np.array([[0,0,0],[80,30,30],[255,0,0],[255,100,100],[170,170,170],[220,220,220],[255,255,255]])

    levels = [([0, 0, 46, 82, 136, 172],"1"),
                ([10, 28, 55, 73, 100, 118],"2"),
                ([37, 46, 60, 69, 82, 91],"3"),
                ([20, 56, 110, 146, 200, 236],"4"),
                ([74, 92, 119, 137, 164, 182],"5"),
                ([101, 110, 124, 133, 146, 155],"6"),
                ([84, 120, 174, 210, 255, 255],"7"),
                ([138, 156, 183, 201, 228, 246],"8"),
                ([165, 174, 188, 197, 210, 219],"9")]

    def __init__(self,image_name):
        im = Image.open(image_name).convert("L")
        self.numpy_im = np.asarray(im)
        self.color_deltas = np.diff(self.colors,axis=0)
        self.genPresets()

    def genPresets(self):
        for l in self.levels:
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
        t.save(OUPUT_DIR+levels[1]+".png")



class Preview:

    colors = np.array([[0,0,0],[80,30,30],[255,0,0],[255,100,100],[170,170,170],[220,220,220],[255,255,255]])

    levels = [([0, 0, 46, 82, 136, 172],"1"),
                ([10, 28, 55, 73, 100, 118],"2"),
                ([37, 46, 60, 69, 82, 91],"3"),
                ([20, 56, 110, 146, 200, 236],"4"),
                ([74, 92, 119, 137, 164, 182],"5"),
                ([101, 110, 124, 133, 146, 155],"6"),
                ([84, 120, 174, 210, 255, 255],"7"),
                ([138, 156, 183, 201, 228, 246],"8"),
                ([165, 174, 188, 197, 210, 219],"9")]

    def __init__(self,image_name):
        im = Image.open(image_name).convert("L").resize((1000,1000),Image.BICUBIC)
        self.numpy_im = np.asarray(im)
        self.color_deltas = np.diff(self.colors,axis=0)
        self.loadMasks()
        self.preview(self.levels[1])

    def loadMasks(self):
        self.masks = []
        im = Image.open("masks/black_even_mask.png")
        self.masks.append(np.asarray(im))
        im = Image.open("masks/black_odd_mask.png")
        self.masks.append(np.asarray(im))
        im = Image.open("masks/red_even_mask.png")
        self.masks.append(np.asarray(im))
        im = Image.open("masks/red_odd_mask.png")
        self.masks.append(np.asarray(im))
        im = Image.open("masks/grey_even_mask.png")
        self.masks.append(np.asarray(im))
        im = Image.open("masks/grey_odd_mask.png")
        self.masks.append(np.asarray(im))

    def preview(self,levels):
        layers = []
        r = self.numpy_im * 0
        g = self.numpy_im * 0
        b = self.numpy_im * 0
        i = 0
        for l in levels[0]:
            cr = (self.numpy_im > l) * 255
            cg = (self.numpy_im > l) * 255
            cb = (self.numpy_im > l) * 255
            a = np.dstack((cr,cg,cb))
            a = a + self.masks[i]
            a = np.clip(a,0,255)
            a = np.uint8(a)
            layers.append(a)
            i += 1

        layers.reverse()
        bg = layers[0]
        for layer in layers[1:]:
            bg = np.where(layer != 255,layer,bg)

        t = Image.fromarray(bg)
        t.save("preview.png")


if __name__ == "__main__":
    OutputFolder()
    Cropper("jimi-hendrix.jpg","image_crop")
    ColorOptions(OUPUT_DIR+"image_crop1.jpg")
    Preview(OUPUT_DIR+"image_crop1.jpg")



