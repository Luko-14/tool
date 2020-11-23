import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.stats import norm
from ttkthemes.themed_tk import ThemedTk


class AllCheckboxes:
    def __init__(self, df_results):
        self.dict = {}

        index_name = df_results.index.name
        ls = df_results.index.tolist()
        ls.sort()

        self.dict[index_name] = Checkboxes(ls)

        for column in df_results.columns:
            if df_results[column].dtype == float:
                df_results[column] = round(df_results[column], 3)

            ls = df_results[column].unique()
            ls.sort()

            self.dict[column] = Checkboxes(ls)


class Checkboxes:
    def __init__(self, ls):

        self.ls = ls
        self.checkboxes = {}

        self.checkboxes["All/None"] = []
        self.checkboxes["All/None"].append(
            tk.BooleanVar(self.root, True, name=str("All/None"))
        )
        self.checkboxes["All/None"].append(None)

        for item in self.ls:
            self.checkboxes[item] = []
            self.checkboxes[item].append(tk.BooleanVar(self.root, True, name=str(item)))
            self.checkboxes[item].append(None)

    def new_boxes(self):
        self.checkboxes["All/None"][1] = ttk.Checkbutton(
            self.frame,
            text="All/None",
            variable=self.checkboxes["All/None"][0],
            command=self.check_all_items,
        )

        for item in self.ls:
            self.checkboxes[item][1] = ttk.Checkbutton(
                self.frame, text=item, variable=self.checkboxes[item][0], width=15
            )

    def check_all_items(self):
        allnone = self.checkboxes["All/None"][0]
        if allnone.get():
            for i in self.checkboxes:
                self.root.setvar(name=str(i), value=True)
        else:
            for i in self.checkboxes:
                self.root.setvar(name=str(i), value=False)


def menu_bar(root):
    menubar = tk.Menu(root)

    mb_file = tk.Menu(menubar, tearoff=False)
    mb_file.add_command(label="New Analysis", command=lambda: print("Hello"))
    mb_file.add_command(label="Change results file", command=lambda: print("Goodbye"))
    mb_file.add_separator()
    mb_file.add_command(label="Exit", command=root.destroy)

    menubar.add_cascade(label="File", menu=mb_file)

    root.config(menu=menubar)


def draw_buttons(df_results, frame_buttons):

    Buttons = []

    Buttons.append(
        ttk.Button(
            frame_buttons, text=df_results.index.name.replace("_", " "), width=15
        )
    )

    for column in df_results.columns:
        Buttons.append(
            ttk.Button(frame_buttons, text=column.replace("_", " "), width=15)
        )

    i = 0
    j = 0
    while True:
        if (i % 2) == 0:
            Buttons[i].grid(row=0, column=j, padx=3, pady=3)
        else:
            Buttons[i].grid(row=1, column=j, padx=3, pady=3)
            j += 1

        if i == (len(Buttons) - 1):
            break
        else:
            i += 1

    Buttons.append(ttk.Button(frame_buttons, text="Apply filters"))
    Buttons[i + 1].grid(row=0, column=(j + 1), padx=3, pady=3, rowspan=2)


