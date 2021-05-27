from UI import *
from logReader import *
import traceback

try:
    reader = logReader()
    ui = UserInterface(reader=reader)
    ui.mainLoop()
except:
    print(traceback.format_exc())
    with open('routeTrackerErrorLog.txt', 'w') as f:
        f.write(traceback.format_exc())
