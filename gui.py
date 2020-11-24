import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from scipy.stats import norm
from ttkthemes.themed_tk import ThemedTk
from math import isnan


class AllCheckboxes:
    # start function
    def __init__(self, df_results):
        # create dictionary with all boxes
        self.dict = {}

        # get name of index
        index_name = df_results.index.name
        # get all serial numbers
        ls = df_results.index.tolist()
        ls.sort()

        # add checkbox of each serial numbers to dict
        self.dict[index_name] = Checkboxes(ls, index_name)

        # add each column to dict
        for column in df_results.columns:
            # creates unique list of column and sorts it
            ls = df_results[column].unique()
            ls.sort()
            # add checkbox of each unique items to dict
            self.dict[column] = Checkboxes(ls, column)


class Checkboxes:
    # startup funciton
    def __init__(self, ls, name):

        # create list of unique items in column
        self.ls = ls
        # creates dictionary of checkboxes
        self.checkboxes = {}

        # add all/non checkbox and add to dict
        self.checkboxes["All/None"] = []
        # create allnon variable
        self.checkboxes["All/None"].append(
            tk.BooleanVar(root, True, name=(name + "_All/None"))
        )
        # create checkbox
        self.checkboxes["All/None"].append(
            ttk.Checkbutton(
                self.frame,
                text="All/None",
                variable=self.checkboxes["All/None"][0],
                command=self.check_all_items,
            )
        )

        # create checkbox for each unique item
        for item in self.ls:
            self.checkboxes[item] = []
            # create variable
            self.checkboxes[item].append(tk.BooleanVar(root, True, name=str(item)))
            # create checkbox
            self.checkboxes[item].append(
                ttk.Checkbutton(
                    self.frame, text=item, variable=self.checkboxes[item][0], width=15
                )
            )

    # function of all/none button
    def check_all_items(self):
        # locate the varaible
        allnone = self.checkboxes["All/None"][0]
        # check state of varaible
        if allnone.get():
            # changes state of all checkboxes to true
            for i in self.checkboxes:
                root.setvar(name=str(i), value=True)
        else:
            # changes state of all checkboxes to false
            for i in self.checkboxes:
                root.setvar(name=str(i), value=False)


class Buttons:
    def __init__(self, df_results, frame_buttons):
        # creat list of filter buttons
        self.list = []

        # add serial number button
        name = df_results.index.name.replace("_", " ")
        self.list.append(Button(name, frame_buttons))

        # for each column add button and add to list
        for column in df_results.columns:
            self.list.append(Button(column, frame_buttons))


class Button:
    def __init__(self, name, frame_buttons):
        # create name of each button
        self.name = name
        # create button
        self.button = ttk.Button(
            frame_buttons,
            text=self.name.replace("_", " "),
            width=15,
            command=(lambda: button_click(self)),
        )


def filter_data():

    # create a dataframe for filtering
    df_filt = df_results.copy()

    # get dict of all checkboxes
    all_dict = all_checkboxes.dict

    # go through each filter (columns)
    for key in all_dict:
        # get object of each filter {column}
        item = all_dict[key]
        # go through each checkbox
        for i in item.ls:
            # check if checkbox is Flase
            if not item.checkboxes[i][0].get():
                # check if column is the index column
                if key == df_filt.index.name:
                    # drop the index
                    df_filt.drop(index=i, inplace=True)
                else:
                    # filter results
                    df_filt = df_filt[df_filt[key] != i]

    # calculate mean
    mean = df_filt["Gas_Reduction"].mean()

    # calculate standard deviation
    std = df_filt["Gas_Reduction"].std()

    # plot the bellcurve
    if isnan(mean) or isnan(std):
        messagebox.showerror(
            title="Data error",
            message="With the current filters the dataframe has no results. \n Try a differnt filter!",
        )
        return 0

    draw_plots(mean, std)


def menu_bar():
    # add menu bar on top
    menubar = tk.Menu()

    # add file menu
    mb_file = tk.Menu(menubar, tearoff=False)
    # add new analysis button
    mb_file.add_command(label="New Analysis", command=lambda: print("Hello"))
    # add change results file button
    mb_file.add_command(label="Change results file", command=lambda: print("Goodbye"))
    # adding separator
    mb_file.add_separator()
    # add exit button
    mb_file.add_command(label="Exit", command=root.destroy)

    # add file to menu bar
    menubar.add_cascade(label="File", menu=mb_file)

    # sets menubar
    root.config(menu=menubar)