def draw_plots(frame_plots, mean, std):
    plots = Figure(dpi=100)
    std2_color = "orange"
    std1_color = "red"

    x_axis = np.arange(0, 2 * mean, 0.01)
    y_axis = norm.pdf(x_axis, mean, std)

    ax1 = plots.add_subplot()
    ax1.plot(x_axis, y_axis)

    ax1.set_title("Bellcurve gas reduction")
    ax1.set_xlabel("Gas reduction (%)")
    ax1.set_ylabel("Change")

    pos_x = []
    i = 0
    j = int(mean // std + 1)
    for i in range(2 * j):
        x = mean - std * (j - i)
        pos_x.append(x)

    plt.setp(ax1, xticks=pos_x)

    x_fil1 = np.arange((mean - 2 * std), (mean - std), 0.01)
    y_fil1 = norm.pdf(x_fil1, mean, std)

    x_fil2 = np.arange((mean - std), (mean + std), 0.01)
    y_fil2 = norm.pdf(x_fil2, mean, std)

    x_fil3 = np.arange((mean + std), (mean + 2 * std), 0.01)
    y_fil3 = norm.pdf(x_fil3, mean, std)

    ax1.fill_between(x_fil1, y_fil1, alpha=0.25, color=std2_color)
    ax1.fill_between(x_fil2, y_fil2, alpha=0.25, color=std1_color, label="68.2")
    ax1.fill_between(x_fil3, y_fil3, alpha=0.25, color=std2_color, label="95.4%")

    ax1.set_xlim(0, 2 * mean)
    ax1.set_ylim(0)
    ax1.legend()

    plots.tight_layout(pad=2.5)

    canvas_plots = FigureCanvasTkAgg(plots, master=frame_plots)
    canvas_plots.draw()
    canvas_plots.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)


def draw_scrollbar(frame_scroll, df_results, name, all_checkboxes):

    name = name.replace(" ", "_")
    canvas_scroll = tk.Canvas(frame_scroll)

    scrollbar = ttk.Scrollbar(
        frame_scroll, orient=tk.VERTICAL, command=canvas_scroll.yview
    )

    frame_scroll_items = ttk.Frame(canvas_scroll)

    canvas_scroll.bind(
        "<Configure>",
        lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")),
    )

    canvas_scroll.bind_all(
        "<MouseWheel>",
        lambda e: canvas_scroll.yview_scroll(int(-1 * (e.delta / 120)), "units"),
    )

    canvas_scroll.create_window((0, 0), window=frame_scroll_items)
    canvas_scroll.configure(yscrollcommand=scrollbar.set)

    Checkboxes.frame = frame_scroll_items

    all_checkboxes.dict[name].new_boxes()
    dict_checkbox = all_checkboxes.dict[name].checkboxes
    row = 0

    for i in dict_checkbox:
        dict_checkbox[i][1].pack(anchor="n", pady=6)
        row += 1

    canvas_scroll.pack(side="left", fill="both", expand=True)
    scrollbar.place(relheight=1, relwidth=0.1, relx=0.9)


def results_gui(df_results):

    df_results["Residents"] = df_results["Residents"].astype(int)
    df_results["Solar_Panels"] = df_results["Solar_Panels"].astype(int)

    for column in df_results.columns:
        if df_results[column].dtype == float:
            df_results[column] = round(df_results[column], 3)

    root = ThemedTk()
    root.get_themes()
    root.set_theme("breeze")
    root.geometry("1000x500")

    p = 12
    scrol_width = 200
    button_height = 150

    root.title("Welcome to the analysis")
    menu_bar(root)

    Checkboxes.root = root

    frame_buttons = ttk.Frame(root, padding=p)
    frame_scroll = ttk.Frame(root, padding=p)
    frame_plots = ttk.Frame(root, padding=p)

    frame_buttons.place(
        x=scrol_width,
        relwidth=1,
        width=scrol_width,
        height=button_height,
    )

    frame_scroll.place(width=scrol_width, relheight=1)

    frame_plots.place(
        x=scrol_width,
        y=button_height,
        relwidth=1,
        relheight=1,
        width=-scrol_width,
        height=-button_height,
    )

    all_checkboxes = AllCheckboxes(df_results)
    draw_scrollbar(frame_scroll, df_results, "Gas Reduction", all_checkboxes)

    # def update(event):
    #     root.update()
    #     width = root.winfo_width()
    #     height = root.winfo_height()

    draw_buttons(df_results, frame_buttons)

    draw_plots(frame_plots, 14.7, 3.7)
    # root.bind("<Configure>", update)
    root.mainloop()


def main():
    df = pd.read_csv("./data/result 19nov.csv", index_col="Serial_number")
    results_gui(df)


if __name__ == "__main__":
    main()
