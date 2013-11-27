if __name__ == "__main__":

    import os

    from machine_settings import *
    from Generator import Generator
    from Easer import Easer
    from Model import Blackstripes_MKII
    from ScanLines import ScanLines

    m = Blackstripes_MKII()
    ScanLines(m,MARKER_NIB_SIZE_MM)
    Generator(m,"data.tmp")
    Easer("data.tmp",output_filename ="scanlines")
    os.remove("data.tmp")
