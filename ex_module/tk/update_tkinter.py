import tkinter as tk
import random

def update():
    l.config(text=str(random.random()))
    root.after(int(1000*1/30), update)

root = tk.Tk()
l = tk.Label(text='0')
l.pack()
root.after(int(1000*1/30), update)
root.mainloop()