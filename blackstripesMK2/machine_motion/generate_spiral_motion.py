if __name__ == "__main__":

    import os

    from machine_settings import *
    from Generator import Generator
    from Easer import Easer
    from Model import Blackstripes_MKII
    from SmallSpiral import Spiral

    m = Blackstripes_MKII()
    Spiral(m,MARKER_NIB_SIZE_MM)
    Generator(m,"data.tmp")
    Easer("data.tmp",output_filename ="spiral")
    os.remove("data.tmp")

