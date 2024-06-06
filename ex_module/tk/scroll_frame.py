import tkinter
from tkinter import *
from tkinter import ttk

def scrolllistbox2(event):
    mycanvas.yview_scroll(int(-1*(event.delta/120)), "units")

win = Tk()
#wrapper1 = LabelFrame(win)
#wrapper2 = LabelFrame(win)

mycanvas = Canvas(win)
mycanvas.pack(side=LEFT)

#yscrollbar = ttk.Scrollbar(wrapper1, orient="vertical", command=mycanvas.yview)
#yscrollbar.pack(side=RIGHT, fill="y")

#mycanvas.configure(yscrollcommand=yscrollbar.set)

mycanvas.bind('<Configure>', lambda e: mycanvas.configure(scrollregion = mycanvas.bbox('all')))

myframe = Frame(mycanvas)
mycanvas.create_window((0, 0), window=myframe, anchor="nw")

#win.pack(fill="both", expand=True, padx=10, pady=10)
#wrapper2.pack(fill="both", expand=True, padx=10, pady=10)

mycanvas.bind_all("<MouseWheel>", scrolllistbox2)


for i in range(50):
    Button(myframe, text=f"my button {i}").pack()

win.geometry("500x500")
win.resizable(False, False)
win.title("k")
win.mainloop()