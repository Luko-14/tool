import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time


root = tk.Tk()

root.title("Welcome to the analysis")

canvas = tk.Canvas(root, height=500, width=1000)
canvas.pack()

mb = tk.Menubutton(canvas, text="Aantal bewoners", relief=tk.RAISED)
mb.place(relx=0.5, rely=0.5, anchor="c", relwidth=0.9, relheight=0.9)

mb.menu = tk.Menu(mb, tearoff=0)
mb["menu"] = mb.menu

ls = [1, 2, 3, 4, 5, 6]
value_ls = {}
all_none = tk.BooleanVar(root, name="all_none", value=True)


def ceck_all_items():
    if all_none.get():
        for i in value_ls:
            root.setvar(name=str(i), value=True)
    else:
        for i in value_ls:
            root.setvar(name=str(i), value=False)


mb.menu.add_checkbutton(label="All/None", variable=all_none, command=ceck_all_items)

for i in ls:
    value_ls[i] = []
    value_ls[i].append(tk.BooleanVar(root, True, name=str(i)))
    value_ls[i].append(mb.menu.add_checkbutton(label=i, variable=value_ls[i][0]))


# def lbl1():


# def lbl2():


# btn1 = tk.Button(canvas, text="True", command=lbl1)
# btn1.place(relx=0, rely=0)
# btn2 = tk.Button(canvas, text="False", command=lbl2)
# btn2.place(relx=0, rely=0.1)


root.mainloop()
