from tkinter import *
import os
import sys
import watcher
import test1
import pyDashtest
import time
from PIL import Image, ImageTk
import datetime
from datetime import timedelta
from typing import List
import threading


class MyGUI:
    def __init__(self):

        self.master = Tk()
        self.canvas = Canvas(self.master)
        self.canvas.pack()
        self.data=[]
        self.pickCalc = []
        watchfilesThread = threading.Thread(target=self.watch_files)
        watchfilesThread.start()
        self.readerr = watcher.reader()


        #-------------- Start Internet operation --------------------------

        self.updateArray()
        self.emailNum = 0
        self.clicked = StringVar() 
        options = [sublist[0] for sublist in self.pickCalc]
        

        # initial menu text 
        self.clicked.set(options[0]) 
        drop = OptionMenu( self.master , self.clicked , *options ) 
        drop.pack() 

        
        button = Button( self.master , text = "See Result", command= self.open_popup).pack() 

    def watch_files(self):
        python_home = os.getcwd()

        print(python_home)

        csv_files = [file for file in os.listdir(python_home) if file.endswith('.csv')]
        
        while True:
            print(python_home)
            csv = [file for file in os.listdir(python_home) if file.endswith('.csv')]
         
            new_csv_files = [file for file in csv if file not in csv_files]
            

            if new_csv_files:
                print('updating Array')
                csv_files=csv
                self.updateArray()
            # Wait for some time before checking again
            time.sleep(30)  # Check every 30 seconds



    def find_double_for_date(self,target_date,data):
        for entry in data:
            print(entry)
            if len(entry) == 2:
                print(entry[0])
                if entry[0] == target_date:
                    return entry[1]
        return None  
    

    def open_popup(self):
        top= Toplevel(self.master)
        top.geometry("750x250")
        top.title('Production Calculator')
        format_str = '%d/%m/%Y'
        
        number = self.find_double_for_date(datetime.datetime.strptime(self.clicked.get(), "%Y-%m-%d %H:%M:%S"),self.pickCalc)

        
        #this points at the coms dropped till columns
        pickLeft = self.pickCalc[0][0]
        for i in self.pickCalc:
            print(f'this is pick calc {i}')

        pickAdd = self.data[-1][-1][-1]
       
        dateAdd = datetime.datetime.strptime(pickAdd.split('_')[0], "%Y-%m-%d-%H-%M-%S")

        title = f"Production Calculation   Time Picked: {pickLeft}"
        six = f"16500: {number/16500:.2f} time: { ( + timedelta(hours=round(number/16500,2)))}"

        seven= f"17000: {number/17000:.2f} time: { (dateAdd + timedelta(hours=number/17000))}"
        eight= f"18000: {number/18000:.2f} time: { (dateAdd + timedelta(hours=number/18000))}"
        nine= f"19000: {number/19000:.2f} time: { (dateAdd + timedelta(hours=number/19000))}"
        ten= f"20000: {number/20000:.2f} time: { (dateAdd + timedelta(hours=number/20000))}"

        Label(top, text= title, font=('Mistral 18 bold')).place(x=150,y=0)
        Label(top, text= ten, font=('Mistral 18')).place(x=150,y=40)
        Label(top, text= nine, font=('Mistral 18')).place(x=150,y=80)
        Label(top, text= eight, font=('Mistral 18')).place(x=150,y=120)
        Label(top, text= seven, font=('Mistral 18')).place(x=150,y=160)
        Label(top, text= six, font=('Mistral 18')).place(x=150,y=200)
        Label(top, text= f'Picks: {str(number)}', font=('Mistral 18')).place(x=150,y=240)
        
            
    




    
    def redraw(self):
        script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        image_path = 'witron.png'
        pil_image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(pil_image)
        self.image_item = self.canvas.create_image(100, 100, anchor=NW, image=self.photo)

        for i in self.data:
            print(i)

            if len(i)>1:
                if 'Todays Calc' in i[0]:
                    self.addRect(i[0]+str(i[1]),"#0069aa")

                elif 'om36' in i[0][0]:
                    continue
                elif 'Coms Dropped till' in i[0]:
                    self.addRect(f'Com: {i[1]}',"#00aa69")  
                elif 'Coms Needed' in i[0]:
                    if len(i)>1:
                        self.addRect(i[0]+str(i[2]),"#f55951")



                elif len(i)<2:
                    self.addRect(i[0]+str(len(i)-1),"#00aa69")    
                else:
                    self.addRect(i[0]+str(len(i)-1),"#f55951")

            


        self.adjust_canvas_size()


 

    def updateArray(self):
        
        
        
        self.readerr.process()

    
           #----- This is my drop down menu 
        self.pickCalc = self.readerr.pickCalc
        #pass self.readerr.warnings
        senderThread = threading.Thread(target=self.send, args=(self.readerr.warnings,))

        senderThread.start()
            
        self.data=self.readerr.warnings
        self.clear_canvas()
        self.redraw()
       
        
            
    def send(self,array):
        print('ENETERING RANDOM')
        if len(array) > 3:    
            print(f'ENtering PLUS 3')
            formatted_string = f'---------------------------{str(array[-1][-1][-1]).split("_")[0]}-----------------------------'
            test1.teamSender(formatted_string)
            for i in array:
               
                print(i)
                if i == array[-1]:
                    continue

                if len(i)>1:
                    if 'Coms Dropped till' in i[0]:
                        test1.teamSender(str(i))
                    else:
                        test1.teamSender(i)

        
        



    def clear_canvas(self):
        self.canvas.delete("all")
        for label in self.master.winfo_children():
            if isinstance(label, Label):
                label.destroy()    

    def addRect(self, text,fill):
        bbox = self.canvas.bbox("all")
        last_rect_coords = self.canvas.bbox("all")



        if last_rect_coords == (100,100,350,175):
            print('last rect 1')
            print(last_rect_coords)
            rect = RoundedRect(self.canvas, 30, 110, 225, 210, radius=80,text=text ,fill=fill) 
            print(self.canvas.bbox("all"))
            

        else:
            x1, y1, x2, y2 = last_rect_coords
            
            
            rect = RoundedRect(self.canvas, 30, y2+10, 225, y2+110, radius=80,text=text ,fill=fill) 

            print("Coordinates of the last rectangle:", last_rect_coords)
            print(type(last_rect_coords))


        
        
        
    
    def adjust_canvas_size(self):
        bbox = self.canvas.bbox("all")
        self.canvas.config(width=bbox[2], height=bbox[3])

        # Update the image item to fit the new canvas size
        self.canvas.coords(self.image_item, 0, 0)


