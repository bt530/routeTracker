import json
import os
import fnmatch
import logging
import dateutil.parser

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

        match = 1
        target_match = 7 * 5 * 3 * 2
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
                    with open(self.folder_location + "\\" + directory[i], encoding="utf-8") as f:
                        file_data = f.readlines()

                except Exception:
                    file_data = {}
                    self.log.exception('Error reading file ' + self.folder_location + "\\" + directory[i])

                for line in file_data:
                    data = json.loads(line)

                    if match % 2 != 0:
                        if data["event"] == "CarrierJump" or data["event"] == "FSDJump":
                            system = data["StarSystem"]
                            self.log.info("Found current star system: " + system)
                            match = match * 2

                    if match % 3 != 0:
                        if data["event"] == "CarrierJumpRequest":
                            t = data["timestamp"]
                            self.log.debug("CarrierJumpRequest: extracted " + t)
                            t = dateutil.parser.parse(t)
                            self.log.info("CarrierJumpRequest: found timestamp " + str(t))
                            self.route_data.lastJumpRequest = t.timestamp()
                            match = match * 3

                    if match % 5 != 0:
                        if data["event"] == "Cargo" and data["Vessel"] == "Ship":
                            cargo = data["Count"]
                            self.log.info('Ship Inventory: ' + str(cargo))
                            self.route_data.shipInventory = cargo
                            match = match * 5

                    if match % 7 != 0:
                        if data["event"] == "CarrierStats":
                            fuel = data["FuelLevel"]
                            self.route_data.carrierFuel = fuel
                            self.log.info('Carrier fuel: ' + str(fuel))
                            cargo = data["SpaceUsage"]["Cargo"]
                            self.log.info('Carrier cargo: ' + str(cargo))
                            self.route_data.carrierInventory = cargo
                            match = match * 7
                    if match == target_match:
                        break

        self.route_data.firstCheck = False


if __name__ == '__main__':
    reader = LogReader()
    reader.update_log()
