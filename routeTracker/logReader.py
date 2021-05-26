import threading
import time
import os
# from os.path import isfile, join
import datetime
from typing import Union


class logReader():
    carrierName: str
    carrierFuel: int
    carrierInventory: int
    shipInventory: int
    currentSystem: str
    firstCheck: bool
    checked: Union[str, None]
    activeFile: Union[str, None]
    oldSystem: str
    lastJumpRequest: float

    def __init__(self, checkFrequency=60, folderLocation=None):
        self.resetValues()
        self.folderLocation = folderLocation
        if self.folderLocation is None:
            self.defaultLocation()

    def defaultLocation(self):

        # self.folderLocation='C:\\Users\\'+os.getlogin()+'\\Saved Games\\Frontier Developments\\Elite Dangerous'
        self.folderLocation = os.environ['USERPROFILE'] + '\\Saved Games\\Frontier Developments\\Elite Dangerous'
        # print(os.environ['USERPROFILE'])
        # print(self.folderLocation)

    def resetValues(self):
        self.firstCheck = True
        self.checked = None
        self.activeFile = None
        self.currentSystem = 'unknown'
        self.carrierFuel = 0

        self.carrierInventory = 0
        self.shipInventory = 0
        self.carrierName = 'unknown'
        self.oldSystem = 'unknown'
        self.lastJumpRequest = 0

    def updateLog(self):
        self.oldSystem = self.currentSystem
        directory = os.listdir(self.folderLocation)
        directory.reverse()
        ##print(directory)

        match = 1
        targetMatch = 11 * 7 * 5 * 3 * 2
        activeFileReached = False
        for i in range(len(directory)):
            # print(i)
            if match == targetMatch or (not self.firstCheck and activeFileReached):
                break
            else:
                self.checked = directory[i]
            if directory[i] == self.activeFile:
                activeFileReached = True
            splitCheck = directory[i].split('.')
            if splitCheck[-1] == 'log' and splitCheck[0] == 'Journal':
                if not activeFileReached:
                    self.activeFile = directory[i]
                    activeFileReached = True
                try:
                    with open(self.folderLocation + "\\" + directory[i], 'rb') as f:
                        scanningFile = f.read()
                    scanningFile = scanningFile.decode('UTF-8')

                except:
                    scanningFile = ''
                    # print('error reading file '+self.folderLocation+"\\"+directory[i])
                ##print(scanningFile)

                if match % 2 != 0:
                    scan = scanningFile

                    scan = "generalJump".join(scan.split('"event":"CarrierJump"'))
                    scan = "generalJump".join(scan.split('"event":"FSDJump"'))
                    scan = "generalJump".join(scan.split('"event":"Location"'))
                    try:
                        scan = scan.split('generalJump')
                        if len(scan) != 1:
                            scan = scan[-1].split('"StarSystem":"')[1].split('",')[0]
                            print(scan)
                            self.currentSystem = scan

                            match = match * 2
                    except IndexError:
                        print('error')
                        pass

                if match % 3 != 0:

                    scan = scanningFile

                    try:
                        scan = scan.split('Z", "event":"CarrierJumpRequest"')
                        # print(len(scan))
                        if len(scan) != 1:
                            scan = scan[-2].split('"timestamp":"')[-1]
                            # print(scan)
                            scan = scan.split('T')
                            scan[0] = scan[0].split('-')
                            scan[1] = scan[1].split(':')

                            t = datetime.datetime(int(scan[0][0]), int(scan[0][1]), int(scan[0][2]), int(scan[1][0]),
                                                  int(scan[1][1]), int(scan[1][2]))
                            # print(t)

                            t = t.replace(tzinfo=datetime.timezone.utc).timestamp()
                            # print(t)
                            self.lastJumpRequest = t

                            match = match * 3
                    except IndexError:
                        pass
                if match % 5 != 0:

                    scan = scanningFile

                    try:
                        scan = scan.split('"event":"CarrierStats"')

                        if len(scan) != 1:
                            del scan[-1]
                            scan = ''.join(scan)
                            scan = scan.split('"event":"Cargo", "Vessel":"Ship", "Count":')
                            if len(scan) != 1:

                                scan = scan[-1].split(' ')[0]
                                print('cargo', scan)
                                scan = scan.split(',')[0]

                                try:
                                    self.shipInventory = int(scan)
                                except:
                                    self.shipInventory = 0
                                    print('ship inv match error')
                                    # print(scan)

                                match = match * 5
                    except IndexError:
                        # print('error')
                        pass
                if match % 7 != 0:

                    scan = scanningFile

                    try:
                        scan = scan.split('"event":"CarrierStats"')
                        if len(scan) != 1:

                            scan = scan[-1].split('"FuelLevel":')[1].split(',')[0]
                            # print('carrier fuel',scan)
                            # print(directory[i])

                            try:
                                self.carrierFuel = int(scan)
                            except:
                                self.carrierFuel = 0
                                # print('carrier fuel match error')
                                # print(scan)

                            match = match * 7
                    except IndexError:
                        # print('error')
                        pass
                if match % 11 != 0:

                    scan = scanningFile

                    try:
                        scan = scan.split('"event":"CarrierStats"')
                        if len(scan) != 1:

                            scan = scan[-1].split('"Cargo":')[1].split(',')[0]
                            # print('carrier cargo',scan)

                            try:
                                self.carrierInventory = int(scan)
                            except:
                                self.carrierFuel = 0
                                # print('carrier cargo match error')
                                # print(scan)

                            match = match * 11
                    except IndexError:
                        # print('error')
                        pass

        self.firstCheck = False


if __name__ == '__main__':

    reader = logReader()
    reader.updateLog()
    """
    import time
    for i in range(100):
        start=time.time()
        reader.updateLog()
        print(time.time()-start)
    """
