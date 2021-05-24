from UI import *
from logReader import *
import traceback
try:
    reader=logReader()
    ui=userInterface(reader=reader)
    ui.mainLoop()
except Exception as e:
    with open('routeTrackerErrorLog.txt','w') as f:
        f.write(traceback.format_exc())
