import pandas as pd
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np


class dropbutton:
    def __init__(self, name, items):
        self.name = name
        self.items = items

        self.mb = tk.Menubutton(dropbutton.canvas, text=self.name, relief=tk.RAISED)
        self.mb.menu = tk.Menu(self.mb, tearoff=0)
        self.mb["menu"] = self.mb.menu

        self.value_ls = {}
        self.all_none = tk.BooleanVar(
            dropbutton.root, name=(self.name + "_all_none"), value=True
        )

        self.mb.menu.add_checkbutton(
            label="All/None",
            variable=self.all_none,
            command=self.check_all_items,
        )

        self.mb.menu.insert_separator(1)

        for i in self.items:
            self.value_ls[i] = []
            self.value_ls[i].append(tk.BooleanVar(dropbutton.root, True, name=str(i)))
            self.value_ls[i].append(
                self.mb.menu.add_checkbutton(label=i, variable=self.value_ls[i][0])
            )

    def check_all_items(self):
        if self.all_none.get():
            for i in self.value_ls:
                dropbutton.root.setvar(name=str(i), value=True)
        else:
            for i in self.value_ls:
                dropbutton.root.setvar(name=str(i), value=False)

    def __repr__(self):
        return self.name


def gui(df_results):
    root = tk.Tk()

    root.title("Welcome to the analysis")

    canvas = tk.Canvas(root, height=500, width=1000)
    canvas.pack()

    frame_fig1 = tk.Frame(canvas)
    frame_fig1.place(relx=0.1, rely=0.25, relwidth=(0.8), relheight=(0.65))

    fig1 = Figure(dpi=100)
    t = np.arange(0, 3, 0.01)
    fig1.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

    canvas_fig1 = FigureCanvasTkAgg(fig1, master=frame_fig1)  # A tk.DrawingArea.
    canvas_fig1.draw()
    canvas_fig1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)

    dropbutton.root = root
    dropbutton.canvas = canvas

    dropbuttons = []

    df_results["Residents"] = df_results["Residents"].astype(int)
    df_results["Solar_Panels"] = df_results["Solar_Panels"].astype(int)

    ls = df_results.index.tolist()
    ls.sort()

    dropbuttons.append(dropbutton(df_results.index.name, ls))

    for column in df_results.columns:
        ls = df_results[column].unique()
        ls.sort()

        if df_results[column].dtype == float:
            for i in range(len(ls)):
                ls[i] = round(ls[i], 3)

        dropbuttons.append(dropbutton(column, ls))

    for i in range(len(dropbuttons)):
        dropbuttons[i].mb.place(
            relx=0.1 * i + 0.02 * (i + 1),
            rely=0.1,
            anchor="nw",
            relwidth=0.1,
            relheight=0.1,
        )

    root.mainloop()


def main():
    df = pd.read_csv("./data/result 19nov.csv", index_col="Serial_number")
    gui(df)


if __name__ == "__main__":
    main()
