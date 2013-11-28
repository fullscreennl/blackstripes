import unittest

import sys
sys.path.append('../blackstripesMK1/machine_motion')
from generate_mk1_drawing import OrderProcessor

import builder
import driver
import sys, os
import filecmp
 
class outputTest(unittest.TestCase):
    def setUp(self):
        pass

    def generate(self,fake_order_id):

        order = "../blackstripesMK1/machine_motion/testies_210_180_120_50.png"
        job = OrderProcessor(order)
        filename = job.getFileName()
        basepath = job.getReferenceSetBasePath(fake_order_id)
        levels = job.getLevels()
        order_id = fake_order_id 
        tempPath = basepath+"temp/"
        
        needsDataGeneration = 1
        try:
            os.makedirs(basepath+"/temp")
        except OSError,err:
            if err.errno != 17:
                #dir exsists
                raise
            if "reference" in basepath:
                needsDataGeneration = 0
                
        if needsDataGeneration:
            buildr = builder.Builder(order)
            buildr.buildLayerData(basepath+order_id,0,levels)   
           
            drivr = driver.Driver(basepath+order_id,tempPath)
            linenr = 0
            start = 0
            drivr.run(int(linenr),start)
        else:
            print "skip"

        return tempPath

    def compare(self,reference,testcase):
        print "comparing ",reference, " to ", testcase
        for f in ["layer0.dat","layer1.dat","layer2.dat","layer3.dat","layer4.dat"]:
            if not filecmp.cmp(reference+f, testcase+f):
                raise Exception("testcase FAILED machine instructions changed!") 
            else:
                print "comparing "+f+" OK"

    def testOutput(self):
        reference = self.generate("reference")
        testcase = self.generate("testcase")
        self.compare(reference,testcase)

        

if __name__ == '__main__':
    unittest.main()