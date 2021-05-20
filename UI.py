import tkinter as tk
import ctypes
import logging
import time
import math
import pickle
import winsound
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import messagebox
import pyperclip
import webbrowser
import traceback

START_Y = 290

BOX_HEIGHT = 20
VERTICAL_SPACING = 25
SCROLL_LENGTH = 10

TRACKER_DATA_TXT = "trackerData.txt"


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_ulong), ("y", ctypes.c_ulong)]


def pickle_data(data_template):
    try:
        with open(TRACKER_DATA_TXT, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        with open(TRACKER_DATA_TXT, "wb") as f:
            pickle.dump(data_template, f)
            return data_template


def mouse_position():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return int(pt.x), int(pt.y)


class UserInterface:

    def __init__(self, log_reader):
        self.log = logging.getLogger(__name__)
        user32 = ctypes.windll.user32
        width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        data_template = {'window position': [width / 2 - 250, height / 4], 'route positions': {}, 'showType': 'show',
                         'topmost': 1, 'alarm': True, 'logLocation': '', 'shipCargo': 0, 'carrierCargo': 0,
                         'more': False}
        self.exiting = False
        self.maxCountdown = 60 * 21

        self.logCheck = 30
        self.logReader = log_reader

        self.canvas = None
        self.root = None
        self.window = None
        self.settingsWindow = None
        self.hidden = False
        self.scroll = 0
        self.scrollHeight = VERTICAL_SPACING * (SCROLL_LENGTH - 1) + BOX_HEIGHT
        self.dragOffset = [0, 0]
        self.barCentre = None
        self.scrolling = False
        self.startDrag = None
        self.alarmButton = None
        self.logLocationLabel = None
        self.carrierGoodsEntry = None
        self.shipGoodsEntry = None

        self.stopLocations = []

        self.countdown = self.maxCountdown
        self.countdownStart = time.time()
        self.logStart = 0

        self.currentFileData = [['unknown']]
        self.system = None
        self.nextSystem = 'unknown'
        self.currentFile = None

        self.position = 0

        self.dragging = False
        self.draggingPos = [width / 2 - 250, height / 4]

        self.scrollTop = [0, 0]
        self.scrollBottom = [0, 0]

        self.data = pickle_data(data_template)
        self.add_missing_data_from_template(data_template)

        if "current file" in list(self.data.keys()):
            self.currentFile = self.data["current file"]

            self.open_file(dialogue=False)

        if self.data['logLocation'] != '':
            self.logReader.folder_location = self.data['logLocation']
        self.create_window()

    def add_missing_data_from_template(self, data_template):
        added = False
        data_keys = list(self.data.keys())
        for i in list(data_template.keys()):
            if i not in data_keys:
                self.data[i] = data_template[i]
                added = True
        if added:
            self.save_data()

    def main_loop(self):
        time_loop = time.time()
        while True:
            time.sleep(0.01)
            try:
                pyperclip.paste()
                if self.exiting:
                    self.save_data()
                    self.destroy_windows()

                    break
                current_time = time.time()
                if current_time - self.logStart > self.logCheck and self.currentFileData is not None:
                    self.logStart = current_time
                    try:
                        self.logReader.update_log()
                    except Exception:
                        self.log.exception("Error updating log!")
                        messagebox.showerror("Error updating logs.",
                                             "There was an error updating the CMDR logs."
                                             " See routeTracker.log for details")
                        pass
                    self.log.debug('Old system: %s, current system: %s', self.logReader.route_data.oldSystem,
                                   self.logReader.route_data.currentSystem)
                    if self.logReader.route_data.oldSystem != self.logReader.route_data.currentSystem:
                        self.log.info("Jumped to " + self.logReader.route_data.currentSystem)
                        self.nextSystem = 'unknown'
                        for i in range(self.position, len(self.currentFileData) - 1):
                            self.log.debug(i)
                            self.log.debug(ui.currentFileData[i])
                            if self.currentFileData[i][0] == self.logReader.route_data.currentSystem:

                                self.log.info('copied ' + self.nextSystem + ' to clipboard')
                                if self.currentFileData[i + 1][0] == self.currentFileData[i][0]:
                                    self.position = i + 1
                                    self.log.debug('double')
                                else:
                                    self.position = i
                                self.nextSystem = self.currentFileData[self.position + 1][0]
                                pyperclip.copy(self.nextSystem)
                                self.data['route positions'][self.currentFile] = self.position
                                self.save_data()
                                self.clear()
                                break
                import _tkinter
                try:
                    self.root.update()

                    x, y = mouse_position()
                    if self.dragging:

                        self.data['window position'] = [x - self.dragOffset[0], y - self.dragOffset[1]]
                        self.clear()
                    elif self.scrolling and SCROLL_LENGTH < len(self.currentFileData):
                        proportion = (y - self.barCentre - self.scrollTop[1]) / self.scrollHeight
                        self.scroll = round(proportion * len(self.currentFileData) - self.position)
                        if self.scroll + self.position < 0:
                            self.scroll = -self.position
                        if self.scroll + self.position >= len(self.currentFileData) - SCROLL_LENGTH:
                            self.scroll = len(self.currentFileData) - self.position - 1 - SCROLL_LENGTH
                        self.clear()
                    elif current_time - time_loop > 1:
                        self.clear()
                        time_loop = current_time

                    self.settingsWindow.update()
                except AttributeError:
                    # window does not exist yet
                    pass
                except _tkinter.TclError:
                    # window has already been destroyed
                    pass
                except Exception:
                    self.log.exception("Error updating settingsWindow")
                    pass
            except pyperclip.PyperclipWindowsException:
                self.log.debug("PyperclipWindowsException")
                time.sleep(2)

    def destroy_windows(self):
        if self.window is not None:
            self.window.destroy()
        if self.root is not None:
            self.root.destroy()
        if self.settingsWindow is not None:
            self.settingsWindow.destroy()

    def open_file(self, dialogue=True):
        self.scroll = 0
        if dialogue:
            self.currentFile = askopenfilename()
            self.data["current file"] = self.currentFile
        if self.currentFile != '':
            self.log.debug('Current file: ' + self.currentFile)
            self.log.debug('Data: ' + self.data)
            if self.currentFile in list(self.data['route positions'].keys()):
                self.position = self.data['route positions'][self.currentFile]
            else:
                self.position = 0
                self.data['route positions'][self.currentFile] = self.position
            self.save_data()
            try:
                with open(self.currentFile, 'r') as f:
                    self.currentFileData = f.read()

                self.currentFileData = "".join(self.currentFileData.split("\""))

                self.currentFileData = self.currentFileData.split("\n")
                self.currentFileData = [i.split(",") for i in self.currentFileData]
                self.log.debug('Current file data: ' + str(self.currentFileData))
                del self.currentFileData[0]

                self.stopLocations = []
                for i in range(len(self.currentFileData) - 1):
                    if self.currentFileData[i][0] == self.currentFileData[i + 1][0]:
                        self.stopLocations.append(i)
                    self.log.debug('Current file data at i=%d: ' + str(self.currentFileData[i]), i)
                self.log.debug('StopLocations: ' + str(self.stopLocations))
            except FileNotFoundError as e:
                self.log.exception("Import Error")
                messagebox.showerror("Import Error", e)
            if self.data['showType'] == 'show':
                self.logReader.route_data = RouteData()
                self.logStart = 0

                self.create_window()

    def save_data(self):
        self.log.info('Saving routeTracker data')
        with open(TRACKER_DATA_TXT, "wb") as f:
            pickle.dump(self.data, f)

    # overlay functions

    def clear(self):

        # all to change with new UI

        try:
            self.canvas.destroy()
        except Exception:
            self.log.debug("Exception during canvas destroy")
            pass

        clip = pyperclip.paste()

        x, y = self.data['window position'][0], self.data['window position'][1]

        self.canvas = tk.Canvas(self.window, bg="pink", bd=0, highlightthickness=0, relief='ridge')
        self.canvas.pack(fill="both", expand=True)

        self.canvas.create_rectangle(x, y, x + 520, y + 30, fill='black')
        if self.logReader.route_data.currentSystem == clip:
            self.canvas.create_text(x + 5, y + 5, text=self.logReader.route_data.currentSystem, font="Ebrima 13 bold",
                                    fill='green', anchor='nw')
        else:
            self.canvas.create_text(x + 5, y + 5, text=self.logReader.route_data.currentSystem, font="Ebrima 13 bold",
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

        time_since = time.time() - self.logReader.route_data.lastJumpRequest
        time_since = self.maxCountdown - time_since

        if time_since > 0:
            if time_since < 10 and self.data['alarm']:
                winsound.Beep(3000, 100)
            minutes = str(round(time_since // 60))
            seconds = str(math.floor(time_since % 60))
            if len(minutes) == 1:
                minutes = '0' + minutes
            if len(seconds) == 1:
                seconds = '0' + seconds
            text = minutes + ':' + seconds
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
            self.create_dashboard()

    def create_dashboard(self):

        x, y = self.data['window position'][0], self.data['window position'][1]
        try:

            self.canvas.create_rectangle(x, y + 35, x + 520, y + 600, fill='black', outline='orange')

            # panel backgrounds
            self.canvas.create_rectangle(x + 10, y + 40, x + 510, y + 150, fill='#111111', outline='#333333')

            self.canvas.create_rectangle(x + 10, y + 160, x + 510, y + 270, fill='#111111', outline='#333333')

            self.canvas.create_rectangle(x + 10, y + 280, x + 510, y + 540, fill='#111111', outline='#333333')

            above = True
            for i in [0] + self.stopLocations:
                hor_pos = i / len(self.currentFileData) * 480 + 20
                if above:

                    self.canvas.create_rectangle(x + hor_pos - 8, y + 45, x + 500, y + 80, fill='#111111',
                                                 outline='#111111')
                    self.canvas.create_line(x + hor_pos, y + 70, x + hor_pos, y + 80, fill='orange')
                    self.canvas.create_text(x + hor_pos, y + 60, text=self.currentFileData[i][0] + "   ",
                                            font="Ebrima 8 bold", fill='orange', anchor='w')
                else:

                    self.canvas.create_rectangle(x + hor_pos - 8, y + 80, x + 500, y + 120, fill='#111111',
                                                 outline='#111111')
                    self.canvas.create_line(x + hor_pos, y + 80, x + hor_pos, y + 90, fill='orange')
                    self.canvas.create_text(x + hor_pos, y + 95, text=self.currentFileData[i][0] + "   ",
                                            font="Ebrima 8 bold", fill='orange', anchor='w')

                above = not above
            hor_pos = 500
            if above:
                self.canvas.create_rectangle(x + hor_pos - 10, y + 45, x + 500, y + 80, fill='#111111',
                                             outline='#111111')
                self.canvas.create_line(x + hor_pos, y + 70, x + hor_pos, y + 80, fill='orange')
                self.canvas.create_text(x + hor_pos, y + 60, text="   " + self.currentFileData[-2][0],
                                        font="Ebrima 8 bold", fill='orange', anchor='e')
            else:
                self.canvas.create_rectangle(x + hor_pos - 10, y + 80, x + 500, y + 120, fill='#111111',
                                             outline='#111111')
                self.canvas.create_line(x + hor_pos, y + 80, x + hor_pos, y + 90, fill='orange')
                self.canvas.create_text(x + hor_pos, y + 95, text="   " + self.currentFileData[-2][0],
                                        font="Ebrima 8 bold", fill='orange', anchor='e')
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
            self.canvas.create_text(x + 380, y + 130, text="| Left: " + str(len(self.currentFileData) - self.position),
                                    font="Ebrima 13 bold", fill='orange', anchor='w')
            for i in self.stopLocations:
                hor_pos = i / len(self.currentFileData) * 480 + 20
                self.canvas.create_oval(x + hor_pos - 3, y + 77, x + hor_pos + 3, y + 83, fill='orange',
                                        outline='orange')
            hor_pos = self.position / len(self.currentFileData) * 480 + 20
            self.canvas.create_polygon(x + hor_pos - 5, y + 85, x + hor_pos, y + 75, x + hor_pos + 5, y + 85,
                                       fill='#00ff00', outline='#00ff00')

            req_fuel = self.currentFileData[self.position][4]

            req_fuel = int(req_fuel)
            if req_fuel > 0:
                req_fuel += 1000
            else:
                for i in range(self.position, len(self.currentFileData)):
                    req_fuel += int(self.currentFileData[i][5])
                req_fuel -= int(self.currentFileData[self.position][5])

            tank_fuel = self.logReader.route_data.carrierFuel
            ship_fuel = self.logReader.route_data.shipInventory - self.data['shipCargo']
            carrier_fuel = self.logReader.route_data.carrierInventory - self.data['carrierCargo']
            self.canvas.create_text(x + 20, y + 180, text="Tritium | ", font="Ebrima 13 bold", fill='orange',
                                    anchor='w')
            self.canvas.create_text(x + 95, y + 180, text="Tank: " + str(tank_fuel), font="Ebrima 13 bold",
                                    fill='green', anchor='w')
            self.canvas.create_text(x + 190, y + 180, text="| Ship: " + str(ship_fuel), font="Ebrima 13 bold",
                                    fill='blue', anchor='w')
            self.canvas.create_text(x + 280, y + 180, text="| Cargo: " + str(carrier_fuel), font="Ebrima 13 bold",
                                    fill='orange', anchor='w')

            self.canvas.create_text(x + 400, y + 180, text="| Min: " + str(req_fuel), font="Ebrima 13 bold", fill='red',
                                    anchor='w')

            fuel_total = tank_fuel + ship_fuel + carrier_fuel

            width = max(fuel_total, req_fuel) / 480

            self.canvas.create_rectangle(x + 20, y + 210, x + 20 + req_fuel / width, y + 230, fill='red', outline='red',
                                         stipple='gray25')
            self.canvas.create_rectangle(x + 20, y + 210, x + 20 + tank_fuel / width, y + 230, fill='green',
                                         outline='green')

            self.canvas.create_rectangle(x + 20 + tank_fuel / width, y + 210,
                                         x + 20 + ship_fuel / width + tank_fuel / width, y + 230, fill='blue',
                                         outline='blue')

            self.canvas.create_rectangle(x + 20 + ship_fuel / width + tank_fuel / width, y + 210,
                                         x + 20 + ship_fuel / width + tank_fuel / width + carrier_fuel / width, y + 230,
                                         fill='orange', outline='orange')

            self.canvas.create_rectangle(x + 20 + req_fuel / width - 2, y + 210, x + 20 + req_fuel / width, y + 230,
                                         fill='red', outline='red')

            diff = fuel_total - req_fuel

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

            bar_height = min(SCROLL_LENGTH / len(self.currentFileData) * self.scrollHeight, self.scrollHeight)
            self.barCentre = bar_height / 2
            bar_position = y + (self.position + self.scroll) / len(self.currentFileData) * self.scrollHeight + START_Y

            for i in range(SCROLL_LENGTH):
                if self.position + self.scroll + i < len(self.currentFileData) - 1:
                    if self.currentFileData[self.position + self.scroll + i][0] == pyperclip.paste():
                        box_fill = 'green'
                        text_fill = 'black'
                    elif self.scroll + i == 0:
                        box_fill = 'orange'
                        text_fill = 'black'
                    elif self.position + self.scroll + i in self.stopLocations \
                            or self.position + self.scroll + i - 1 in self.stopLocations:
                        box_fill = 'red'
                        text_fill = 'black'

                    else:
                        box_fill = 'black'
                        text_fill = 'orange'

                    self.canvas.create_rectangle(x + 15, y + START_Y + VERTICAL_SPACING * i, x + 490,
                                                 y + START_Y + VERTICAL_SPACING * i + BOX_HEIGHT, fill=box_fill,
                                                 outline='orange')
                    self.canvas.create_text(x + 17, y + START_Y + VERTICAL_SPACING * i,
                                            text=self.currentFileData[self.position + self.scroll + i][0],
                                            font="Ebrima 12 bold", fill=text_fill, anchor='nw')
            self.canvas.create_rectangle(x + 497, y + START_Y, x + 505, y + START_Y + self.scrollHeight, fill='black',
                                         outline='orange')

            self.scrollTop = [x + 497, y + START_Y]
            self.scrollBottom = [x + 505, y + START_Y + VERTICAL_SPACING * (SCROLL_LENGTH - 1) + BOX_HEIGHT]

            self.canvas.create_rectangle(x + 497, bar_position, x + 505, bar_position + bar_height, fill='orange',
                                         outline='orange')

            for i in self.stopLocations:
                bar_position = y + i / len(self.currentFileData) * self.scrollHeight + START_Y
                self.canvas.create_rectangle(x + 497, bar_position, x + 505, bar_position + 1, fill='red',
                                             outline='red')

            bar_position = y + self.position / len(self.currentFileData) * self.scrollHeight + START_Y
            self.canvas.create_rectangle(x + 497, bar_position, x + 505, bar_position + 1, fill='orange',
                                         outline='orange')

        except IndexError:
            self.log.debug("No data to display")
            self.canvas.create_rectangle(x, y + 35, x + 520, y + 600, fill='black', outline='orange')
        except Exception:
            self.log.exception("Error creating dashboard")

            self.canvas.create_rectangle(x, y + 35, x + 520, y + 600, fill='black', outline='orange')

    def mouse_down(self, values):
        self.startDrag = time.time()
        if self.scrollTop[0] <= values.x <= self.scrollBottom[0] \
                and self.scrollTop[1] <= values.y <= self.scrollBottom[1] \
                and not self.dragging:

            self.scrolling = True
        elif not self.scrolling:

            self.dragging = True

            self.dragOffset = [values.x - self.data['window position'][0], values.y - self.data['window position'][1]]

    def end_drag(self, values):
        self.dragging = False
        self.scrolling = False

        rel_x = values.x - self.data['window position'][0]
        if time.time() - self.startDrag < 0.3 and values.y - self.data['window position'][1] < 30:

            if rel_x < 150:
                pyperclip.copy(self.logReader.route_data.currentSystem)
                self.log.info('Copied ' + self.logReader.route_data.currentSystem + ' to clipboard')

            elif 190 < rel_x < 340:
                pyperclip.copy(self.nextSystem)
                self.log.info('Copied ' + self.nextSystem + ' to clipboard')

            # more
            elif 420 < rel_x < 440:
                self.data['more'] = not self.data['more']

                pass
            # open route
            elif 440 < rel_x < 463:
                self.open_file()
            # settings
            elif 463 < rel_x < 485:
                self.settings()
                pass

            # minimise
            elif 485 < rel_x < 500:

                self.data['topmost'] = -self.data['topmost'] + 1
                self.create_window()

            # close
            elif 500 < rel_x < 520:
                self.exiting = True

            self.save_data()

        elif time.time() - self.startDrag < 0.3 and 15 < rel_x < 490:
            proportion = (values.y - self.scrollTop[1]) / self.scrollHeight
            clicked_on = proportion * SCROLL_LENGTH
            pyperclip.copy(self.currentFileData[math.floor(self.position + self.scroll + clicked_on)][0])

        self.clear()

    def wheel(self, values):

        if SCROLL_LENGTH < len(self.currentFileData):
            self.scroll += round(-values.delta / 100)
            if self.scroll + self.position < 0:
                self.scroll = -self.position
            if self.scroll + self.position >= len(self.currentFileData) - SCROLL_LENGTH:
                self.scroll = len(self.currentFileData) - self.position - 1 - SCROLL_LENGTH
            self.clear()

    def create_window(self):
        import _tkinter
        try:
            self.root.destroy()
            self.window.destroy()
        except _tkinter.TclError:
            # window has already been destroyed
            pass

        except AttributeError:
            self.log.debug('no root window exists yet')

        self.hidden = False
        user32 = ctypes.windll.user32

        width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.root = tk.Tk()
        self.root.title('routeTracker')
        self.root.attributes('-alpha', 0.0)  # For icon
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
        self.window.bind('<ButtonPress-1>', self.mouse_down)
        self.window.bind('<ButtonRelease-1>', self.end_drag)
        self.window.bind("<MouseWheel>", self.wheel)

        self.clear()

    # settings window
    def alarm(self):
        self.data['alarm'] = not self.data['alarm']
        self.save_data()
        self.alarmButton.config(text='Alarm: ' + str(self.data['alarm']))

    def log_location(self):

        self.data['logLocation'] = askdirectory()
        self.log.debug(self.data['logLocation'])
        if self.data['logLocation'] != '':
            self.logReader.folder_location = self.data['logLocation']
        else:
            self.logReader.default_location()

        self.save_data()
        self.logLocationLabel.config(text=self.logReader.folder_location)

    def cargo_change(self, values):
        can_be_int = False
        value = self.carrierGoodsEntry.get()
        try:
            value = int(value)
            can_be_int = True
        except Exception:
            self.log.exception("Error processing carrier goods")
            pass
        if can_be_int:
            self.data['carrierCargo'] = value

        can_be_int = False
        value = self.shipGoodsEntry.get()
        try:
            value = int(value)
            can_be_int = True
        except Exception:
            self.log.exception("Error processing carrier goods")
            pass
        if can_be_int:
            self.data['shipCargo'] = value

        self.save_data()

    def settings(self):
        try:
            self.settingsWindow.destroy()
        except AttributeError:
            self.log.debug('Settings window does not exist yet')

        self.settingsWindow = tk.Tk()
        self.settingsWindow.title('Settings')
        self.settingsWindow.config(bg='black')

        settings_label = tk.Label(self.settingsWindow, text='Settings\n', font="Ebrima 15 bold", fg='orange',
                                  bg='black')
        settings_label.grid(row=0, column=0, columnspan=2)

        # log reader file path
        open_browser_button = tk.Button(self.settingsWindow,
                                        text='Log File Location',
                                        font="Ebrima 13 bold",
                                        fg='orange',
                                        activeforeground='orange',
                                        bg='#222222',
                                        activebackground='#111111',
                                        width=25,
                                        command=self.log_location)
        open_browser_button.grid(row=1, column=0)
        self.logLocationLabel = tk.Label(self.settingsWindow, text=self.logReader.folder_location,
                                         font="Ebrima 15 bold",
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
        carrier_goods = tk.Button(self.settingsWindow,
                                  text='Carrier Goods',
                                  font="Ebrima 13 bold",
                                  fg='orange',
                                  activeforeground='orange',
                                  bg='#222222',
                                  activebackground='#111111',
                                  width=25,
                                  )
        carrier_goods.grid(row=3, column=0)

        self.carrierGoodsEntry = tk.Entry(self.settingsWindow, bg='#222222', fg='orange', bd=0, font="Ebrima 13 bold")
        self.carrierGoodsEntry.insert(0, str(self.data['carrierCargo']))
        self.carrierGoodsEntry.grid(row=3, column=1)
        # non tritium goods in ship
        ship_goods = tk.Button(self.settingsWindow,
                               text='Ship Goods',
                               font="Ebrima 13 bold",
                               fg='orange',
                               activeforeground='orange',
                               bg='#333333',
                               activebackground='#222222',
                               width=25,
                               )
        ship_goods.grid(row=4, column=0)

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

        self.settingsWindow.bind("<KeyRelease>", self.cargo_change)


if __name__ == '__main__':
    from LogReader import *

    ui = UserInterface(log_reader=LogReader())
    ui.main_loop()
