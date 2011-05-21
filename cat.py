#!/usr/bin/python

# CA Toy
# by anders pearson <anders@columbia.edu>
# CCNMTL

# provides a basic framework for playing with
# simple CA models. gives you a grid and a textbox
# that you can enter code in. each time you step,
# the code is executed for each Cell, then the cells
# are redrawn on the grid.

from random import Random
from Tkinter import *
from Numeric import *
import numpy
import numpy.random
from tkSimpleDialog import Dialog
import Image
import ImageTk

r = Random()

cache = {}

# build a lookup table of colors
color_cache = {}
for val in range (256):
    color_cache[val] = "#%02x%02x%02x" % (val,val,val)

def array2image(a):
    return Image.fromstring("L", (a.shape[1], a.shape[0]), a.tostring())

class Cat:
    def __init__(self,parent):
        """ constructor for the CA Toy """
        self.parent = parent

        self.display_width = 400
        self.display_height = 400
        self.rows = 100
        self.cols = 100

        self.y_step_size = float(self.display_height/self.rows)
        self.x_step_size = float(self.display_width/self.cols)

        menubar = Menu(self.parent)
        filemenu = Menu(menubar,tearoff=0)

        filemenu.add_command(label="Load rule")
        filemenu.add_command(label="Save rule")
        filemenu.add_command(label="Export to federate...")
        
        menubar.add_cascade(label="File",menu=filemenu)

        editmenu = Menu(menubar,tearoff=0)
        editmenu.add_command(label="Grid size",command=self.edit_grid_size)
        
        menubar.add_cascade(label="Settings",menu=editmenu)
        menubar.add_command(label="Exit",command=self.parent.quit)
        self.parent.config(menu=menubar)

        self.handle_binary = 1
        self.f1 = Frame(self.parent)
        self.f1.pack()
        self.top_frame = Frame(self.f1)
        self.top_frame.pack(side=TOP)

        self.rule_frame = Frame(self.f1)
        self.rule_frame.pack(side=TOP)

        self.command_frame = Frame(self.f1)
        self.command_frame.pack()

        self.grid_controls = Frame(self.top_frame)
        self.grid_controls.pack(side=LEFT,anchor=N)

        self.canvas_frame = Frame(self.top_frame)
        self.canvas_frame.pack(side=LEFT)
        self.canvas = Canvas(self.canvas_frame,
                             width = self.display_width,
                             height = self.display_height)


        self.grid = numpy.random.rand(self.rows + 2, self.cols + 2) * 255
        self.grid = self.grid.astype('i')

        self.initial_draw()
        self.canvas.pack()
        self.previous_code = ""

        self.canvas.bind("<Button-1>",self.canvas_click)


        self.clear = Button(self.grid_controls,text="clear",command=self.clear_grid)
        self.clear.pack(side=TOP,fill=X,anchor=N)
        self.random = Button(self.grid_controls,text="random",command=self.randomize_grid)
        self.random.pack(side=TOP,fill=X,anchor=N)
        self.bool = Button(self.grid_controls,text="boolean",command = self.booleanize)
        self.bool.pack(side=TOP,fill=X,anchor=N)

        self.rule_buttons = Frame(self.rule_frame)
        self.rule_buttons.pack(side=LEFT,anchor=N)

        self.l1 = Label(self.rule_buttons,text="rule:")
        self.l1.pack(side=TOP)

        self.start_button = Button(self.rule_buttons,text="start",command=self.start)
        self.start_button.pack(side=TOP,fill=X)
        self.stop_button = Button(self.rule_buttons,text="stop",command=self.stop)
        self.stop_button.pack(side=TOP,fill=X)
        self.step_button = Button(self.rule_buttons,text="step",command=self.step)
        self.step_button.pack(side=TOP,fill=X)

        self.rule_input = Frame(self.rule_frame)
        self.rule_input.pack(side=LEFT)
        
        self.scrollbar = Scrollbar(self.rule_input)
        self.scrollbar.pack(side=RIGHT,fill=Y)
        self.code_input = Text(self.rule_input,height=10,width=55,yscrollcommand=self.scrollbar.set)
        self.code_input.pack()
        self.scrollbar.config(command=self.code_input.yview)
        

        self.command_buttons = Frame(self.command_frame)
        self.command_buttons.pack(side=LEFT,anchor=N)
        
        self.l2 = Label(self.command_buttons,text="command:")
        self.l2.pack(side=TOP)
        self.exec_button = Button(self.command_buttons,text="exec",command=self.exec_command)
        self.exec_button.pack(side=TOP)

        self.command_input_frame = Frame(self.command_frame)
        self.command_input_frame.pack(side=LEFT)
        
        self.command_scrollbar = Scrollbar(self.command_input_frame)
        self.command_scrollbar.pack(side=RIGHT,fill=Y)
        self.command_input = Text(self.command_input_frame,height=5,width=55,yscrollcommand=self.command_scrollbar.set)
        self.command_input.pack()
        self.command_scrollbar.config(command=self.command_input.yview)
        
        self.tickDelay = 10
        self.ticking = 0

    def initial_draw(self):
        self.image = self.grid[1:-1,1:-1]
        self.im = array2image(self.image.astype('b'))
        self.im2 = self.im.resize((self.display_width,self.display_height))
        self.img = ImageTk.PhotoImage(self.im2)
        self.canvas_image = self.canvas.create_image(0, 0, anchor=NW, image=self.img)


    def display(self):
        """ updates the canvas to show to the grid """
        self.image = self.grid[1:-1,1:-1]
        self.im = array2image(self.image.astype('b'))
        self.im2 = self.im.resize((self.display_width,self.display_height))
        self.img = ImageTk.PhotoImage(self.im2)
        self.canvas.itemconfigure(self.canvas_image,image=self.img)

    def update_edges(self):
        self.grid[0,] = self.grid[-2,]
        self.grid[-1,] = self.grid[1,]
        self.grid[:,0] = self.grid[:,-2]
        self.grid[:,-1] = self.grid[:,1]
        # corners
        self.grid[0,0] = self.grid[-2,-2]
        self.grid[0,-1] = self.grid[-2,1]
        self.grid[-1,0] = self.grid[1,-2]
        self.grid[-1,-1] = self.grid[1,1]
            
    def canvas_click(self,event):
        """ event handler for the user clicking on the canvas """
        # get the right grid coordinates from the
        # location of the click
        x = int(self.canvas.canvasx(event.y)/self.y_step_size)
        y = int(self.canvas.canvasy(event.x)/self.x_step_size)
        self.grid[x + 1,y + 1] = ~self.grid[x + 1, y + 1]
        self.display()
        #cell = self.cells[int((y + 1) * (steps + 2) + (x + 1))]
        # toggle the value of the cell

    def step(self):
        """ performs a single step of the simulation """

        self.update_edges()
        # peel out the individual bits

        b1 = where(self.grid & 1,  1,0)
        b2 = where(self.grid & 2,  1,0)
        b3 = where(self.grid & 4,  1,0)
        b4 = where(self.grid & 8,  1,0)
        b5 = where(self.grid & 16, 1,0)
        b6 = where(self.grid & 32, 1,0)
        b7 = where(self.grid & 64, 1,0)
        b8 = where(self.grid & 128,1,0)

        b = array([b1,b2,b3,b4,b5,b6,b7,b8])

        # prepare for computation by collecting the values
        # of the neighbors of each cell

        off = zeros((8,self.rows,self.cols))
        on =  ones((8,self.rows,self.cols))

        c = b[:,1:-1,1:-1]

        nw = b[:,0:-2,0:-2]
        n  = b[:,0:-2,1:-1]
        ne = b[:,0:-2,2:]

        w  = b[:,1:-1,0:-2]
        e  = b[:,1:-1,2:]

        sw = b[:,2:,0:-2]
        s  = b[:,2:,1:-1]
        se = b[:,2:,2:]

        m_cnt = nw + n + ne + w + e + sw + s +se
        m_total = m_cnt + c

        vn_cnt = n + e + s + w
        vn_total = vn_cnt + c

        # get the code to run out of the text box

        code = self.code_input.get(1.0,END)
        try:
            if code != self.previous_code:
                self.compiled_code = compile(code, '<string>', 'exec')
                self.previous_code = code
            exec self.compiled_code
        except:
            print "had problems"

        # stick the bits back together
        ints = ((c[7] * 128) + (c[6] * 64)
                                + (c[5] * 32) + (c[4] * 16)
                                + (c[3] * 8) + (c[2] * 4)
                                + (c[1] * 2) + c[0])
        
        self.grid[1:-1,1:-1] = ints.astype('b')
        
        # let each cell compute itself and
        # then update its display
        self.display()

    def exec_command(self):
        """ performs a single step using the code in the command window """

        self.update_edges()
        # peel out the individual bits

        b1 = where(self.grid & 1,  1,0)
        b2 = where(self.grid & 2,  1,0)
        b3 = where(self.grid & 4,  1,0)
        b4 = where(self.grid & 8,  1,0)
        b5 = where(self.grid & 16, 1,0)
        b6 = where(self.grid & 32, 1,0)
        b7 = where(self.grid & 64, 1,0)
        b8 = where(self.grid & 128,1,0)

        b = array([b1,b2,b3,b4,b5,b6,b7,b8])

        # prepare for computation by collecting the values
        # of the neighbors of each cell

        off = zeros((8,self.rows,self.cols))
        on =  ones((8,self.rows,self.cols))

        c = b[:,1:-1,1:-1]

        nw = b[:,0:-2,0:-2]
        n  = b[:,0:-2,1:-1]
        ne = b[:,0:-2,2:]

        w  = b[:,1:-1,0:-2]
        e  = b[:,1:-1,2:]

        sw = b[:,2:,0:-2]
        s  = b[:,2:,1:-1]
        se = b[:,2:,2:]

        m_cnt = nw + n + ne + w + e + sw + s +se
        m_total = m_cnt + c

        vn_cnt = n + e + s + w
        vn_total = vn_cnt + c

        # get the code to run out of the text box

        code = self.command_input.get(1.0,END)
        try:
            exec code
        except:
            print "had problems"

        # stick the bits back together
        ints = ((c[7] * 128) + (c[6] * 64)
                                + (c[5] * 32) + (c[4] * 16)
                                + (c[3] * 8) + (c[2] * 4)
                                + (c[1] * 2) + c[0])
        self.grid[1:-1,1:-1] = ints.astype('b')
        
        # let each cell compute itself and
        # then update its display
        self.display()

    def random_bit(self):
        r = numpy.random.rand(self.rows,self.cols) * 2
        r = r.astype('i')
        return r

    def boolean_mode(self):
        pass

    def start(self):
        """ makes it step repeatedly until the user hits stop"""
        self.stop()
        self.ticking = 1
        self.step()
        self.tickId = self.parent.after(self.tickDelay, self.start)

    def stop(self):
        """makes it stop stepping"""
        if self.ticking:
            self.parent.after_cancel(self.tickId)
            self.ticking = 0

    def clear_grid(self):
        """ set all cells in the grid to off """
        self.grid = reshape(zeros((self.rows + 2)*(self.cols+2)),(self.rows + 2,self.cols + 2))
        self.display()


    def randomize_grid(self):
        """ set each cell on the grid to a random value """
        self.grid = numpy.random.rand(self.rows + 2, self.cols + 2) * 255
        self.grid = self.grid.astype('i')
        self.display()

    def booleanize(self):
        self.grid = where(self.grid > 127, 255, 0)
        self.display()

    def edit_grid_size(self):
        self.edit_window = Grid_Edit_Window(self.parent)
        
        self.rows = self.edit_window.get_rows()
        self.cols = self.edit_window.get_cols()

        self.display_width = self.edit_window.get_width()
        self.display_height = self.edit_window.get_height()

        self.x_step_size = float(self.display_width/float(self.cols))
        self.y_step_size = float(self.display_height/float(self.rows))

        print self.x_step_size,self.y_step_size
        
        self.grid = resize(self.grid,(self.rows,self.cols))
        self.display()

