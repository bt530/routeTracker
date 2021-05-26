from routeTracker import logReader, UI
from loguru import logger

# noinspection PyBroadException
try:
    logger.add(sink='routeTrackerErrorLog.txt')
    reader = logReader.logReader()
    ui = UI.userInterface(reader=reader)
    ui.mainLoop()
except Exception:
    logger.exception("Unhandled exception")
