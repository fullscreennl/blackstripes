import numpy as np
import Image

colors = np.array([ [0,0,0],
                    [80,30,30],
                    [255,0,0],
                    [255,100,100],
                    [170,170,170],
                    [220,220,220],
                    [255,255,255]])

levels = [  ([0, 0, 46, 82, 136, 172],"_0"),
            ([10, 28, 55, 73, 100, 118],"_1"),
            ([37, 46, 60, 69, 82, 91],"_2"),
            ([20, 56, 110, 146, 200, 236],"_3"),
            ([74, 92, 119, 137, 164, 182],"_4"),
            ([101, 110, 124, 133, 146, 155],"_5"),
            ([84, 120, 174, 210, 255, 255],"_6"),
            ([138, 156, 183, 201, 228, 246],"_7"),
            ([165, 174, 188, 197, 210, 219],"_8")]


mask_images = ( "masks/black_even_mask.png","masks/black_odd_mask.png",
                "masks/red_even_mask.png","masks/red_odd_mask.png",
                "masks/grey_even_mask.png","masks/grey_odd_mask.png")

masks = []
for m in mask_images:
    im = Image.open("masks/black_even_mask.png").convert("L")
    masks.append(np.asarray(im))