class Grid_Edit_Window(Dialog):
    def body(self,master):
        self.title("Grid Size")

        Label(master, text="rows of cells:").grid(row=0,sticky=W)
        Label(master, text="cols of cells:").grid(row=1,sticky=W)
        Label(master, text="display width (pixels):").grid(row=2,sticky=W)
        Label(master, text="display height (pixels):").grid(row=3,sticky=W)

        self.rows = Entry(master,width=4)
        self.cols = Entry(master,width=4)
        self.width= Entry(master,width=4)
        self.height= Entry(master,width=4)

        self.rows.grid(row=0,column=1,sticky=W)
        self.cols.grid(row=1,column=1,sticky=W)
        self.width.grid(row=2,column=1,sticky=W)
        self.height.grid(row=3,column=1,sticky=W)

        self.rows_var = IntVar()
        self.rows_var.set(cat.rows)
        self.cols_var = IntVar()
        self.cols_var.set(cat.cols)
        self.width_var = IntVar()
        self.width_var.set(cat.display_width)
        self.height_var = IntVar()
        self.height_var.set(cat.display_height) 
        
        self.rows["textvariable"] = self.rows_var
        self.cols["textvariable"] = self.cols_var
        self.width["textvariable"] = self.width_var
        self.height["textvariable"] = self.height_var
        

    def apply(self):
        pass

    def get_rows(self):
        return self.rows_var.get()
    def get_cols(self):
        return self.cols_var.get()
    def get_width(self):
        return self.width_var.get()
    def get_height(self):
        return self.height_var.get()


# run it

root = Tk()
cat = Cat(root)
#cat.draw_grid()
root.mainloop()

