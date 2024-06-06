from tkinter import Tk, Canvas

tk = Tk()
tk.config(width=400, height=800)
tk.title('Grid')

canvas = Canvas(tk, width=400, height=800, bg='#FFFFFF')

canvas.pack(side="left")
canvas2 = Canvas(tk, width=200, height=800, bg='#000000')

canvas2.pack(side="right")

tk.mainloop()