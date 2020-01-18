import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk
from math import floor

class MainWindow():
    imgl = []
    mask = np.zeros((56,56))
    maskFinal = np.zeros((560,560))
    maskZoomed = []
    loadedImage = []
    displayedImage = []
    displayedImageCopy = []
    listboxCount = 0
    errMsg = ''
    def __init__(self, window):
        window.title('Labe-Kinter')
        self.master = window
        self.sideFrame = tk.Frame(window)
        self.sideFrame.grid(row = 0,column = 1, sticky = 'n')     
        
        self.menubar = tk.Menu(window)
        self.filemenu = tk.Menu(self.menubar)
        self.editmenu = tk.Menu(self.menubar)
        self.helpmenu = tk.Menu(self.menubar)
        self.settingsmenu = tk.Menu(self.menubar)
        self.menubar.add_cascade(label = 'File', menu = self.filemenu)
        self.filemenu.add_command(label = 'Open')
        self.filemenu.add_command(label = 'Save')
        self.menubar.add_cascade(label = 'Edit', menu = self.editmenu)
        self.editmenu.add_command(label = 'Mode')
        self.menubar.add_cascade(label = 'Settings', menu = self.settingsmenu)
        self.menubar.add_cascade(label = 'Help', menu = self.helpmenu)
        window.config(menu=self.menubar)
        
        self.canvas = tk.Canvas(window, width=560,height=560, background = 'white')
        self.canvas.grid(row = 0, column = 0)
        self.img = ImageTk.PhotoImage(image=Image.fromarray(np.random.randint(low = 0, high = 255,size = (560,560))))
        self.imgOnCanvas = self.canvas.create_image(0, 0, anchor = 'nw' ,image = self.img)
        self.canvas.bind('<B1-Motion>',self.__motion)
        self.listbox = tk.Listbox(self.sideFrame, height = 20)
        self.listbox.grid(row = 0, column = 0, sticky = 'nwe')
        self.button1 = tk.Button(self.sideFrame, text = 'Add region', fg ='red', command = self.__addRegion).grid(row = 1, column = 0, sticky = 'we')
        self.button2 = tk.Button(self.sideFrame, text = 'Remove region', fg ='red', command = self.__removeRegion).grid(row = 2, column = 0, sticky = 'we')
        self.button3 = tk.Button(self.sideFrame, text = 'Load image', fg ='blue', command = self.__openImage).grid(row = 3, column = 0, sticky = 'we')
        self.button4 = tk.Button(self.sideFrame, text = 'Save image', fg ='blue', command = self.__saveImage).grid(row = 4, column = 0, sticky = 'we')
        self.check1 = tk.Checkbutton(self.sideFrame, text = 'Original image').grid(row = 5, column = 0, sticky = 'w')
        self.check2 = tk.Checkbutton(self.sideFrame, text = 'Monochrome').grid(row = 6, column = 0, sticky = 'w')
        self.check3 = tk.Checkbutton(self.sideFrame, text = 'Contour').grid(row = 7, column = 0, sticky = 'w')
        self.scroll1 = tk.Scrollbar(window, orient = 'horizontal').grid(columnspan = 2, sticky = 'we')

    def __addRegion(self):
        print('Adding Region')
        print('listbox count is', self.listboxCount)
        self.displayedImageCopy.append(self.displayedImage*1)
        self.listboxCount = self.listboxCount + 1
        self.listbox.insert(self.listboxCount, 'Region ' + str(self.listboxCount))
        self.maskZoomed.append(np.zeros((560, 560)))

    def __removeRegion(self):
        print('removing region')
        try:
            print(len(self.displayedImageCopy))
            self.displayedImage = self.displayedImageCopy[self.listboxCount-1]
            self.displayedImageCopy.pop()
            self.__displayImage(self.displayedImage)
            self.maskZoomed.pop()
            self.listbox.delete(self.listboxCount - 1)
            self.listboxCount = self.listboxCount - 1
        except Exception as ex:
            print(str(ex))

    def __openImage(self):
        filePath = filedialog.askopenfilename(initialdir = "/", title = 'Select a file')
        if filePath:
            self.__loadImage(filePath)
    
    def __saveImage(self):
        fileName = filedialog.asksaveasfilename(defaultextension='.npy')
        self.loadedImage = np.where(self.loadedImage > 0, 1, 0)
        if fileName:
            for i in range(self.listboxCount):
                print('adding the masks')
                self.maskFinal = self.maskFinal + (self.maskZoomed[i]*self.loadedImage)*(i+1)
        np.save('full_file', self.maskFinal)
        scaling = 10        
        a = self.mask.shape        
        for i in range(a[0]):
            for j in range(a[1]):
                slices = self.maskFinal[i*scaling:(i*scaling)+scaling,j*scaling:(j*scaling)+scaling]
                self.mask[i][j] = slices.max()
        np.save(fileName, self.mask)
            
    def __loadImage(self, filePath):
        try:
            array = np.load(filePath)
        except:
            array = np.zeros((56, 56))
        scaling = 10
        a = array.shape
        array_scaled = np.zeros((a[0]*scaling, a[1]*scaling))
        max_val = np.max(array)
        for i in range(a[0]):
            for j in range(a[1]):
               array_scaled[i*scaling:(i*scaling)+scaling, j*scaling:(j*scaling)+scaling] = (array[i][j] / max_val)
        self.displayedImage = ((array_scaled-1)*-1)*255
        self.loadedImage = array_scaled
        self.__displayImage(self.displayedImage)
    
    def __motion(self,event):
        print("Mouse position: (%s %s)" % (event.x, event.y)) 
        if self.listboxCount > 0:
            x = event.x
            y = event.y
            sx = floor(x/10)*10
            sy = floor(y/10)*10
            if self.listboxCount-1 > 0:
                hitCount = []
                for i in range(self.listboxCount-1):
                    if self.maskZoomed[i][sy][sx] != 1:
                        hitCount.append(0)
                    else:
                        hitCount.append(1)
                if max(hitCount) == 0:
                    self.maskZoomed[self.listboxCount-1][sy:(sy+10), sx:(sx+10)] = 1
                    self.displayedImage[sy:(sy+10), sx:(sx+10)] = 255
            else:
                self.maskZoomed[self.listboxCount-1][sy:(sy+10),sx:(sx+10)] = 1
                self.displayedImage[sy:(sy+10), sx:(sx+10)] = 255
            self.__displayImage(self.displayedImage)
        else:
            self.errMsg = messagebox.showerror("Error!", "No region added")
    
    def __displayImage(self, image):
        self.imgl = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.canvas.itemconfig(self.imgOnCanvas, image = self.imgl)
        
root = tk.Tk()
mw = MainWindow(root)
maskFinal = mw.maskFinal                
root.mainloop()