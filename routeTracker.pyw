import tkinter as tk
import ctypes
#import vkmod
import time
import pyperclip
import pickle
import winsound
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from PIL import ImageTk, Image
def openFile(dialogue = True):
    global currentFile
    global currentFileData
    global position
    global data
    if dialogue:
        currentFile = askopenfilename()
        data["current file"] = currentFile
    print(currentFile)
    if currentFile in list(data.keys()):
        position = data[currentFile]
    else:
        position = 0
        data[currentFile] = position
    saveData()
    try:
        with open(currentFile,'r') as f:
            currentFileData = f.read()


        currentFileData="".join(currentFileData.split("\""))

        currentFileData = currentFileData.split("\n")
        currentFileData = [i.split(",") for i in currentFileData]
        #print(currentFileData)
        del currentFileData[0]
    except Exception as e:
        messagebox.showerror("Import Error", e)
    if dialogue:
        clear()
    
    pass
def saveData():
    global data
    with open("trackerData.txt","wb") as f:
        pickle.dump(data,f)




def exiting():

    root.destroy()
    exit()

def hide():
    global hidden
    hidden=True
    print(hidden)
    root.destroy()

def confirm():
    global confirmed
    confirmed = True

def left():
    global position
    global data
    global currentFile
    if position > 0:
        position -= 1
        data[currentFile] = position
        saveData()
        clear()
    pass
def right():
    global position
    global data
    global currentFile
    if position < len(currentFileData) -1:
        position += 1
        data[currentFile] = position
        saveData()
        clear()
    pass
def jump():
    global position
    global data
    global currentFileData
    global currentFile
    if position < len(currentFileData) -1:
        position += 1
        data[currentFile] = position
        if currentFileData != "None":
            pyperclip.copy(currentFileData[position][0])
        saveData()
        clear()
    global start
    start=time.time()

    global confirmed
    confirmed = False

def clear():
    global canvas

    try:

        canvas.destroy()
        
    except:
        pass

    global system
    global currentFileData
    global position


    if currentFileData != "None":
        if position >= len(currentFileData):
            position = len(currentFileData) - 1
        system=currentFileData[position][0]
    
    canvas=tk.Canvas(window,bg="pink",bd=0, highlightthickness=0, relief='ridge')
    canvas.pack(fill="both",expand=True)


    

    exButton=tk.Button(canvas,command=exiting,text="Exit")

    exButton.pack(anchor="nw",side="left")


    hideButton=tk.Button(canvas,command=hide,text="Hide")

    hideButton.pack(anchor="nw",side="left")



    openButton=tk.Button(canvas,command=openFile,text="Open")

    openButton.pack(anchor="nw",side="left")

    leftButton=tk.Button(canvas,command=left,text="<---")

    leftButton.pack(anchor="nw",side="left")
    
    systemButton=tk.Button(canvas,command=jump,text=system)

    systemButton.pack(anchor="nw",side="left")

    rightButton=tk.Button(canvas,command=right,text="--->")

    rightButton.pack(anchor="nw",side="left")
    if currentFileData != "None":
        jumpsDone = str(position)
        jumpsLeft = str(len(currentFileData) - position)
        distance = str(round(float(currentFileData[position][2])))
        tankFuel = str(currentFileData[position][3])
        cargoFuel = str(currentFileData[position][4])
        message="Jumps Done: "  + jumpsDone + " | Jumps Left: " + jumpsLeft + " | Distance Remaining: " + distance + " | Fuel in Tank: " + tankFuel + " | Fuel in Cargo: " + cargoFuel
        
        
        numberLabel=tk.Button(canvas,text=message)
        numberLabel.pack(anchor="nw",side="left")
    
    global timerButton
    timerButton=tk.Button(canvas,command=confirm,text='',bg='gray')

    timerButton.pack(anchor="nw",side="left")
    """
    numberLabel=tk.Button(canvas,text="Jump Number: ")
    numberLabel.pack(anchor="nw",side="left")

    global number
    number=tk.Entry(canvas)
    number.pack(anchor="nw",side="left")
    """

def createWindow():
    global hidden
    global root
    global window
    hidden=False
    user32 = ctypes.windll.user32


    width,height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    root = tk.Tk()
    root.attributes('-alpha', 0.0) #For icon
    root.lower()
    root.iconify()
    window = tk.Toplevel(root)
    window.config(bg="pink")
    window.geometry(str(width)+"x"+str(height)) #Whatever size
    window.overrideredirect(1) #Remove border
    window.attributes('-topmost', 1)
    window.wm_attributes("-transparentcolor", "pink")




global canvas
global root
global window
global countdown
maxCountdown = 60 * 21
countdown = maxCountdown

global currentFile
global currentFileData
currentFileData = "None"

global system
system = "None"
currentFile = "None"

global data
global position
position = 0
try:
    with open("trackerData.txt","rb") as f:
        data=pickle.load(f)
except:
    data={}
    with open("trackerData.txt","wb") as f:
        pickle.dump(data,f)




#width-=40
#height-=20
global hidden
hidden=False
createWindow()
if "current file" in list(data.keys()):
    currentFile = data["current file"]

    openFile(dialogue = False)




clear()
global start
start=time.time()
global timerButton
global confirmed
confirmed = False
cSwitch='red'




while True:
    
    countdown = maxCountdown - (time.time() - start)
    if countdown < 30 and hidden:
        createWindow()
        clear()
    elif not hidden:
        try:
            #print(hidden)
            window.update()
            if countdown <0:
                pre='-'
            else:
                pre=''
            tens=str(round(abs(countdown) // 60))
            units=str(round(abs(countdown) % 60))
            if len(tens)==1:
                tens='0'+tens
            if len(units)==1:
                units='0'+units
            countdownMessage = pre + tens + ":" + units
            if countdown < 0 and countdown % 2 < 1:

                if cSwitch == 'grey':
                    
                    timerButton.config(bg='red')
                    if not confirmed:
                        winsound.Beep(4000, 500)
                    cSwitch = 'red'
            elif cSwitch == 'red':
                timerButton.config(bg='gray')
                cSwitch = 'grey'
            timerButton.config(text=countdownMessage)
        except Exception as e:
            print(e)
    #print(countdownMessage)

#window.mainloop()
