import tkinter as tk
import ctypes
import time
import math
import pickle
import winsound
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import messagebox
import os
import pyperclip
import webbrowser
import traceback


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_ulong), ("y", ctypes.c_ulong)]


def mousePosition():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))

    return int(pt.x), int(pt.y)


class userInterface():

    def __init__(self, reader, debug=False):
        user32 = ctypes.windll.user32
        width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        dataTemplate = {'window position': [width / 2 - 250, height / 4], 'route positions': {}, 'showType': 'show',
                        'topmost': 1, 'alarm': True, 'logLocation': '', 'shipCargo': 0, 'carrierCargo': 0,
                        'more': False}
        self.exiting = False
        self.debug = debug
        # self.logReader=reader
        self.maxCountdown = 60 * 21

        self.logCheck = 5
        self.logReader = reader

        self.scroll = 0

        self.dragOffset = [0, 0]
        self.scrolling = False

        self.stopLocations = []

        self.countdown = self.maxCountdown
        self.countdownStart = time.time()
        self.logStart = 0

        self.currentFileDataKeys = {}
        self.currentFileData = [['unknown']]
        self.system = None
        self.nextSystem = 'unknown'
        self.currentFile = None

        self.position = 0

        self.dragging = False
        self.draggingPos = [width / 2 - 250, height / 4]

        self.scrollTop = [0, 0]
        self.scrollBottom = [0, 0]

        try:
            with open("trackerData.txt", "rb") as f:
                self.data = pickle.load(f)
        except FileNotFoundError:

            self.data = dataTemplate
            with open("trackerData.txt", "wb") as f:
                pickle.dump(self.data, f)

        added = False
        dataKeys = list(self.data.keys())
        for i in list(dataTemplate.keys()):
            if i not in dataKeys:
                self.data[i] = dataTemplate[i]
                added = True
        if added:
            with open("trackerData.txt", "wb") as f:
                pickle.dump(self.data, f)

        if "current file" in list(self.data.keys()):
            self.currentFile = self.data["current file"]

            self.openFile(dialogue=False)

        if self.data['logLocation'] != '':
            self.logReader.folderLocation = self.data['logLocation']
        self.createWindow()

    def mainLoop(self):
        topSet = -1
        timeLoop = time.time()
        while True:
            time.sleep(0.01)
            try:
                test = pyperclip.paste()
                if self.exiting:
                    self.saveData()
                    self.window.destroy()
                    self.root.destroy()
                    try:
                        self.settingsWindow.destroy()
                    except:
                        # print('settings window does not yet exist')
                        pass
                    break
                # self.menu.update()
                currentTime = time.time()
                if currentTime - self.logStart > self.logCheck and self.currentFileData != None:
                    self.logStart = currentTime
                    try:
                        self.logReader.updateLog()
                    except Exception as e:
                        if self.debug:
                            messagebox.showerror("Error", e)
                        pass
                    # print(self.logReader.oldSystem,self.logReader.currentSystem)
                    if self.logReader.oldSystem != self.logReader.currentSystem:
                        # print("Jumped to "+self.logReader.currentSystem)
                        self.nextSystem = 'unknown'
                        for i in range(self.position, len(self.currentFileData) - 1):
                            ##print(i)
                            ##print(ui.currentFileData[i])
                            if self.currentFileData[i][
                                self.currentFileDataKeys['System Name']] == self.logReader.currentSystem:

                                # print('copied ' + self.nextSystem + ' to clipboard')
                                if self.currentFileData[i + 1][self.currentFileDataKeys['System Name']] == \
                                        self.currentFileData[i][self.currentFileDataKeys['System Name']]:
                                    self.position = i + 1
                                    # print('double')
                                else:
                                    self.position = i
                                self.nextSystem = self.currentFileData[self.position + 1][
                                    self.currentFileDataKeys['System Name']]
                                pyperclip.copy(self.nextSystem)
                                self.data['route positions'][self.currentFile] = self.position
                                self.saveData()
                                # try:
                                self.clear()
                                """
                                except Exception as e:
                                    #print(e)"""
                                break

                # try:
                self.root.update()
                x, y = mousePosition()
                if self.dragging:

                    self.data['window position'] = [x - self.dragOffset[0], y - self.dragOffset[1]]
                    self.clear()
                elif self.scrolling and self.scrollLength < len(self.currentFileData):
                    proportion = (y - self.barCentre - self.scrollTop[1]) / self.scrollHeight
                    self.scroll = round(proportion * len(self.currentFileData) - self.position)
                    self.limitScroll()

                    self.clear()
                elif currentTime - timeLoop > 1:
                    self.clear()
                    timeLoop = currentTime
                    """
                    if self.data['topmost'] == 0:
                        if not self.window.focus_displayof():
                            if topSet != 0:
                                self.window.attributes('-topmost', 0)
                                topSet=0
                            
                        elif topSet != 1:
                            self.window.attributes('-topmost', 1)
                            topSet=1
                        ##print(topSet)
                    """

                """
                except Exception as e:
                    if e == SystemExit:
                        break
                    else:
                        self.exiting=True
                        #print(e)"""

                try:
                    self.settingsWindow.update()
                except:
                    pass
            except pyperclip.PyperclipWindowsException:
                time.sleep(2)

    def openFile(self, dialogue=True):
        self.scroll = 0
        if dialogue:
            self.currentFile = askopenfilename()
            self.data["current file"] = self.currentFile
        if self.currentFile != '':
            # print(self.currentFile)
            # print(self.data)
            if self.currentFile in list(self.data['route positions'].keys()):
                self.position = self.data['route positions'][self.currentFile]
            else:
                self.position = 0
                self.data['route positions'][self.currentFile] = self.position
            self.saveData()
            try:
                with open(self.currentFile, 'r') as f:
                    self.currentFileData = f.read()

                self.currentFileData = "".join(self.currentFileData.split("\""))

                self.currentFileData = self.currentFileData.split("\n")
                self.currentFileData = [i.split(",") for i in self.currentFileData]
                ##print(currentFileData)

                self.currentFileDataKeys = {}
                for i in range(len(self.currentFileData[0])):
                    self.currentFileDataKeys[self.currentFileData[0][i]] = i
                del self.currentFileData[0]
                if [''] in self.currentFileData:
                    self.currentFileData.remove([''])

                self.stopLocations = []
                for i in range(len(self.currentFileData) - 1):
                    if self.currentFileData[i][self.currentFileDataKeys['System Name']] == self.currentFileData[i + 1][
                        self.currentFileDataKeys['System Name']]:
                        self.stopLocations.append(i)
                    ##print(self.currentFileData[i])
                ##print(self.stopLocations)
            except FileNotFoundError as e:

                messagebox.showerror("Import Error", e)
            if self.data['showType'] == 'show':
                self.logReader.resetValues()
                self.logStart = 0

                self.createWindow()

    def saveData(self, values=None):

        with open("trackerData.txt", "wb") as f:
            pickle.dump(self.data, f)

    # overlay functions

    def clear(self):

        # all to change with new UI

        try:

            self.canvas.destroy()

        except:
            pass

        clip = pyperclip.paste()

        x, y = self.data['window position'][0], self.data['window position'][1]

        self.canvas = tk.Canvas(self.window, bg="pink", bd=0, highlightthickness=0, relief='ridge')
        self.canvas.pack(fill="both", expand=True)

        self.canvas.create_rectangle(x, y, x + 520, y + 30, fill='black')
        if self.logReader.currentSystem == clip:
            self.canvas.create_text(x + 5, y + 5, text=self.logReader.currentSystem, font="Ebrima 13 bold",
                                    fill='green', anchor='nw')
        else:
            self.canvas.create_text(x + 5, y + 5, text=self.logReader.currentSystem, font="Ebrima 13 bold",
                                    fill='orange', anchor='nw')
        self.canvas.create_rectangle(x + 150, y, x + 500, y + 30, fill='black')

        self.canvas.create_text(x + 158, y + 5, text='>>  ', font="Ebrima 13 bold", fill='orange', anchor='nw')

        if self.nextSystem == clip:
            self.canvas.create_text(x + 190, y + 5, text=self.nextSystem, font="Ebrima 13 bold", fill='green',
                                    anchor='nw')
        else:
            self.canvas.create_text(x + 190, y + 5, text=self.nextSystem, font="Ebrima 13 bold", fill='orange',
                                    anchor='nw')

        self.canvas.create_rectangle(x + 340, y, x + 500, y + 30, fill='black')

        timeSince = time.time() - self.logReader.lastJumpRequest
        timeSince = self.maxCountdown - timeSince

        if timeSince > 0:
            if timeSince < 10 and self.data['alarm']:
                winsound.Beep(3000, 100)
            mins = str(round(timeSince // 60))
            seconds = str(math.floor(timeSince % 60))
            if len(mins) == 1:
                mins = '0' + mins
            if len(seconds) == 1:
                seconds = '0' + seconds
            text = mins + ':' + seconds
        else:
            text = 'Ready'
        text = '| ' + text + ' |'

        self.canvas.create_text(x + 350, y + 5, text=text, font="Ebrima 13 bold", fill='orange', anchor='nw')

        self.canvas.create_text(x + 420, y + 5, text='☰', font="Ebrima 13 bold", fill='orange', anchor='nw')

        self.canvas.create_text(x + 440, y + 5, text='📁', font="Ebrima 13 bold", fill='orange', anchor='nw')

        self.canvas.create_text(x + 463, y + 5, text='⚙', font="Ebrima 13 bold", fill='orange', anchor='nw')
        if self.data['topmost'] == 1:
            self.canvas.create_text(x + 485, y + 5, text='⮝', font="Ebrima 13 bold", fill='orange', anchor='nw')

        else:
            self.canvas.create_text(x + 485, y + 5, text='⮟', font="Ebrima 13 bold", fill='orange', anchor='nw')

        self.canvas.create_text(x + 500, y + 5, text='✘', font="Ebrima 13 bold", fill='orange', anchor='nw')

        self.canvas.create_line(x, y, x + 520, y, fill='orange')
        self.canvas.create_line(x, y + 30, x + 520, y + 30, fill='orange')
        if self.data['more']:
            self.createDashboard()

    def createDashboard(self):

        x, y = self.data['window position'][0], self.data['window position'][1]
        try:

            self.canvas.create_rectangle(x, y + 35, x + 520, y + 600, fill='black', outline='orange')

            # pannel backgrounds
            self.canvas.create_rectangle(x + 10, y + 40, x + 510, y + 150, fill='#111111', outline='#333333')

            self.canvas.create_rectangle(x + 10, y + 160, x + 510, y + 270, fill='#111111', outline='#333333')

            self.canvas.create_rectangle(x + 10, y + 280, x + 510, y + 540, fill='#111111', outline='#333333')

            above = True
            for i in [0] + self.stopLocations:
                horPos = i / len(self.currentFileData) * 480 + 20
                if above:

                    self.canvas.create_rectangle(x + horPos - 8, y + 45, x + 500, y + 80, fill='#111111',
                                                 outline='#111111')
                    self.canvas.create_line(x + horPos, y + 70, x + horPos, y + 80, fill='orange')
                    self.canvas.create_text(x + horPos, y + 60, text=self.currentFileData[i][self.currentFileDataKeys[
                        'System Name']] + "   ", font="Ebrima 8 bold", fill='orange', anchor='w')
                else:

                    self.canvas.create_rectangle(x + horPos - 8, y + 80, x + 500, y + 120, fill='#111111',
                                                 outline='#111111')
                    self.canvas.create_line(x + horPos, y + 80, x + horPos, y + 90, fill='orange')
                    self.canvas.create_text(x + horPos, y + 95, text=self.currentFileData[i][self.currentFileDataKeys[
                        'System Name']] + "   ", font="Ebrima 8 bold", fill='orange', anchor='w')

                above = not above
            horPos = 500
            if above:

                self.canvas.create_rectangle(x + horPos - 10, y + 45, x + 500, y + 80, fill='#111111',
                                             outline='#111111')
                self.canvas.create_line(x + horPos, y + 70, x + horPos, y + 80, fill='orange')
                self.canvas.create_text(x + horPos, y + 60,
                                        text="   " + self.currentFileData[-1][self.currentFileDataKeys['System Name']],
                                        font="Ebrima 8 bold", fill='orange', anchor='e')
            else:

                self.canvas.create_rectangle(x + horPos - 10, y + 80, x + 500, y + 120, fill='#111111',
                                             outline='#111111')
                self.canvas.create_line(x + horPos, y + 80, x + horPos, y + 90, fill='orange')
                self.canvas.create_text(x + horPos, y + 95,
                                        text="   " + self.currentFileData[-1][self.currentFileDataKeys['System Name']],
                                        font="Ebrima 8 bold", fill='orange', anchor='e')
            ##print(self.stopLocations)
            self.canvas.create_line(x + 20, y + 80, x + 500, y + 80, fill='orange', width=2)

            self.canvas.create_oval(x + 15, y + 75, x + 25, y + 85, fill='orange', outline='orange')

            self.canvas.create_oval(x + 495, y + 75, x + 505, y + 85, fill='orange', outline='orange')

            self.canvas.create_text(x + 20, y + 130, text="Jumps | Completed: " + str(self.position),
                                    font="Ebrima 13 bold", fill='orange', anchor='w')
            for i in self.stopLocations:
                diff = i - self.position
                if diff >= 0:
                    self.canvas.create_text(x + 220, y + 130, text="| To Waypoint: " + str(diff), font="Ebrima 13 bold",
                                            fill='orange', anchor='w')
                    break
            self.canvas.create_text(x + 380, y + 130,
                                    text="| Left: " + str(len(self.currentFileData) - self.position - 1),
                                    font="Ebrima 13 bold", fill='orange', anchor='w')
            for i in self.stopLocations:
                horPos = i / len(self.currentFileData) * 480 + 20
                self.canvas.create_oval(x + horPos - 3, y + 77, x + horPos + 3, y + 83, fill='orange', outline='orange')
                ##print('h',horPos)
            ##print(self.stopLocations)
            horPos = self.position / len(self.currentFileData) * 480 + 20
            self.canvas.create_polygon(x + horPos - 5, y + 85, x + horPos, y + 75, x + horPos + 5, y + 85,
                                       fill='#00ff00', outline='#00ff00')

            try:
                reqFuel = self.currentFileData[self.position][self.currentFileDataKeys['Tritium in market']]

                reqFuel = int(reqFuel)
                if reqFuel > 0:
                    reqFuel += 1000
                else:
                    for i in range(self.position, len(self.currentFileData)):
                        reqFuel += int(self.currentFileData[i][self.currentFileDataKeys['Fuel Used']])
                    reqFuel -= int(self.currentFileData[self.position][self.currentFileDataKeys['Fuel Used']])
            except IndexError:
                reqFuel = 'Error'

            tankFuel = self.logReader.carrierFuel
            shipFuel = self.logReader.shipInventory - self.data['shipCargo']
            carrierFuel = self.logReader.carrierInventory - self.data['carrierCargo']
            self.canvas.create_text(x + 20, y + 180, text="Tritium | ", font="Ebrima 13 bold", fill='orange',
                                    anchor='w')
            self.canvas.create_text(x + 95, y + 180, text="Tank: " + str(tankFuel), font="Ebrima 13 bold", fill='green',
                                    anchor='w')
            self.canvas.create_text(x + 190, y + 180, text="| Ship: " + str(shipFuel), font="Ebrima 13 bold",
                                    fill='blue', anchor='w')
            self.canvas.create_text(x + 280, y + 180, text="| Cargo: " + str(carrierFuel), font="Ebrima 13 bold",
                                    fill='orange', anchor='w')

            self.canvas.create_text(x + 400, y + 180, text="| Min: " + str(reqFuel), font="Ebrima 13 bold", fill='red',
                                    anchor='w')

            fuelTotal = tankFuel + shipFuel + carrierFuel
            if reqFuel == 'Error':
                reqFuel = 0

            width = max(fuelTotal, reqFuel) / 480

            self.canvas.create_rectangle(x + 20, y + 210, x + 20 + reqFuel / width, y + 230, fill='red', outline='red',
                                         stipple='gray25')
            self.canvas.create_rectangle(x + 20, y + 210, x + 20 + tankFuel / width, y + 230, fill='green',
                                         outline='green')

            self.canvas.create_rectangle(x + 20 + tankFuel / width, y + 210,
                                         x + 20 + shipFuel / width + tankFuel / width, y + 230, fill='blue',
                                         outline='blue')

            self.canvas.create_rectangle(x + 20 + shipFuel / width + tankFuel / width, y + 210,
                                         x + 20 + shipFuel / width + tankFuel / width + carrierFuel / width, y + 230,
                                         fill='orange', outline='orange')

            self.canvas.create_rectangle(x + 20 + reqFuel / width - 2, y + 210, x + 20 + reqFuel / width, y + 230,
                                         fill='red', outline='red')

            diff = fuelTotal - reqFuel

            if diff >= 0:
                self.canvas.create_text(x + 260, y + 250, text="You are " + str(diff) + " Tritium in excess",
                                        font="Ebrima 13 bold", fill='green')
            else:
                self.canvas.create_text(x + 260, y + 250, text="Warning! You are " + str(-diff) + " Tritium short!",
                                        font="Ebrima 13 bold", fill='red')
            self.canvas.create_text(x + 260, y + 197,
                                    text="Please note you need to open the carrier management page to update this.",
                                    font="Ebrima 8 bold", fill='orange')

            # routeList
            length = 10
            self.scrollLength = length
            verticalSpacing = 25
            self.verticalSpacing = verticalSpacing

            boxHeight = 20
            self.boxHeight = boxHeight
            startY = 290

            self.scrollHeight = verticalSpacing * (length - 1) + boxHeight

            barHeight = min(length / len(self.currentFileData) * self.scrollHeight, self.scrollHeight)
            self.barCentre = barHeight / 2
            barPosition = y + (self.position + self.scroll) / len(self.currentFileData) * self.scrollHeight + startY
            clipboard = pyperclip.paste()
            for i in range(length):
                if self.position + self.scroll + i < len(self.currentFileData):
                    if self.currentFileData[self.position + self.scroll + i][
                        self.currentFileDataKeys['System Name']] == clipboard:
                        boxFill = 'green'
                        textFill = 'black'
                    elif self.scroll + i == 0:
                        boxFill = 'orange'
                        textFill = 'black'
                    elif self.position + self.scroll + i in self.stopLocations or self.position + self.scroll + i - 1 in self.stopLocations:
                        boxFill = 'red'
                        textFill = 'black'

                    else:
                        boxFill = 'black'
                        textFill = 'orange'

                    self.canvas.create_rectangle(x + 15, y + startY + verticalSpacing * i, x + 490,
                                                 y + startY + verticalSpacing * i + boxHeight, fill=boxFill,
                                                 outline='orange')
                    self.canvas.create_text(x + 17, y + startY + verticalSpacing * i,
                                            text=self.currentFileData[self.position + self.scroll + i][
                                                self.currentFileDataKeys['System Name']], font="Ebrima 12 bold",
                                            fill=textFill, anchor='nw')
            self.canvas.create_rectangle(x + 497, y + startY, x + 505, y + startY + self.scrollHeight, fill='black',
                                         outline='orange')

            self.scrollTop = [x + 497, y + startY]
            self.scrollBottom = [x + 505, y + startY + verticalSpacing * (length - 1) + boxHeight]

            self.canvas.create_rectangle(x + 497, barPosition, x + 505, barPosition + barHeight, fill='orange',
                                         outline='orange')

            for i in self.stopLocations:
                barPosition = y + i / len(self.currentFileData) * self.scrollHeight + startY
                self.canvas.create_rectangle(x + 497, barPosition, x + 505, barPosition + 1, fill='red', outline='red')

            barPosition = y + self.position / len(self.currentFileData) * self.scrollHeight + startY
            self.canvas.create_rectangle(x + 497, barPosition, x + 505, barPosition + 1, fill='orange',
                                         outline='orange')




        except Exception as e:
            if self.debug:
                messagebox.showerror("Error", e)
            ##print('error creating dashboard',e)

            self.canvas.create_rectangle(x, y + 35, x + 520, y + 600, fill='black', outline='orange')
            self.canvas.create_text(x + 260, y + 250, text=traceback.format_exc(), font="Ebrima 13 bold", fill='red')

    def mouseDown(self, values):
        ##print(values)
        self.startDrag = time.time()
        if self.scrollTop[0] <= values.x and values.x <= self.scrollBottom[0] and self.scrollTop[1] <= values.y and \
                self.scrollBottom[1] >= values.y and not self.dragging:

            self.scrolling = True
        elif not self.scrolling:

            self.dragging = True

            self.dragOffset = [values.x - self.data['window position'][0], values.y - self.data['window position'][1]]

    def endDrag(self, values):
        self.dragging = False
        self.scrolling = False

        relX = values.x - self.data['window position'][0]
        if time.time() - self.startDrag < 0.3 and values.y - self.data['window position'][1] < 30:

            if relX < 150:
                pyperclip.copy(self.logReader.currentSystem)
                # print('copied ' + self.logReader.currentSystem + ' to clipboard')

            elif relX > 190 and relX < 340:
                pyperclip.copy(self.nextSystem)
                # print('copied ' + self.nextSystem + ' to clipboard')

            # more
            elif relX > 420 and relX < 440:
                self.data['more'] = not self.data['more']

                pass
            # open route
            elif relX > 440 and relX < 463:
                self.openFile()
            # settings
            elif relX > 463 and relX < 485:
                self.settings()
                pass

            # minimise
            elif relX > 485 and relX < 500:

                self.data['topmost'] = -self.data['topmost'] + 1
                self.createWindow()

            # close
            elif relX > 500 and relX < 520:
                self.exiting = True

            self.saveData()

        elif time.time() - self.startDrag < 0.3 and 15 < relX and 490 > relX:
            proportion = (values.y - self.scrollTop[1]) / self.scrollHeight
            clickedOn = proportion * self.scrollLength
            pyperclip.copy(self.currentFileData[math.floor(self.position + self.scroll + clickedOn)][
                               self.currentFileDataKeys['System Name']])

        self.clear()

    def wheel(self, values):

        if self.scrollLength < len(self.currentFileData):
            self.scroll += round(-values.delta / 100)
        self.limitScroll()
        self.clear()

    def limitScroll(self):
        if self.scroll + self.position < 0:
            self.scroll = -self.position
        if self.scroll + self.position >= len(self.currentFileData) - self.scrollLength:
            self.scroll = len(self.currentFileData) - self.position - self.scrollLength

    def createWindow(self, onTop=1):
        try:
            self.root.destroy()
            self.window.destroy()
        except Exception as e:
            pass
            # print('no root window exists yet')

        self.hidden = False
        user32 = ctypes.windll.user32

        width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.root = tk.Tk()
        self.root.title('routeTracker')
        self.root.attributes('-alpha', 0.0)  # For icon
        # self.root.lower()
        self.root.iconify()
        if self.data['topmost'] == 1:
            self.window = tk.Toplevel(self.root, highlightthickness=0)
        else:
            self.window = tk.Tk()
        self.window.title('routeTracker')
        self.window.config(bg="pink")
        self.window.geometry(str(width) + "x" + str(height))  # Whatever size

        if self.data['topmost'] == 1:
            self.window.overrideredirect(1)  # Remove border
            self.window.attributes('-topmost', 1)
        else:
            self.window.wm_attributes('-fullscreen', 'true')
            self.root.overrideredirect(1)

        self.window.wm_attributes("-transparentcolor", "pink")
        self.window.bind('<ButtonPress-1>', self.mouseDown)
        self.window.bind('<ButtonRelease-1>', self.endDrag)
        self.window.bind("<MouseWheel>", self.wheel)

        self.clear()

    # settings window
    def alarm(self):
        self.data['alarm'] = not self.data['alarm']
        self.saveData()
        self.alarmButton.config(text='Alarm: ' + str(self.data['alarm']))

    def logLocation(self):

        self.data['logLocation'] = askdirectory()
        # print(self.data['logLocation'])
        if self.data['logLocation'] != '':
            self.logReader.folderLocation = self.data['logLocation']
        else:
            self.logReader.defaultLocation()

        self.saveData()
        self.logLocationLabel.config(text=self.logReader.folderLocation)

    def cargoChange(self, values):
        canBeInt = False
        value = self.carrierGoodsEntry.get()
        try:
            value = int(value)
            canBeInt = True
        except Exception as e:
            if self.debug:
                messagebox.showerror("Error", e)
            pass
        if canBeInt:
            self.data['carrierCargo'] = value

        canBeInt = False
        value = self.shipGoodsEntry.get()
        try:
            value = int(value)
            canBeInt = True
        except Exception as e:
            if self.debug:
                messagebox.showerror("Error", e)
            pass
        if canBeInt:
            self.data['shipCargo'] = value

        self.saveData()

    def settings(self):
        try:
            self.settingsWindow.destroy()
        except:
            pass
            # print('settings window does not yet exist')

        self.settingsWindow = tk.Tk()
        self.settingsWindow.title('Settings')
        self.settingsWindow.config(bg='black')

        settingsLabel = tk.Label(self.settingsWindow, text='Settings\n', font="Ebrima 15 bold", fg='orange', bg='black')
        settingsLabel.grid(row=0, column=0, columnspan=2)

        # log reader file path
        openBrowserButton = tk.Button(self.settingsWindow,
                                      text='Log File Location',
                                      font="Ebrima 13 bold",
                                      fg='orange',
                                      activeforeground='orange',
                                      bg='#222222',
                                      activebackground='#111111',
                                      width=25,
                                      command=self.logLocation)
        openBrowserButton.grid(row=1, column=0)
        self.logLocationLabel = tk.Label(self.settingsWindow, text=self.logReader.folderLocation, font="Ebrima 15 bold",
                                         fg='orange', bg='black')
        self.logLocationLabel.grid(row=1, column=1)

        # alarm

        self.alarmButton = tk.Button(self.settingsWindow,
                                     text='Alarm: ' + str(self.data['alarm']),
                                     font="Ebrima 13 bold",
                                     fg='orange',
                                     activeforeground='orange',
                                     bg='#333333',
                                     activebackground='#222222',
                                     width=25,
                                     command=self.alarm)
        self.alarmButton.grid(row=2, column=0)
        # non tritium goods in carrier
        carrierGoods = tk.Button(self.settingsWindow,
                                 text='Carrier Goods',
                                 font="Ebrima 13 bold",
                                 fg='orange',
                                 activeforeground='orange',
                                 bg='#222222',
                                 activebackground='#111111',
                                 width=25,
                                 )
        carrierGoods.grid(row=3, column=0)

        self.carrierGoodsEntry = tk.Entry(self.settingsWindow, bg='#222222', fg='orange', bd=0, font="Ebrima 13 bold")
        self.carrierGoodsEntry.insert(0, str(self.data['carrierCargo']))
        self.carrierGoodsEntry.grid(row=3, column=1)
        # non tritium goods in ship
        shipGoods = tk.Button(self.settingsWindow,
                              text='Ship Goods',
                              font="Ebrima 13 bold",
                              fg='orange',
                              activeforeground='orange',
                              bg='#333333',
                              activebackground='#222222',
                              width=25,
                              )
        shipGoods.grid(row=4, column=0)

        self.shipGoodsEntry = tk.Entry(self.settingsWindow, bg='#222222', fg='orange', bd=0, font="Ebrima 13 bold")
        self.shipGoodsEntry.insert(0, str(self.data['shipCargo']))
        self.shipGoodsEntry.grid(row=4, column=1)
        # Thanks

        invite = tk.Button(self.settingsWindow,
                           text="With thanks to the Fleet Carrier Owner's Club",
                           font="Ebrima 13 bold",
                           fg='orange',
                           activeforeground='orange',
                           bg='#222222',
                           activebackground='#111111',
                           width=50,
                           command=lambda: webbrowser.open('https://discord.gg/tcMPHfh'))
        invite.grid(row=5, column=0, columnspan=2)

        self.settingsWindow.bind("<KeyRelease>", self.cargoChange)


if __name__ == '__main__':
    from routeTracker.logReader import logReader

    reader = logReader()

    ui = userInterface(reader=reader)
    # print('t')

    ui.mainLoop()

    ##print(countdownMessage)

# window.mainloop()