def draw_plots(mean, std):
    # deletes old content
    for checkbox in frame_plots.winfo_children():
        checkbox.destroy()

    # creates figure
    plots = Figure(figsize=(8, 4))

    # colors
    std2_color = "orange"
    std1_color = "red"

    # creates x-axis values
    x_axis = np.arange(0, 2 * mean, 0.01)
    # creates y-axis values
    y_axis = norm.pdf(x_axis, mean, std)

    # add plot
    ax1 = plots.add_subplot()
    # plot x and y values
    ax1.plot(x_axis, y_axis)

    # set title and lables
    ax1.set_title("Bellcurve gas reduction")
    ax1.set_xlabel("Gas Reduction(%)")
    ax1.set_ylabel("Chance")

    # creates x-axis ticks
    pos_x = []
    i = 0
    j = int(mean // std + 1)
    for i in range(2 * j):
        x = mean - std * (j - i)
        pos_x.append(x)

    # set x-axis ticks
    plt.setp(ax1, xticks=pos_x)

    # creates region between mean - 2std and mean - std
    x_fil1 = np.arange((mean - 2 * std), (mean - std), 0.01)
    y_fil1 = norm.pdf(x_fil1, mean, std)

    # creates region between mean - std and mean + std
    x_fil2 = np.arange((mean - std), (mean + std), 0.01)
    y_fil2 = norm.pdf(x_fil2, mean, std)

    # creates region between mean + std and mean =2 std
    x_fil3 = np.arange((mean + std), (mean + 2 * std), 0.01)
    y_fil3 = norm.pdf(x_fil3, mean, std)

    # fill regions
    ax1.fill_between(x_fil1, y_fil1, alpha=0.25, color=std2_color)
    ax1.fill_between(x_fil2, y_fil2, alpha=0.25, color=std1_color, label="68.2")
    ax1.fill_between(x_fil3, y_fil3, alpha=0.25, color=std2_color, label="95.4%")

    # set x and y axis limits
    ax1.set_xlim(0, 2 * mean)
    ax1.set_ylim(0)
    ax1.legend()

    # make plot tight
    # plots.tight_layout(pad=2.5)

    # create and draw canvas
    canvas_plots = FigureCanvasTkAgg(plots, master=frame_plots)
    canvas_plots.draw()
    canvas_plots.get_tk_widget().place(anchor="sw")

    # add toolbar
    toolbar = NavigationToolbar2Tk(canvas_plots, frame_plots)
    toolbar.update()
    canvas_plots.get_tk_widget().pack()


def draw_checkboxes(name, all_checkboxes):

    # removes all checkboxes
    for checkbox in frame_scroll_items.winfo_children():
        checkbox.grid_forget()

    # changes name to column name
    name = name.replace(" ", "_")

    # retrieves a list with all checkboxes for input column
    dict_checkbox = all_checkboxes.dict[name].checkboxes

    # places each checkbox in dict
    row = 0
    for i in dict_checkbox:
        dict_checkbox[i][1].grid(column=1, row=row)
        row += 1
    canvas_scroll.yview_moveto(0)


def button_click(button):
    global last_pressed
    # run draw checkboxes
    draw_checkboxes(button.name, all_checkboxes)

    button.button.state(["pressed", "!disabled"])

    # try to set "unpress" laspressed
    try:
        last_pressed.state(["!pressed", "!disabled"])
    except Exception:
        pass

    # set button to pressed
    last_pressed = button.button


def draw_buttons(df_results, frame_buttons):

    buttons = Buttons(df_results, frame_buttons)
    button_list = buttons.list
    # column number
    j = 0
    # add each button
    for i in range((len(button_list))):
        # checks if button is in row 0 or 1
        if (i % 2) == 0:
            # adds button to row 0
            button_list[i].button.grid(row=0, column=j, padx=3, pady=3)
        else:
            # adds button to row 1
            button_list[i].button.grid(row=1, column=j, padx=3, pady=3)
            j += 1

        i += 1

    # creates apply filters button
    apply_button = ttk.Button(frame_buttons, text="Apply filters", command=filter_data)
    # add apply filter button
    apply_button.grid(row=0, column=(j + 1), padx=3, pady=3, rowspan=2)

    return button_list[0]


def results_gui():

    # changes datatype to int
    df_results["Residents"] = df_results["Residents"].astype(int)
    df_results["Solar_Panels"] = df_results["Solar_Panels"].astype(int)

    # round floats to 3 decimals
    for column in df_results.columns:
        if df_results[column].dtype == float:
            df_results[column] = round(df_results[column], 3)

    # setup the gui
    global root
    root = ThemedTk()
    root.get_themes()
    root.set_theme("breeze")
    root.geometry("1000x500")
    root.title("Welcome to the analysis")

    # changeable parameters
    p = 12
    scrol_width = 200
    button_height = 150

    # add menubar
    menu_bar()

    # create frames
    frame_buttons = ttk.Frame(root, padding=p)
    frame_scroll = ttk.Frame(root, padding=p)
    global frame_plots
    frame_plots = ttk.Frame(root, padding=p)

    # place frames
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

    # create canvas scrollbar
    global canvas_scroll
    canvas_scroll = tk.Canvas(frame_scroll)

    # create scrollbar
    scrollbar = ttk.Scrollbar(
        frame_scroll, orient=tk.VERTICAL, command=canvas_scroll.yview
    )

    # create frame for checkboxes
    global frame_scroll_items
    frame_scroll_items = ttk.Frame(canvas_scroll, padding=10)

    # add scrolling features
    canvas_scroll.bind(
        "<Configure>",
        lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")),
    )

    canvas_scroll.bind_all(
        "<MouseWheel>",
        lambda e: canvas_scroll.yview_scroll(int(-1 * (e.delta / 120)), "units"),
    )

    canvas_scroll.configure(yscrollcommand=scrollbar.set)

    # add scrolling frame to canvas
    canvas_scroll.create_window((0, 0), window=frame_scroll_items, anchor="nw")

    canvas_scroll.place(relheight=1, relwidth=0.9)
    scrollbar.place(relheight=1, relwidth=0.1, relx=0.9)

    # create checkboxes
    Checkboxes.frame = frame_scroll_items

    global all_checkboxes
    all_checkboxes = AllCheckboxes(df_results)

    # create filter buttons
    first_button = draw_buttons(df_results, frame_buttons)

    # adding first checkboxes
    button_click(first_button)

    # draw plot
    filter_data()

    root.mainloop()


def main():
    global df_results
    df_results = pd.read_csv("./data/result 19nov.csv", index_col="Serial_number")
    results_gui()


if __name__ == "__main__":
    main()
