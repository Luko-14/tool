import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time


window = tk.Tk()

window.title("Welcome to the analysis")
window.geometry("500x300")


def warning():

    messagebox.showwarning("Nice", "Dit werkt bijna!")


def clicked():

    messagebox.showinfo("Nice", "Dit werkt!")


def error():

    messagebox.showerror("Nice", "Dit werkt niet!")


btn1 = tk.Button(window, text="Warning", command=warning)
btn2 = tk.Button(window, text="Goed", command=clicked)
btn3 = tk.Button(window, text="Error", command=error)

btn1.grid(column=0, row=0)
btn2.grid(column=1, row=0)
btn3.grid(column=2, row=0)


style = ttk.Style()

style.theme_use("default")

style.configure("black.Horizontal.TProgressbar", background="green")

MAX = 50
progress_var = tk.DoubleVar()

progressbar = ttk.Progressbar(
    window,
    variable=progress_var,
    maximum=MAX,
    style="black.Horizontal.TProgressbar",
)


progressbar.grid(column=0, row=1)


def loop_var():

    x = 0
    while x <= MAX:
        progress_var.set(x)
        x += 1
        time.sleep(0.05)
        window.update_idletasks()
    window.after(100, loop_var)


loop_var()
window.mainloop()
