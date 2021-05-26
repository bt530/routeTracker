from UI import *
from logReader import *
from loguru import logger

try:
    logger.add(sink='routeTrackerErrorLog.txt')
    reader = logReader()
    ui = UserInterface(reader=reader)
    ui.mainLoop()
except Exception:
    logger.exception("Unhandled Exception")
