from xml.dom import minidom
from subprocess import Popen
import os
import string

SVG_UNITS_TO_MM_RATIO = 2693.4 / 950.0 #142.23/50.000000

class VectorDrawing:

    def __init__(self,s,nib_size_mm=0.5,base_path="",input_filename=None):

        svg_filename = None
        if ".eps" in input_filename:

            svg_filename = input_filename.replace(".eps",".svg")

            command = ["pstoedit -f plot-svg",input_filename,svg_filename,"-nc"]
            command = string.join(command)

            try:
                pstoedit = os.popen(command, "r")
                status = pstoedit.close()
                if status:
                    raise IOError("pstoedit failed (status %d)" % status)
            except: 
                raise Exception("oops, can not convert eps file")

        else:
            svg_filename = input_filename

        self.s = s
        self.base_path = base_path
        self.s.setBoundsFunction(self.inCanvas)

        self.signature_pos = (750,917)
        self.start = (100,100)

        doc = minidom.parse(svg_filename)

        path_strings = [(path.getAttribute('stroke') != "red",path.getAttribute('points'),"polygon") for path in doc.getElementsByTagName('polygon')]
        path_strings += [(path.getAttribute('stroke') != "red",path.getAttribute('points'),"polyline") for path in doc.getElementsByTagName('polyline')]
        path_strings += [self.lineToPathString(path) for path in doc.getElementsByTagName('line')]

        self.paths = []
        for pstr in path_strings:
            if pstr[0]:
                self.paths.append((pstr[1],pstr[2]))
        doc.unlink()  

        self.generate()

    def lineToPathString(self,line_xml):
        path_string = u"%s,%s %s,%s"%(line_xml.getAttribute('x1'),line_xml.getAttribute('y1'),line_xml.getAttribute('x2'),line_xml.getAttribute('y2')) 
        return (line_xml.getAttribute('stroke') != "red",path_string,"line")

    def inCanvas(self,x,y):
        return 1

    def toradians(self,deg):
        return deg * math.pi/180.0

    def sign(self):
        import json
        f = open(self.base_path+"assets/signature_data.json","r") 
        data = json.loads(f.read())

        self.s.releaseMoveMode()

        x_offset,y_offset = data[0]
        for pos in data:
            x,y = pos
            x = (x - x_offset ) / 10.0 + self.signature_pos[0]
            y = (y - y_offset ) / 10.0 + self.signature_pos[1]
            a1,a2 = self.s.getStateFromXYonCanvas(x,y)
            xy = self.s.appendAngles(a1,a2)

        return xy

    def translate(self,coord):
        return float(coord[0]) / SVG_UNITS_TO_MM_RATIO, -( float(coord[1]) / SVG_UNITS_TO_MM_RATIO )  + 1000.0

    def drawPath(self,path_string,should_close=False):
        self.s.setMoveMode()
        start_coord = self.translate(path_string.split(" ")[0].split(","))
        self.s.drawVectorFromTo(self.prev_coord, start_coord,-1,beginspeed=0,endspeed=0)
        self.prev_coord = start_coord
        self.s.releaseMoveMode()
        for _xy in path_string.split(" "):
            coord = _xy.split(",")
            if len(coord) == 2:
                _coord = self.translate(coord)
                self.s.drawVectorFromTo(self.prev_coord, _coord,1,beginspeed=0,endspeed=0)
                self.prev_coord = _coord
        if should_close:
            self.s.drawVectorFromTo(self.prev_coord, start_coord,1,beginspeed=0,endspeed=0)
            self.prev_coord = start_coord

    def generate(self): 
    
        self.s.setMoveMode()
        start_pos = self.translate(self.paths[0][0].split(" ")[0].split(","))
        self.s.drawLineFromTo(HOME, start_pos,-1,beginspeed=0,endspeed=0)
        self.s.releaseMoveMode()

        self.prev_coord = start_pos

        self.s.beginLine(0,35,500)
        for p in self.paths:
            self.drawPath(p[0],p[1] is "polygon")
        self.s.endLine(0,500)

        self.s.setMoveMode()
        self.s.drawLineFromTo(self.prev_coord,self.signature_pos,-1)
        self.s.releaseMoveMode()

        self.s.beginLine(0,35,500)
        x,y = self.sign()
        self.s.endLine(0,500)

        self.s.setMoveMode()
        self.s.drawLineFromTo((x,y),HOME,-1)
        self.s.releaseMoveMode()
        
if __name__ == "__main__":

    import os
    

    from machine_settings import *
    from generator import Generator
    from easer import Easer
    from model import Blackstripes_MKII
    from simulator import Simulator

    m = Blackstripes_MKII()
    VectorDrawing(m,MARKER_NIB_SIZE_MM,"","test_drawing.eps")
    Generator(m,"data.tmp")
    Easer("data.tmp",output_filename ="svg_drawing")
    os.remove("data.tmp")

    Simulator("svg_drawing.bin",None,8000000)

    print "scp svg_drawing.bin rpi@192.168.0.102:/home/rpi/blackstripes/svg_drawing.bin"