class RoundedRect:
    def __init__(self, canvas, x1, y1, x2, y2, radius=25, text="ERROR", **kwargs):
        self.canvas = canvas
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.radius = radius
        self.kwargs = kwargs
        self.draw()
        self.create_text_in_rectangle(text)

    def create_text_in_rectangle(self, text):
        x, y, width, height = self.x1, self.y1, self.x2 - self.x1, self.y2 - self.y1
        self.text_id = self.canvas.create_text(
            x + width / 2, y + height / 2,
            text=text,
            font=("Helvetica", 17, "bold"),
            fill="white"
        )


    def draw(self):
        points = [self.x1 + self.radius, self.y1,
                  self.x1 + self.radius, self.y1,
                  self.x2 - self.radius, self.y1,
                  self.x2 - self.radius, self.y1,
                  self.x2, self.y1,
                  self.x2, self.y1 + self.radius,
                  self.x2, self.y1 + self.radius,
                  self.x2, self.y2 - self.radius,
                  self.x2, self.y2 - self.radius,
                  self.x2, self.y2,
                  self.x2 - self.radius, self.y2,
                  self.x2 - self.radius, self.y2,
                  self.x1 + self.radius, self.y2,
                  self.x1 + self.radius, self.y2,
                  self.x1, self.y2,
                  self.x1, self.y2 - self.radius,
                  self.x1, self.y2 - self.radius,
                  self.x1, self.y1 + self.radius,
                  self.x1, self.y1 + self.radius,
                  self.x1, self.y1]

        self.canvas.create_polygon(points, **self.kwargs, smooth=True)



def main():
    files = pyDashtest.Files()
    files.master()
    gui = MyGUI()
    gui.master.mainloop()

    # Optionally, you can call other functions or classes from watcher.py here

if __name__ == "__main__":
    main()


