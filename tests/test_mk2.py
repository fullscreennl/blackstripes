import unittest
import sys, os
sys.path.append('../blackstripesMK2/machine_motion')

from machine_settings import *
from generator import Generator
from easer import Easer
from model import Blackstripes_MKII
#small spiral fits on cardboard panel
from smallSpiral import SmallSpiral
from spiral import Spiral

import filecmp
 
class outputTest(unittest.TestCase):

    def setUp(self):
        pass

    def generate(self,_id):

        needsDataGeneration = 1
        try:
            os.makedirs("generated_data/"+_id)
        except OSError,err:
            if err.errno != 17:
                #dir exsists
                raise
            if "reference" in _id:
                needsDataGeneration = 0

        if needsDataGeneration:
            m = Blackstripes_MKII()
            Spiral(m,MARKER_NIB_SIZE_MM,'../blackstripesMK2/machine_motion/')
            
            temp_file = "generated_data/"+_id+"/data.tmp"
            Generator(m,temp_file)
            Easer(temp_file,output_filename ="generated_data/"+_id+"/spiral")
            os.remove(temp_file)

        return "generated_data/"+_id+"/spiral.bin"

    def compare(self,reference,testcase):
        print "comparing ",reference, " to ", testcase
        if not filecmp.cmp(reference, testcase):
            raise Exception("testcase FAILED machine instructions changed!") 
        else:
            print "comparing "+reference+" OK"

    def testOutput(self):
        reference = self.generate("mk2_reference")
        testcase = self.generate("mk2_testcase")
        self.compare(reference,testcase)

        

if __name__ == '__main__':
    unittest.main()