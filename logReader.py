import threading
import time
import os
#from os.path import isfile, join
import datetime
class logReader():
    def __init__(self,checkFrequency=60,folderLocation=None):
        self.resetValues()
        self.folderLocation=folderLocation
        if self.folderLocation == None:
            self.defaultLocation()
        
    def defaultLocation(self):      
        
        self.folderLocation='C:\\Users\\'+os.getlogin()+'\Saved Games\Frontier Developments\Elite Dangerous'


    def resetValues(self):
        self.firstCheck=True
        self.checked=None
        self.activeFile=None
        self.currentSystem='unknown'
        self.carrierFuel='unknown'
        self.carrierCargo='unknown'
        self.carrierTrit='unknown'
        self.shipTrit='unknown'
        self.carrierName='unknown'
        self.oldSystem='unknown'
        self.lastJumpRequest=0
    def updateLog(self):
        self.oldSystem=self.currentSystem
        directory=os.listdir(self.folderLocation)
        directory.reverse()
        #print(directory)
        
        match=1
        targetMatch=3*2
        activeFileReached=False
        for i in range(len(directory)):
            print(i)
            if match == targetMatch or (not self.firstCheck and activeFileReached):
                break
            else:
                self.checked=directory[i]
            if directory[i] == self.activeFile:
                activeFileReached=True

            if directory[i].split('.')[-1] == 'log':
                if activeFileReached == False:
                    self.activeFile=directory[i]
                    activeFileReached=True
                with open(self.folderLocation+"\\"+directory[i],'r') as f:
                    scanningFile = f.read()
                #print(scanningFile)

                if match %2 != 0:
                    scan=scanningFile
                    scan="generalJump".join(scan.split('"event":"CarrierJump"'))
                    scan="generalJump".join(scan.split('"event":"FSDJump"'))
                    try:
                        scan=scan.split('generalJump')[-1].split('"StarSystem":"')[1].split('",')[0]
                        print(scan)
                        self.currentSystem=scan

                    

                    
                        match=match*2
                    except IndexError:
                        pass


        
            

                if match %3 != 0:

                    scan=scanningFile

                    try:
                        scan=scan.split('Z", "event":"CarrierJumpRequest"')[-2].split('"timestamp":"')[-1]
                        print(scan)
                        scan=scan.split('T')
                        scan[0]=scan[0].split('-')
                        scan[1]=scan[1].split(':')
                        

                        
                        t = datetime.datetime(int(scan[0][0]), int(scan[0][1]), int(scan[0][2]), int(scan[1][0]), int(scan[1][1]), int(scan[1][2]))
                        print(t)
                        
                        t = t.replace(tzinfo=datetime.timezone.utc).timestamp()
                        print(t)
                        self.lastJumpRequest=t
                        
                    

                    
                        match=match*3
                    except IndexError:
                        pass

        self.firstCheck=False

if __name__ == '__main__':
    reader=logReader()
    reader.updateLog()
        




