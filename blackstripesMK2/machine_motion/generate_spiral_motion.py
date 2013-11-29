if __name__ == "__main__":

    import os

    from machine_settings import *
    from generator import Generator
    from easer import Easer
    from model import Blackstripes_MKII
    #small spiral fits on cardboard panel
    from smallspiral import SmallSpiral
    from spiral import Spiral

    m = Blackstripes_MKII()
    Spiral(m,MARKER_NIB_SIZE_MM)
    Generator(m,"data.tmp")
    Easer("data.tmp",output_filename ="spiral")
    os.remove("data.tmp")

