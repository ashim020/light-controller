from ctypes.wintypes import HWND
from statistics import mode
from tkinter import *
from turtle import clear, color, width
from PIL import ImageTk, Image
from ctypes import windll
from apscheduler.schedulers.background import BackgroundScheduler
import time
import socket
import json
# Importing Libraries
import serial
import time
import tkinter
import tkinter.messagebox
import customtkinter
import os

global pickedColor
global patternMode
global blendingMode
global motionMode
global LEDStatus
global LEDbrightness
global brightnessMenu
global data

#hi

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

PATH = os.path.dirname(os.path.realpath(__file__))

class LightController(customtkinter.CTk):

    WIDTH = 840
    HEIGHT = 750
    button_val = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.r = 0xFF
        self.g = 0xFF
        self.b = 0xFF
        
        self.data = {'pickedcolordic':pickedColor,'patternModedic': patternMode,'blendingModedic': blendingMode, 'motionModedic':motionMode,'LEDStatusdic': LEDStatus, 'LEDbrightnesdic':LEDbrightness}   
        self.data_Json = json.dumps(self.data)
        self.r=self.b=self.g =0
        self.data_Send_List = []
        self.prevData = []
        self.newData = []
        start_time = time.time()
        self.backupdata = []
        self.sock = socket.socket()
        self.host = "192.168.93.81"
        self.port = 80
        self.title("Light Controller")
        self.iconbitmap(PATH + '/1564159150695.ico')
        self.geometry(f"{LightController.WIDTH}x{LightController.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        def rgb_to_hex(r, g, b):
            if(r + g + b > 50):
                return '#%02x%02x%02x' % (r, g, b)

        #self.root = root
        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        # ============ frame_left ============

        # configure grid layout (1x11)
        #self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(2, weight=1)
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing
        self.frame_left.grid_rowconfigure(12, weight=1)  # empty row as spacing

        #self.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing
        #self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Light Controller",
                                              text_font=("Roboto Medium", -16))  # font name and size in px
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        self.label_mode_1 = customtkinter.CTkLabel(master=self.frame_left, text="Selected Color:")
        self.label_mode_1.grid(row=3, column=0, pady=0, padx=20, sticky="w")

        self.canvas_1 = Canvas(master=self.frame_left, height=30, width=30, highlightthickness=3, highlightbackground='grey')
        self.canvas_1.grid(row=4, column=0, pady=10)
        #self.canvas_1.create_rectangle(0, 0, 20, 20, fill='red')

        combobox_var1 = customtkinter.StringVar(value="Solid")  # set initial value
        combobox_var2 = customtkinter.StringVar(value="Linear Blend")  # set initial value
        combobox_var3 = customtkinter.StringVar(value="Static")  # set initial value
        
        self.label_mode_2 = customtkinter.CTkLabel(master=self.frame_left, text="Light Mode:")
        self.label_mode_2.grid(row=6, column=0, pady=0, padx=20, sticky="w")

        self.combobox_1 = customtkinter.CTkComboBox(master=self.frame_left,
                                                    values=["Solid", "Rainbow", "Rainbow Stripe", "Party", "Cloud", "Red, White & Blue", "Black & White Stripe"],
                                                    variable=combobox_var1)
        self.combobox_1.grid(row=7, column=0, columnspan=1, pady=10, padx=20, sticky="we")

        self.label_mode_3 = customtkinter.CTkLabel(master=self.frame_left, text="Blending Pattern:")
        self.label_mode_3.grid(row=8, column=0, pady=0, padx=20, sticky="w")

        self.combobox_2 = customtkinter.CTkComboBox(master=self.frame_left,
                                                    values=["Linear Blend", "No Blending"],
                                                    variable=combobox_var2)
        self.combobox_2.grid(row=9, column=0, columnspan=1, pady=10, padx=20, sticky="we")

        self.label_mode_4 = customtkinter.CTkLabel(master=self.frame_left, text="Light Motion:")
        self.label_mode_4.grid(row=10, column=0, pady=0, padx=20, sticky="w")

        self.combobox_3 = customtkinter.CTkComboBox(master=self.frame_left,
                                                    values=["Static", "Moving"],
                                                    variable=combobox_var3)
        self.combobox_3.grid(row=11, column=0, columnspan=1, pady=10, padx=20, sticky="we")

        def switch_event_1():
            print("switch toggled, current value:", self.switch_1.get())
            if(self.switch_1.get() == 0):
                self.button_1.configure(state=tkinter.DISABLED)
                self.frame_info.configure(border_color='black')
                self.canvas_1.configure(bg='black')
            else:
                self.button_1.configure(state=tkinter.NORMAL)

        def switch_event_2():
            print("switch toggled, current value:", self.switch_2.get())

        self.switch_1 = customtkinter.CTkSwitch(master=self.frame_left,
                                                text="Power",
                                                command=switch_event_1,)
        self.switch_1.grid(row=13, column=0, columnspan=1, pady=10, padx=20, sticky="we")

        self.switch_2 = customtkinter.CTkSwitch(master=self.frame_left,
                                                text="Wi-Fi",
                                                command=switch_event_2)
        self.switch_2.grid(row=14, column=0, columnspan=1, pady=10, padx=20, sticky="we")

        self.label_mode_4 = customtkinter.CTkLabel(master=self.frame_left, text="Appearance Mode:")
        self.label_mode_4.grid(row=15, column=0, pady=0, padx=20, sticky="w")

        self.optionmenu_1 = customtkinter.CTkOptionMenu(master=self.frame_left,
                                                        values=["Light", "Dark"],
                                                        command=self.change_appearance_mode)
        self.optionmenu_1.grid(row=16, column=0, pady=10, padx=20, sticky="w")

        # ============ frame_right ============

        # configure grid layout (3x7)
        #self.frame_right.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_right.rowconfigure(7, weight=10)
        self.frame_right.columnconfigure((0, 1), weight=5)
        self.frame_right.columnconfigure(2, weight=0)

        #.......
        self.frame_info = customtkinter.CTkFrame(master=self.frame_right, fg_color='black', border_width=20, border_color='black')
        self.frame_info.grid(row=0, column=0, columnspan=4, rowspan=8, pady=20, padx=20, sticky="nsew")

        # ============ frame_info ============

        # configure grid layout (1x1)
        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.columnconfigure(0, weight=1)

        img_1 = ImageTk.PhotoImage(Image.open(PATH + '\INDI-EV-Logo-Black_color select_final_cropped.jpg').resize((700, 700)))
        #img_2 = ImageTk.PhotoImage(Image.open(PATH + '\BlackBackground.jpg').resize((600, 600)))
    

        self.canvas = Canvas(self.frame_info, width=600, height=600, bd=0, bg='black')
        #self.canvas.pack(expand=True, fill='both')
        #self.canvas.create_image(0, 0, anchor=NW, image=img_2)
        self.canvas.grid(row=0, column=0, pady=20, padx=20)

        def button_event():
            print("button pressed")
            self.sendMessage()
            self.canvas_1.configure(bg=rgb_to_hex(self.r, self.g, self.b))
            self.frame_info.configure(border_color=rgb_to_hex(self.r, self.g, self.b))

        self.button_1 = customtkinter.CTkButton(master= self.canvas, image=img_1, text="",
                                                bg_color='black', fg_color='black', hover=False, command=button_event, highlightthickness = 0, borderwidth=0)                                        
        self.button_1.grid(row=0, column=0, padx=0, pady=0)

        #self.button_1.bind('<Button-1>', LightController.clickOnLogo)
        self.bind('<Button-1>', self.clickOnLogo)
        #self.button_1.pack()
            
        # ============ frame_right ============
        def slider_event(value):
            print(value)
    
        #self.label_2 = customtkinter.CTkLabel(master=self.frame_right,
        #                                      text="Brightness",
        #                                      text_font=("Roboto Medium", -16))  # font name and size in px
        #self.label_2.grid(row=9, column=0, columnspan=2, pady=10, padx=10)

        self.label_mode_5 = customtkinter.CTkLabel(master=self.frame_right, text="Brightness:")
        self.label_mode_5.grid(row=9, column=0, columnspan=2, pady=10, padx=10)

        self.slider_1 = customtkinter.CTkSlider(master=self.frame_right, from_=0, to=255, command=slider_event)
        self.slider_1.grid(row=10, column=0, columnspan=2, pady=10, padx=20, sticky="we")

        # set default values
        self.switch_1.select()
        self.switch_2.select()
        self.optionmenu_1.set("Dark")
        self.slider_1.set(0.5)

    #def changeButtonVal():
    #    global button_val
    #    button_val = not button_val

    def clickOnLogo(self, event): 
        dc = windll.user32.GetDC(0)
        rgb = windll.gdi32.GetPixel(dc,event.x_root,event.y_root)
        self.r = rgb & 0xff
        self.g = (rgb >> 8) & 0xff
        self.b = (rgb >> 16) & 0xff
        self.data['pickedcolordic']= "["+str(self.r)+","+str(self.g)+","+str(self.b)+"]"
        #self.sendMessage()
        #self.changeButtonVal()
        
    def sendMessage(self):
        self.data_Send_List.append(self.r)
        self.data_Send_List.append(self.g)
        self.data_Send_List.append(self.b)
        
        self.data_Send_List = str(self.data_Send_List)
        print(self.data_Send_List)
        self.data_Send_List = []     

    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()

    def is_socket_valid(self):
        try:
            self.sock.send(self.backupdata.encode())
        except:
            #print('Connection is Lost')
            self.switch_2.deselect()
            self.sock.close()            
              
    def makeConnectionAgain(self):        
        del(self.sock)
        self.sock = socket.socket()
        host = "192.168.93.81" #ESP32 IP in local network
        port = 80            #ESP32 Server Port    
        #self.sock.connect((host, port))
        print('I am connected to the Arduino!')
        self.switch_2.select()
    
if __name__ == "__main__":

    #setup initial values
    pickedColor  = str("[0,0,0]")
    patternMode = str('Solid')
    blendingMode = str("Linear Blend")
    motionMode = str("Static")
    LEDStatus = str ("Off")
    LEDbrightness = str(0)

    #setup intial data to send to the Arduino
    data = {'pickedcolordic':pickedColor,'patternModedic': patternMode,'blendingModedic': blendingMode, 'motionModedic':motionMode,'LEDStatusdic': LEDStatus, 'LEDbrightnesdic':LEDbrightness}   

    app = LightController()
    app.mainloop()