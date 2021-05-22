import json
import os
import fnmatch
import logging
import time

import dateutil.parser
import tailer

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

        while True:
            directory = fnmatch.filter(os.listdir(self.folder_location), "Journal.*.log")
            directory.reverse()
            self.log.debug("Directory content: " + str(directory))
            target_log_file = self.folder_location + "\\" + directory[0]
            if self.route_data.checked != target_log_file:
                self.log.debug("Checking log: " + target_log_file)
                self.follow_log(target_log_file)
            else:
                self.log.debug("Elite not running, sleeping a bit")
                time.sleep(10)

    def follow_log(self, filename):
        self.route_data.activeFile = filename
        file_handle = open(filename)
        all_lines = file_handle.readlines()
        for line in all_lines:
            self.process_line(line)
            if self.route_data.checked == self.route_data.activeFile:
                break
        if self.route_data.checked != self.route_data.activeFile:
            for line in tailer.follow(file_handle):
                self.process_line(line)
                if self.route_data.checked == self.route_data.activeFile:
                    break

    def process_line(self, line):
        data = json.loads(line)
        if data["event"] == "Shutdown":
            # we are at the end of the file, Elite was shutdown
            self.route_data.checked = self.route_data.activeFile
            self.log.info("Elite Dangerous shutdown detected. Waiting for a newer log file.")
            # stop following the log and wait for a newer one
        if data["event"] == "CarrierJump" or data["event"] == "FSDJump" or data["event"] == "Location":
            system = data["StarSystem"]
            self.log.info("Found current star system: " + system)
            self.route_data.currentSystem = system
        if data["event"] == "CarrierJumpRequest":
            t = data["timestamp"]
            self.log.debug("CarrierJumpRequest: extracted " + t)
            t = dateutil.parser.parse(t)
            self.log.info("CarrierJumpRequest: found timestamp " + str(t))
            self.route_data.lastJumpRequest = t.timestamp()
            self.route_data.destinationSystem = data["SystemName"]
        if data["event"] == "Cargo" and data["Vessel"] == "Ship":
            cargo = data["Count"]
            self.log.info('Ship Inventory: ' + str(cargo))
            self.route_data.shipInventory = cargo
        if data["event"] == "CarrierStats":
            fuel = data["FuelLevel"]
            self.route_data.carrierFuel = fuel
            self.log.info('Carrier fuel: ' + str(fuel))
            cargo = data["SpaceUsage"]["Cargo"]
            self.log.info('Carrier cargo: ' + str(cargo))
            self.route_data.carrierInventory = cargo
        if data["event"] == "CarrierDepositFuel":
            fuel = data["Total"]
            self.route_data.carrierFuel = fuel
            self.log.info('Carrier fuel: ' + str(fuel))
        if data["event"] == "CarrierJumpCancelled":
            self.log.info('Carrier jump cancelled!')
            self.route_data.destinationSystem = None
            self.route_data.lastJumpRequest = None


if __name__ == '__main__':
    reader = LogReader()
    reader.update_log()
