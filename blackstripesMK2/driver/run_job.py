import os
from subprocess import Popen

os.chdir(os.getcwd())

if os.path.isfile("spiral.bin"):
    print "motiondata found.."
else:
    print "ERROR : motiondata not found"
    os._exit(0)

if os.path.isfile("image.bin"):
    print "image found.."
else:
    print "ERROR : image not found"
    os._exit(0)

raw_input("start drawing?")

Popen(["./driver", "spiral.bin","image.bin"])