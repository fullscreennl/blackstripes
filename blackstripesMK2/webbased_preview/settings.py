import numpy as np
from PIL import Image as Image

v2_colors = np.array([ [0,0,0],
                    [80,30,30],
                    [255,0,0],
                    [255,100,100],
                    [170,170,170],
                    [220,220,220],
                    [255,255,255]])

v1_colors = np.array([ [0,0,0],
                       [60,60,60],
                       [120,120,120],
                       [180,180,180],
                       [255,255,255]])

v2_levels = [  ([0, 0, 46, 82, 136, 172],"_0"),
            ([10, 28, 55, 73, 100, 118],"_1"),
            ([37, 46, 60, 69, 82, 91],"_2"),
            ([20, 56, 110, 146, 200, 236],"_3"),
            ([74, 92, 119, 137, 164, 182],"_4"),
            ([101, 110, 124, 133, 146, 155],"_5"),
            ([84, 120, 174, 210, 255, 255],"_6"),
            ([138, 156, 183, 201, 228, 246],"_7"),
            ([165, 174, 188, 197, 210, 219],"_8")]

v1_levels = [  ([0, 46, 82, 136],"_0"),
                ([28, 55, 73, 100],"_1"),
                ([46, 60, 69, 82],"_2"),
                ([56, 110, 146, 200],"_3"),
                ([92, 119, 137, 164],"_4"),
                ([110, 124, 133, 146],"_5"),
                ([120, 174, 210, 255],"_6"),
                ([156, 183, 201, 228],"_7"),
                ([174, 188, 197, 210],"_8")]


v2_mask_images = ( "masks/black_even_mask.png","masks/black_odd_mask.png",
                "masks/red_even_mask.png","masks/red_odd_mask.png",
                "masks/grey_even_mask.png","masks/grey_odd_mask.png")

v1_mask_images = ( "masks/sep_mask_0.png","masks/sep_mask_1.png",
                "masks/sep_mask_3.png","masks/sep_mask_3.png")

v2_masks = []
for m in v2_mask_images:
    im = Image.open(m).convert("L")
    v2_masks.append(np.asarray(im))

v1_masks = []
for m in v1_mask_images:
    im = Image.open(m).convert("L")
    v1_masks.append(np.asarray(im))

versionmap = {}
versionmap['v1'] = (v1_colors,v1_levels,v1_masks)
versionmap['v2'] = (v2_colors,v2_levels,v2_masks)
versionmap['v3'] = (v1_colors,v1_levels,v1_masks)

def colors(version):
    return versionmap[version][0]
def levels(version):
    return versionmap[version][1]
def masks(version):
    return versionmap[version][2]




