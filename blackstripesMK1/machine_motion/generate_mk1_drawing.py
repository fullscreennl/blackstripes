import builder
import driver
import sys, os
import zipfile

class OrderProcessor:

    def __init__(self,order):
        self.filename = order = os.path.basename(str(order))
        data = order.split(".")[0].split("_")
        self.orderid = data[0]
        self.basePath = "generated_data/"+self.orderid+"/"
        self.levels = []
        levels_strings = data[1:]
        for l in levels_strings:
            self.levels.append(int(l))
            
        if len(self.levels) < 4:
            raise Exception("to few levels!")
        if len(self.levels) > 4:
            raise Exception("to many levels!")
        if ".png" not in self.filename:
            raise Exception( "no .png file!")


    def getFileName(self):
        return self.filename

    def getOrderId(self):
        return self.orderid
        
    def getLevels(self):
        return self.levels
        
    def getBasePath(self):
        return self.basePath

    def getReferenceSetBasePath(self,fake_order_id = ""):
        return "generated_data/"+fake_order_id+"/"


if __name__ == '__main__':
    order = sys.argv[1]
    job = OrderProcessor(order)
    filename = job.getFileName()
    basepath = job.getBasePath()
    levels = job.getLevels()
    order_id = job.getOrderId() 
    
    try:
        os.makedirs(basepath)
    except:
        pass

    buildr = builder.Builder(filename)
    buildr.buildLayerData(basepath+order_id,0,levels)   
   
    drivr = driver.Driver(basepath+order_id)
    linenr = 0
    start = 0
    drivr.run(int(linenr),start)  

    zf = zipfile.ZipFile(basepath+order_id+'.zip', 'w',zipfile.ZIP_DEFLATED)
    zf.write('layer0.dat')
    zf.write('layer1.dat')
    zf.write('layer2.dat')
    zf.write('layer3.dat')
    zf.close()
    
    command = "scp generated_data/"+order_id+"/"+order_id+".zip jed@192.168.0.103:/home/jed/GPIO_C_driver/job.zip"
    res = os.system(command)
    if res:
        print "ERROR"
        print "auto scp failed, no key or host down?"
    else:
        print "OK"

    os.remove('layer0.dat')
    os.remove('layer1.dat')
    os.remove('layer2.dat')
    os.remove('layer3.dat')
    os.remove('layer4.dat')

