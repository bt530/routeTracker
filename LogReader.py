import os
import fnmatch
import datetime
import logging

from RouteData import RouteData




class LogReader:
    def __init__(self, folder_location=None):
        self.log = logging.getLogger(__name__)
        self.route_data = RouteData()
        self.folder_location = folder_location
        if self.folder_location is None:
            self.default_location()

    def default_location(self):
        self.folder_location = os.environ['USERPROFILE'] + '\\Saved Games\\Frontier Developments\\Elite Dangerous'
        self.log.debug("USERPROFILE path: " + os.environ['USERPROFILE'])
        self.log.debug("Full folder path: " + self.folder_location)

    def update_log(self):
        self.route_data.oldSystem = self.route_data.currentSystem
        directory = fnmatch.filter(os.listdir(self.folder_location), "Journal.*.log");
        directory.reverse()
        self.log.debug("Directory content: " + str(directory))

        # TODO use JSON library instead of custom parsing
        match = 1
        target_match = 11 * 7 * 5 * 3 * 2
        active_file_reached = False
        for i in range(len(directory)):
            self.log.info("Processing file %d: %s", i, directory[i])
            if match == target_match or (not self.route_data.firstCheck and active_file_reached):
                break
            else:
                self.route_data.checked = directory[i]
            if directory[i] == self.route_data.activeFile:
                active_file_reached = True
                self.log.debug('Active file reached')

            if directory[i].split('.')[-1] == 'log' or directory[i].split(',')[-1]:
                if not active_file_reached:
                    self.route_data.activeFile = directory[i]
                    active_file_reached = True
                    self.log.debug('Active file reached')
                try:
                    with open(self.folder_location + "\\" + directory[i], 'rb') as f:
                        scanning_file = f.read()
                    scanning_file = scanning_file.decode('UTF-8')

                except Exception:
                    scanning_file = ''
                    self.log.exception('Error reading file ' + self.folder_location + "\\" + directory[i])
                # Too much info self.log.debug('Full file content: ' + scanning_file)

                if match % 2 != 0:
                    scan = scanning_file
                    scan = "generalJump".join(scan.split('"event":"CarrierJump"'))
                    scan = "generalJump".join(scan.split('"event":"FSDJump"'))
                    try:
                        scan = scan.split('generalJump')
                        if len(scan) != 1:
                            scan = scan[-1].split('"StarSystem":"')[1].split('",')[0]
                            self.log.info("Found current star system: " + scan)
                            self.route_data.currentSystem = scan

                            match = match * 2
                    except Exception:
                        self.log.exception("Problem reading current system")
                        pass

                if match % 3 != 0:

                    scan = scanning_file

                    try:
                        scan = scan.split('Z", "event":"CarrierJumpRequest"')
                        self.log.debug("CarrierJumpRequest: " + str(len(scan)))
                        if len(scan) != 1:
                            scan = scan[-2].split('"timestamp":"')[-1]
                            self.log.debug("CarrierJumpRequest: " + scan)
                            scan = scan.split('T')
                            scan[0] = scan[0].split('-')
                            scan[1] = scan[1].split(':')

                            t = datetime.datetime(int(scan[0][0]), int(scan[0][1]), int(scan[0][2]), int(scan[1][0]),
                                                  int(scan[1][1]), int(scan[1][2]))
                            self.log.debug("CarrierJumpRequest: extracted " + str(t))

                            t = t.replace(tzinfo=datetime.timezone.utc).timestamp()
                            self.log.info("CarrierJumpRequest: found timestamp " + str(t))
                            self.route_data.lastJumpRequest = t

                            match = match * 3
                    except IndexError:
                        self.log.exception("CarrierJumpRequest")
                        pass
                if match % 5 != 0:

                    scan = scanning_file

                    try:
                        scan = scan.split('"event":"CarrierStats"')

                        if len(scan) != 1:
                            del scan[-1]
                            scan = ''.join(scan)
                            scan = scan.split('"event":"Cargo", "Vessel":"Ship", "Count":')
                            if len(scan) != 1:

                                scan = scan[-1].split(',')[0]
                                self.log.debug('Cargo: ' + scan)

                                try:
                                    self.route_data.shipInventory = int(scan)
                                except Exception:
                                    self.route_data.shipInventory = 0
                                    self.log.exception('Ship inventory match error')
                                    self.log.debug('Ship inventory match error cause: ' + scan)

                                match = match * 5
                    except IndexError:
                        self.log.exception("Cargo")
                        pass
                if match % 7 != 0:

                    scan = scanning_file

                    try:
                        scan = scan.split('"event":"CarrierStats"')
                        if len(scan) != 1:

                            scan = scan[-1].split('"FuelLevel":')[1].split(',')[0]
                            self.log.info('Carrier fuel: ' + scan)

                            try:
                                self.route_data.carrierFuel = int(scan)
                            except:
                                self.route_data.carrierFuel = 0
                                self.log.exception('Carrier fuel parse error')
                                self.log.debug('Carrier fuel parse error cause: ' + scan)

                            match = match * 7
                    except IndexError:
                        self.log.exception('Fuel')
                        pass
                if match % 11 != 0:

                    scan = scanning_file

                    try:
                        scan = scan.split('"event":"CarrierStats"')
                        if len(scan) != 1:

                            scan = scan[-1].split('"Cargo":')[1].split(',')[0]
                            self.log.info('Carrier cargo: ' + scan)

                            try:
                                self.route_data.carrierInventory = int(scan)
                            except:
                                self.route_data.carrierInventory = 0
                                self.log.exception('Carrier cargo parse error')
                                self.log.debug('Carrier cargo parse error cause: ' + scan)

                            match = match * 11
                    except IndexError:
                        self.log.exception('Cargo')
                        pass

        self.route_data.firstCheck = False


if __name__ == '__main__':
    reader = LogReader()
    reader.update_log()
