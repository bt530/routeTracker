import tkinter as tk
import ctypes
#import vkmod
import time
import math
import pickle
import winsound
from tkinter.filedialog import askopenfilename,askdirectory
from tkinter import messagebox
import os
import pyperclip
import webbrowser
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_ulong), ("y", ctypes.c_ulong)]

def mousePosition():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    if pt.x== 0:
        if pt.y == 0:
            print(0/0)
    return int(pt.x),int(pt.y)
class userInterface():

    def __init__(self,reader):
        user32 = ctypes.windll.user32
        width,height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        dataTemplate={'window position':[width/2-250,height/4],'route positions':{},'showType':'show','topmost':1,'alarm':True,'logLocation':''}
        self.exiting=False
        #self.logReader=reader
        self.maxCountdown = 60 * 21
        
        self.logCheck = 30
        self.logReader=reader


        self.dragOffset=[0,0]



        
        self.countdown = self.maxCountdown
        self.countdownStart=time.time()
        self.logStart=0


        self.currentFileData = None
        self.system = None
        self.nextSystem = 'Unknown'
        self.currentFile = None

        self.position=0

        self.dragging=False
        self.draggingPos=[width/2-250,height/4]
        
        
       


        try:
            with open("trackerData.txt","rb") as f:
                self.data=pickle.load(f)
        except FileNotFoundError:
            


            
            self.data=dataTemplate
            with open("trackerData.txt","wb") as f:
                pickle.dump(self.data,f)

        added=False
        dataKeys=list(self.data.keys())
        for i in list(dataTemplate.keys()):
            if i not in dataKeys:
                self.data[i] = dataTemplate[i]
                added=True
        if added:
            with open("trackerData.txt","wb") as f:
                pickle.dump(self.data,f)

        if "current file" in list(self.data.keys()):
            self.currentFile = self.data["current file"]

            self.openFile(dialogue = False)


        if self.data['logLocation'] != '':
            self.logReader.folderLocation=self.data['logLocation']
        self.createWindow()


        """

        self.confirmed = False
        self.cSwitch='red'#

        
        self.menu=tk.Tk()
        self.menu.geometry('200x400')

        if self.data['showType'] == 'show':
            self.showButton=tk.Button(self.menu,command=self.showHide,text='Hide Overlay')
        if self.data['showType'] == 'hide':
            self.showButton=tk.Button(self.menu,command=self.showHide,text='Show Overlay')

        self.showButton.pack()

        self.openButton=tk.Button(self.menu,command=self.openFile,text="Open")

        self.openButton.pack()

        self.exButton=tk.Button(self.menu,command=self.exiting,text="Exit")
        self.exButton.pack()

        self.timerButton=tk.Button(self.menu,command=self.confirm,text='',bg='gray')

        self.timerButton.pack()
        if self.data['showType']=='show':
        """
        



    def mainLoop(self):
        topSet=-1
        timeLoop=time.time()
        while True:
            if self.exiting:
                self.saveData()
                self.window.destroy()
                self.root.destroy()
                try:
                    self.settingsWindow.destroy()
                except:
                    print('settings window does not yet exist')
                break
            #self.menu.update()
            currentTime=time.time()
            if currentTime-self.logStart > self.logCheck and self.currentFileData != None:
                self.logStart=currentTime
                self.logReader.updateLog()
                print(self.logReader.oldSystem,self.logReader.currentSystem)
                if self.logReader.oldSystem != self.logReader.currentSystem:
                    print("Jumped to "+self.logReader.currentSystem)
                    self.nextSystem='unknown'
                    for i in range(self.position,len(self.currentFileData)-1):
                        #print(i)
                        #print(ui.currentFileData[i])
                        if self.currentFileData[i][0] == self.logReader.currentSystem:
                            self.nextSystem=self.currentFileData[i+1][0]
                            pyperclip.copy(self.nextSystem)
                            print('copied ' + self.nextSystem + ' to clipboard')
                            if self.currentFileData[i+1][0] == self.currentFileData[i][0]:
                                self.position=i+1
                            else:
                                self.position=i
                            self.data['route positions'][self.currentFile] = self.position
                            self.saveData()
                            try:
                                self.clear()
                            except Exception as e:
                                print(e)
                            break


            try:
                self.root.update()
                if self.dragging:
                    x,y=mousePosition()
                    self.data['window position']=[x-self.dragOffset[0],y-self.dragOffset[1]]
                    self.clear()
                elif currentTime - timeLoop >1:
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
                    #print(topSet)
                """
                
                
            except Exception as e:
                if e == SystemExit:
                    break
                else:
                    self.exiting=True
                    print(e)

            try:
                self.settingsWindow.update()
            except:
                pass

    def showHide(self):
        if self.data['showType']=='show':
            self.data['showType']='hide'
            self.showButton.config(text='Show Overlay')
            self.saveData()
            try:
                self.close()
            except Exception as e:
                print(e)

        elif self.data['showType']=='hide':
            self.data['showType']='show'
            self.showButton.config(text='Hide Overlay')
            self.saveData()
            self.createWindow()

    def openFile(self,dialogue = True):

        if dialogue:
            self.currentFile = askopenfilename()
            self.data["current file"] = self.currentFile
        if self.currentFile != '':
            print(self.currentFile)
            print(self.data)
            if self.currentFile in list(self.data['route positions'].keys()):
                self.position = self.data['route positions'][self.currentFile]
            else:
                self.position = 0
                self.data['route positions'][self.currentFile] = self.position
            self.saveData()
            try:
                with open(self.currentFile,'r') as f:
                    self.currentFileData = f.read()


                self.currentFileData="".join(self.currentFileData.split("\""))

                self.currentFileData = self.currentFileData.split("\n")
                self.currentFileData = [i.split(",") for i in self.currentFileData]
                #print(currentFileData)
                del self.currentFileData[0]
            except FileNotFoundError as e:
                
                    messagebox.showerror("Import Error", e)
            if self.data['showType']=='show':


                self.logReader.resetValues()
                self.logStart=0


                self.createWindow()

            

    def saveData(self,values=None):

        with open("trackerData.txt","wb") as f:
            pickle.dump(self.data,f)












    #overlay functions

    def clear(self):

        #all to change with new UI

        try:

            self.canvas.destroy()
            
        except:
            pass


        clip=pyperclip.paste()

        x,y=self.data['window position'][0],self.data['window position'][1]
        
        self.canvas=tk.Canvas(self.window,bg="pink",bd=0, highlightthickness=0, relief='ridge')
        self.canvas.pack(fill="both",expand=True)


        self.canvas.create_rectangle(x,y,x+520,y+30,fill='black')
        if self.logReader.currentSystem==clip:
            self.canvas.create_text(x+5,y+5,text=self.logReader.currentSystem,font="Ebrima 13 bold",fill='green',anchor='nw')
        else:
            self.canvas.create_text(x+5,y+5,text=self.logReader.currentSystem,font="Ebrima 13 bold",fill='orange',anchor='nw')
        self.canvas.create_rectangle(x+150,y,x+500,y+30,fill='black')


        self.canvas.create_text(x+158,y+5,text='>>  ',font="Ebrima 13 bold",fill='orange',anchor='nw')

        if self.nextSystem==clip:
            self.canvas.create_text(x+190,y+5,text= self.nextSystem,font="Ebrima 13 bold",fill='green',anchor='nw')
        else:
            self.canvas.create_text(x+190,y+5,text= self.nextSystem,font="Ebrima 13 bold",fill='orange',anchor='nw')

        
        
        self.canvas.create_rectangle(x+340,y,x+500,y+30,fill='black')

        
        timeSince = time.time() -   self.logReader.lastJumpRequest
        timeSince=self.maxCountdown - timeSince
        
        if timeSince > 0:
            if timeSince < 10 and self.data['alarm']:
                winsound.Beep(3000,100)
            mins=str(round(timeSince//60))
            seconds=str(math.floor(timeSince % 60))
            if len(mins) == 1:
                mins='0'+mins
            if len(seconds) == 1:
                seconds = '0'+seconds
            text=mins+':'+seconds
        else:
            text='Ready'
        text='| '+text+' |'

        self.canvas.create_text(x+350,y+5,text=text,font="Ebrima 13 bold",fill='orange',anchor='nw')

        self.canvas.create_text(x+420,y+5,text= '☰',font="Ebrima 13 bold",fill='gray',anchor='nw')

        self.canvas.create_text(x+440,y+5,text= '📁',font="Ebrima 13 bold",fill='orange',anchor='nw')

        self.canvas.create_text(x+463,y+5,text= '⚙',font="Ebrima 13 bold",fill='orange',anchor='nw')
        if self.data['topmost']==1:
            self.canvas.create_text(x+485,y+5,text= '⮝',font="Ebrima 13 bold",fill='orange',anchor='nw')
        
        else:
            self.canvas.create_text(x+485,y+5,text= '⮟',font="Ebrima 13 bold",fill='orange',anchor='nw')

        self.canvas.create_text(x+500,y+5,text= '✘',font="Ebrima 13 bold",fill='orange',anchor='nw')

        self.canvas.create_line(x,y,x+520,y,fill='orange')
        self.canvas.create_line(x,y+30,x+520,y+30,fill='orange')

        
        

        """
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
        """
        """
        numberLabel=tk.Button(canvas,text="Jump Number: ")
        numberLabel.pack(anchor="nw",side="left")

        global number
        number=tk.Entry(canvas)
        number.pack(anchor="nw",side="left")
        """
    def drag(self,values):
        #print(values)
        self.dragging=True
        self.startDrag=time.time()
        
        self.dragOffset=[values.x-self.data['window position'][0],values.y-self.data['window position'][1]]


            
        
    def endDrag(self,values):
        self.dragging=False
       

    
        if time.time()-self.startDrag < 0.3 and values.y - self.data['window position'][1] < 30:
            relX = values.x - self.data['window position'][0]
            if relX < 150:
                pyperclip.copy(self.logReader.currentSystem)
                print('copied ' + self.logReader.currentSystem + ' to clipboard')
                
            elif relX > 190 and relX <340:
                pyperclip.copy(self.nextSystem)
                print('copied ' + self.nextSystem + ' to clipboard')
                
            #list all jumps
            elif relX > 420 and relX <440:
                pass
            #open route
            elif relX > 440 and relX <463:
                self.openFile()
            #settings
            elif relX > 463 and relX <485:
                self.settings()
                pass

            #minimise
            elif relX > 485 and relX <500:
                
                
                self.data['topmost']=-self.data['topmost']+1
                self.createWindow()
                
            #close
            elif relX > 500 and relX <520:
                self.exiting=True
                
                
                pass
        self.clear()
        self.saveData()
    
    def createWindow(self,onTop=1):
        try:
            self.root.destroy()
            self.window.destroy()
        except Exception as e:
            
            print('no root window exists yet')

        self.hidden=False
        user32 = ctypes.windll.user32


        width,height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.root = tk.Tk()
        self.root.title('routeTracker')
        self.root.attributes('-alpha', 0.0) #For icon
        #self.root.lower()
        self.root.iconify()
        if self.data['topmost'] == 1:
            self.window = tk.Toplevel(self.root,highlightthickness=0)
        else:
            self.window = tk.Tk()
        self.window.title('routeTracker')    
        self.window.config(bg="pink")
        self.window.geometry(str(width)+"x"+str(height)) #Whatever size
        
        
        if self.data['topmost'] == 1:
            self.window.overrideredirect(1) #Remove border
            self.window.attributes('-topmost', 1)
        else:
            self.window.wm_attributes('-fullscreen','true')
            self.root.overrideredirect(1)
        
        self.window.wm_attributes("-transparentcolor", "pink")
        self.window.bind('<ButtonPress-1>',self.drag)
        self.window.bind('<ButtonRelease-1>',self.endDrag)
        


        self.clear()


    #settings window
    def alarm(self):
        self.data['alarm']=not self.data['alarm']
        self.saveData()
        self.alarmButton.config(text='Alarm: '+ str(self.data['alarm']))
    def logLocation(self):


        self.data['logLocation'] = askdirectory()
        print(self.data['logLocation'])
        if self.data['logLocation'] != '':
            self.logReader.folderLocation=self.data['logLocation']
        else:
            self.logReader.defaultLocation()

        self.saveData()
        self.logLocationLabel.config(text=self.logReader.folderLocation)
    def settings(self):
        try:
            self.settingsWindow.destroy()
        except:
            print('settings window does not yet exist')

        self.settingsWindow=tk.Tk()
        self.settingsWindow.title('Settings')
        self.settingsWindow.config(bg='black')
        

        
        settingsLabel=tk.Label(self.settingsWindow,text='Settings\n',font="Ebrima 15 bold",fg='orange',bg='black')
        settingsLabel.grid(row=0,column=0,columnspan = 2)

        #log reader file path
        openBrowserButton=tk.Button(self.settingsWindow,
                                   text='Log File Location',
                                   font="Ebrima 13 bold",
                                   fg='orange',
                                   activeforeground='orange',
                                   bg='#222222',
                                   activebackground='#111111',
                                   width=25,
                                   command=self.logLocation)
        openBrowserButton.grid(row=1,column=0)
        self.logLocationLabel=tk.Label(self.settingsWindow,text=self.logReader.folderLocation,font="Ebrima 15 bold",fg='orange',bg='black')
        self.logLocationLabel.grid(row=1,column=1)

        #alarm
        
        self.alarmButton=tk.Button(self.settingsWindow,
                                   text='Alarm: '+ str(self.data['alarm']),
                                   font="Ebrima 13 bold",
                                   fg='orange',
                                   activeforeground='orange',
                                   bg='#333333',
                                   activebackground='#222222',
                                   width=25,
                                   command=self.alarm)
        self.alarmButton.grid(row=2,column=0)
        #non tritium goods in carrier
        carrierGoods=tk.Button(self.settingsWindow,
                                   text='Carrier Goods',
                                   font="Ebrima 13 bold",
                                   fg='orange',
                                   activeforeground='orange',
                                   bg='#222222',
                                   activebackground='#111111',
                                   width=25,
                                   )
        carrierGoods.grid(row=3,column=0)

        self.carrierGoodsEntry=tk.Entry(self.settingsWindow,bg='#222222',fg='orange',bd=0,font="Ebrima 13 bold")
        self.carrierGoodsEntry.insert ( 0, '0' )
        self.carrierGoodsEntry.grid(row=3,column=1)
        #non tritium goods in ship
        shipGoods=tk.Button(self.settingsWindow,
                                   text='Ship Goods',
                                   font="Ebrima 13 bold",
                                   fg='orange',
                                   activeforeground='orange',
                                   bg='#333333',
                                   activebackground='#222222',
                                   width=25,
                                   )
        shipGoods.grid(row=4,column=0)
        #Thanks
        
        
        invite=tk.Button(self.settingsWindow,
                                   text="With thanks to the Fleet Carrier Owner's Club",
                                   font="Ebrima 13 bold",
                                   fg='orange',
                                   activeforeground='orange',
                                   bg='#222222',
                                   activebackground='#111111',
                                   width=50,
                                   command=lambda: webbrowser.open('https://discord.gg/tcMPHfh'))
        invite.grid(row=5,column=0,columnspan=2)






if __name__ == '__main__':
    from logReader import *
    
    reader=logReader()

    ui=userInterface(reader=reader)
    print('t')

    ui.mainLoop()

        





    #print(countdownMessage)

#window.mainloop()
