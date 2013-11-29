import math
from machine_settings import *
import baseSpiral

class Spiral(baseSpiral.BaseSpiral):

    def configure(self):
        self.radius = 524.0
        self.spiral_start = (1023.9980908, 499.085449876)
        self.bounding_radius = 500
        self.signature_pos = (810,920)
        self.max_cycles = 128

        
if __name__ == "__main__":
    pass
    
