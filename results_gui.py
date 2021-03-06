import tkinter as tk
from math import isnan
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from scipy.stats import norm
from ttkthemes.themed_tk import ThemedTk

import analysis


class AllCheckboxes:
    # start function
    def __init__(self, df_results):
        # create dictionary with all boxes
        self.dict = {}

        # setting  checkbox frame
        Checkboxes.frame = frame_scroll_items
        Checkboxes.root = root

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
        self.name = name
        # create list of unique items in column
        self.ls = ls
        # creates dictionary of checkboxes
        self.checkboxes = {}

        # add all/non checkbox and add to dict
        self.checkboxes["All/None"] = []
        # create allnon variable
        self.checkboxes["All/None"].append(
            tk.BooleanVar(self.root, True, name=(name + "_All/None"))
        )
        # create centered allnon checkbox
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
            self.checkboxes[item].append(
                tk.BooleanVar(self.root, True, name=name + str(item))
            )
            # create checkbox
            self.checkboxes[item].append(
                ttk.Checkbutton(
                    self.frame,
                    text=item,
                    variable=self.checkboxes[item][0],
                    width=25,
                    command=checkbox_click,
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
                self.root.setvar(name=self.name + str(i), value=True)
        else:
            # changes state of all checkboxes to false
            for i in self.checkboxes:
                self.root.setvar(name=self.name + str(i), value=False)


class Buttons:
    def __init__(self, df_results, frame_buttons):
        # creat list of filter buttons
        self.list = []

        # add serial number button
        name = df_results.index.name
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
            width=17,
            command=(lambda: button_click(self)),
        )


def clear_av_min_max():
    # remove each child in
    for children in frame_av_min_max.winfo_children():
        if type(children) != tk.Toplevel:
            children.pack_forget()


def checkbox_click():
    # filters the data
    filter_data()
    # if window open load the data frame again
    if root.getvar(name="View_Data") == 1:
        load_df_window()


def close_window():
    # destroy the window
    window.destroy(),
    # sets window var to false
    root.setvar(name="View_Data", value=False),
    # sets scroll wheel to root scroll
    canvas_scroll.bind_all(
        "<MouseWheel>",
        lambda e: canvas_scroll.yview_scroll(int(-1 * (e.delta / 120)), "units"),
    ),


def filter_table():
    # creating list of all active columns
    col = []
    # go through list of all columns
    for i in column_checkbox.ls:
        # check if the checkbox is pressed
        try:
            if column_checkbox.checkboxes[i][0].get():
                # formats the column name and adds it to col
                col.append(i.replace(" ", "_"))
        except:
            col.append(i.replace(" ", "_"))

    # returns the filtered df with only the selected columns
    return df_filt[col]


def load_df_window():
    # delete old content
    tv.delete(*tv.get_children())

    df_table = filter_table()
    # sets the columns of the df to columns of tv
    col_ls = df_table.columns.tolist()
    col_ls.insert(0, "Serial_number")
    tv["column"] = col_ls
    # shows the headers
    tv["show"] = "headings"

    # adds set column name as header
    for column in tv["columns"]:
        tv.heading(column, text=column.replace("_", " "))

    # adds dataframe to treeview
    for i in df_table.index.to_list():
        # creates row for each index
        row = df_table.loc[i].tolist()
        # adds index to row
        row.insert(0, i)
        # add row to treeview
        tv.insert("", "end", values=row)


def av_min_max_click():
    # sets plot to bellcurve
    selected_plot.set("bellcurve")
    # filters the data
    filter_data()
    if root.getvar(name="View_Data") == 1:
        window.lift()


def input_error(text):
    # removes always on top from window
    window.attributes("-topmost", False)

    # shows error
    messagebox.showerror(title="Input error", message=text)

    # sets always on top from window
    window.attributes("-topmost", True)


def calc_chance():
    # setting upper and lower bound to input
    try:
        lowerbound = window.getvar(name="Min")
        upperbound = window.getvar(name="Max")
    except:
        text = (
            "Please make sure to enter a value in \n the minimum and maximum chance.",
        )
        input_error(text)
        return None

    # checking if upper and lower bound are numbers
    try:
        lowerbound = float(lowerbound)
        upperbound = float(upperbound)
    except:
        text = "Make sure the input is Numeric"
        input_error(text)
        return None

    # checks if lowerbound is smaller than upperbound
    if lowerbound > upperbound:
        text = "Make sure lowerbound < upperbound"
        input_error(text)
        return None

    # creating pandas dataframe with x and y values of graph
    df_chance = pd.DataFrame(data=({"x-axis": x_axis, "y-axis": y_axis}))

    # filter the dataframe for upper and lower bounds
    df_chance = df_chance[
        (df_chance["x-axis"] >= lowerbound) & (df_chance["x-axis"] <= upperbound)
    ]

    # calculating the chance
    chance = df_chance["y-axis"].sum()
    # changing output lable
    window.setvar(name="Chance", value=("Chance: " + str(round(chance, 2)) + " %"))


def draw_window_calc_chance(frame_get_chance):
    # creating tk variables for min and max
    var_min = tk.StringVar(window, name="Min")
    var_max = tk.StringVar(window, name="Max")
    var_chance = tk.StringVar(window, name="Chance")

    # creating and placing lable and entry min / max
    ttk.Label(frame_get_chance, padding=4, text="Minimum gas reduction").grid(
        row=0, column=0, sticky="w"
    )

    ttk.Entry(frame_get_chance, textvariable=var_min).grid(row=0, column=1)

    ttk.Label(frame_get_chance, padding=4, text="Maximum gas reduction").grid(
        row=1, column=0, sticky="w"
    )

    ttk.Entry(frame_get_chance, textvariable=var_max).grid(row=1, column=1)

    # creating button and lable for calculating chance
    ttk.Button(frame_get_chance, text="Calculate chance", command=calc_chance).grid(
        row=2, column=0
    )
    ttk.Label(frame_get_chance, padding=4, textvariable=var_chance).grid(
        row=2, column=1, sticky="w"
    )


def window_view_data():
    # check if viewdata is True
    if root.getvar(name="View_Data") == 1:
        return None

    # set view_data var to true
    root.setvar(name="View_Data", value=True)

    # create new window
    global window
    window = tk.Toplevel(root)
    window.geometry("1000x600")
    window.iconbitmap("./resources/tool_logo.ico")
    window.attributes("-topmost", True)

    # certing frames
    frame_select_col = ttk.Frame(window, padding=p)
    frame_get_chance = ttk.Frame(window, padding=p)
    frame_view_df = ttk.Frame(window, padding=p)
    frame_av_max_min = ttk.Frame(window, padding=p)

    # creating scrollable column view
    canvas_scroll_win = tk.Canvas(frame_select_col, highlightthickness=0)

    # create frame for checkboxes
    frame_scroll_items_win = ttk.Frame(canvas_scroll_win, padding=10)

    # add scrolling frame to canvas
    canvas_scroll_win.create_window((0, 0), window=frame_scroll_items_win, anchor="nw")

    # placing items to window
    frame_select_col.place(relheight=1, width=scrol_width_window)
    canvas_scroll_win.place(relheight=1, relwidth=0.9)

    frame_av_max_min.place(
        x=scrol_width_window,
        y=5,
        height=127,
        width=130,
    )

    frame_get_chance.place(
        x=scrol_width_window + 130,
        height=button_height,
        relwidth=1,
        width=-scrol_width_window - button_height,
    )

    frame_view_df.place(
        relwidth=1,
        relheight=1,
        x=scrol_width_window,
        width=-scrol_width_window,
        y=button_height,
        height=-button_height,
    )

    # set frame of checkboxes
    Checkboxes.frame = frame_scroll_items_win
    Checkboxes.root = window

    # creating list with columns
    col_list = df_results.columns.tolist()

    # replacing _ with spaces
    for i in range(len(col_list)):
        col_list[i] = col_list[i].replace("_", " ")

    # creating checkboxes
    global column_checkbox
    column_checkbox = Checkboxes(col_list, "Columns")

    # places each checkbox in dict
    row = 0
    for i in column_checkbox.checkboxes:
        column_checkbox.checkboxes[i][1].grid(column=0, row=row)
        row += 1

    # create scrollbar
    scrollbar = ttk.Scrollbar(
        frame_select_col, orient=tk.VERTICAL, command=canvas_scroll_win.yview
    )

    # add scrolling features
    canvas_scroll_win.configure(yscrollcommand=scrollbar.set)

    canvas_scroll_win.bind(
        "<Configure>",
        lambda e: canvas_scroll_win.configure(
            scrollregion=canvas_scroll_win.bbox("all")
        ),
    )

    canvas_scroll.bind_all(
        "<MouseWheel>",
        lambda e: canvas_scroll_win.yview_scroll(int(-1 * (e.delta / 120)), "units"),
    )
    # placing scrollbar
    scrollbar.place(relheight=1, relwidth=0.1, relx=0.9)

    # run configure event
    window.update()
    canvas_scroll_win.event_generate("<Configure>")

    # creating and placing treeview for df_results
    global tv
    tv = ttk.Treeview(frame_view_df)
    tv.place(relwidth=1, relheight=1)

    # creating scrollbars for treeview
    treescrolly = ttk.Scrollbar(frame_view_df, orient="vertical", command=tv.yview)
    treescrollx = ttk.Scrollbar(frame_view_df, orient="horizontal", command=tv.xview)

    # configuring treeview
    tv.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)

    # placing scrollbars
    treescrolly.place(
        relx=1,
        x=-scrollbar_width,
        width=scrollbar_width,
        relheight=1,
        height=-scrollbar_width,
    )
    treescrollx.place(
        rely=1,
        y=-scrollbar_width,
        height=scrollbar_width,
        relwidth=1,
        width=-scrollbar_width,
    )

    # adding data to treeview
    load_df_window()

    draw_radio_av_min_max(frame_av_max_min)

    draw_window_calc_chance(frame_get_chance)
    # when delete window (cross top right) is pressed destroy window and set var to false
    window.protocol("WM_DELETE_WINDOW", close_window)


def new_analysis():
    root.destroy()
    analysis.main()


def filter_data():
    global df_filt
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
            # check if checkbox is False
            if not item.checkboxes[i][0].get():
                # check if column is the index column
                if key == df_filt.index.name:
                    # drop the index
                    df_filt.drop(index=i, inplace=True)
                else:
                    # filter results
                    df_filt = df_filt[df_filt[key] != i]

    global amount_of_houses
    amount_of_houses = len(df_filt)

    # calculate mean
    global mean, std
    if selected_av_min_max.get() == "Av":
        mean = df_filt["Av_gas_reduction"].mean()
        # calculate standard deviation
        std = df_filt["Av_gas_reduction"].std()
    elif selected_av_min_max.get() == "Min":
        mean = df_filt["Min_gas_reduction"].mean()
        # calculate standard deviation
        std = df_filt["Min_gas_reduction"].std()
    elif selected_av_min_max.get() == "Max":
        mean = df_filt["Max_gas_reduction"].mean()
        # calculate standard deviation
        std = df_filt["Max_gas_reduction"].std()

    # checks if there is enough data in the selected houses
    if selected_plot.get() == "bellcurve":
        if isnan(mean) or isnan(std):
            messagebox.showerror(
                title="Data error",
                message="With the currently selected filters the dataframe has no results. \nTry a different filter!",
            )
            return 0

    elif selected_plot.get() == "bar" and amount_of_houses == 0:
        messagebox.showerror(
            title="Data error",
            message="With the currently selected filters the dataframe has no results. \nTry a different filter!",
        )
        return 0

    elif selected_plot.get() == "bar filt" and amount_of_houses == 0:
        messagebox.showerror(
            title="Data error",
            message="With the currently selected filters the dataframe has no results. \nTry a different filter!",
        )
        return 0

    elif selected_plot.get() == "bar red" and amount_of_houses == 0:
        messagebox.showerror(
            title="Data error",
            message="With the currently selected filters the dataframe has no results. \nTry a different filter!",
        )
        return 0

    draw_plot()


def menu_bar():
    # add menu bar on top
    menubar = tk.Menu()

    # add file menu
    mb_file = tk.Menu(menubar, tearoff=False)
    # add new analysis button
    mb_file.add_command(label="New Analysis", command=new_analysis)
    # adding separator
    mb_file.add_separator()
    # add exit button
    mb_file.add_command(label="Exit", command=root.destroy)

    # add file to menu bar
    menubar.add_cascade(label="File", menu=mb_file)

    # add view data
    menubar.add_cascade(label="View Data", command=window_view_data)
    # creating boolean and setting value for view data
    tk.BooleanVar(root, name="View_Data")
    root.setvar(name="View_Data", value=False)

    # sets menubar
    root.config(menu=menubar)


def draw_select_plot(frame_select_plot):

    # create variables
    width = 85

    # create plot variable
    global selected_plot
    selected_plot = tk.StringVar(root, name="plot", value="bellcurve")

    #
    ttk.Label(frame_select_plot, text="Select chart type").pack(anchor="w")
    # create radio buttons
    ttk.Radiobutton(
        frame_select_plot,
        variable=selected_plot,
        text="bellcurve",
        value="bellcurve",
        width=width,
        command=filter_data,
    ).pack(anchor="w")

    ttk.Radiobutton(
        frame_select_plot,
        variable=selected_plot,
        text="bar reduction",
        value="bar red",
        width=width,
        command=filter_data,
    ).pack(anchor="w")

    ttk.Radiobutton(
        frame_select_plot,
        variable=selected_plot,
        text="bar normalized",
        value="bar",
        width=width,
        command=filter_data,
    ).pack(anchor="w")

    ttk.Radiobutton(
        frame_select_plot,
        variable=selected_plot,
        text="bar variable term",
        value="bar filt",
        width=width,
        command=filter_data,
    ).pack(anchor="w")

    # center the buttons
    frame_select_plot.grid_rowconfigure(0)


def draw_radio_av_min_max(frame):
    # set variables
    width = 10

    # adding lable
    ttk.Label(frame, text="Chart settings").pack(anchor="w")

    # draw and place radio buttons
    ttk.Radiobutton(
        frame,
        variable=selected_av_min_max,
        text="Average",
        value="Av",
        width=width,
        command=av_min_max_click,
    ).pack(anchor="nw")

    ttk.Radiobutton(
        frame,
        variable=selected_av_min_max,
        text="Worst case",
        value="Min",
        width=width,
        command=av_min_max_click,
    ).pack(anchor="nw")

    ttk.Radiobutton(
        frame,
        variable=selected_av_min_max,
        text="Best case",
        value="Max",
        width=width,
        command=av_min_max_click,
    ).pack(anchor="nw")


def plot_bellcurve(plots):
    # colors
    std2_color = "Purple"

    # creates x-axis values
    global x_axis
    x_axis = np.arange(mean - 6 * std, 6 * std + mean, 0.01)
    # creates y-axis values
    global y_axis
    y_axis = norm.pdf(x_axis, mean, std)

    # add plot
    ax1 = plots.add_subplot()

    # plot x and y values
    ax1.plot(x_axis, y_axis, color="black")

    # set title and lables
    ax1.set_title("Bellcurve gas reduction")
    ax1.set_xlabel("Gas Reduction(%)")
    ax1.set_ylabel("Density")

    # creates x-axis ticks
    pos_x = []
    i = 0
    j = 2
    for i in range(2 * j + 1):
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
    ax1.fill_between(x_fil2, y_fil2, alpha=0.5, color=std2_color, label="68.2%")
    ax1.fill_between(x_fil3, y_fil3, alpha=0.25, color=std2_color, label="95.4%")

    # set x and y axis limits
    ax1.set_xlim(mean - 3 * std, 3 * std + mean)
    ax1.set_ylim(0)
    ax1.legend()

    return plots


def plot_bar(plots):

    # Defining constatns
    width = 0.25
    capsize = 3

    # creates x-axis values
    x_axis = df_filt.index.tolist()
    x_indexes = np.arange(len(x_axis))

    # creates y-axis values
    y_axis1 = df_filt["Av_new_usage"].tolist()
    y_axis2 = df_filt["Av_old_usage"].tolist()

    # calculate the average usage and sets to y_axis values
    y_axis4 = df_filt["Av_use"].tolist()
    for i in range(len(y_axis4)):
        y_axis4[i] = 365 * y_axis4[i]

    # creating list of min and max old and new usage
    ls_min_new = df_filt["Min_new_usage"].tolist()
    ls_max_new = df_filt["Max_new_usage"].tolist()
    ls_min_old = df_filt["Min_old_usage"].tolist()
    ls_max_old = df_filt["Max_old_usage"].tolist()

    # creating error bars for axis 1 and 2
    er_min_axis1 = df_filt["Av_new_usage"].tolist()
    er_max_axis1 = df_filt["Max_new_usage"].tolist()
    er_min_axis2 = df_filt["Av_old_usage"].tolist()
    er_max_axis2 = df_filt["Max_old_usage"].tolist()

    for i in range(len(x_axis)):
        # creating error bars
        er_min_axis1[i] -= ls_min_new[i] + y_axis4[i]
        er_max_axis1[i] -= y_axis1[i] + y_axis4[i]

        # creating error bars
        er_min_axis2[i] -= ls_min_old[i] + y_axis4[i]
        er_max_axis2[i] -= y_axis2[i] + y_axis4[i]

        # adding average use to total use
        y_axis1[i] += y_axis4[i]
        y_axis2[i] += y_axis4[i]

    # creating money saved axis
    y_axis3 = []
    er_min_axis3 = []
    er_max_axis3 = []

    for i in range(len(y_axis1)):
        y_axis3.append((y_axis2[i] - y_axis1[i]) * gas_price)
        er_min_axis3.append(y_axis3[i] - (ls_min_old[i] - ls_max_new[i]) * gas_price)
        er_max_axis3.append((ls_max_old[i] - ls_min_new[i]) * gas_price - y_axis3[i])

    # add plot
    ax1 = plots.add_subplot()

    # plot x and y values
    ax1.bar(
        x_indexes - width,
        y_axis2,
        width=width,
        color="#ED254E",
        label="Gas usage before balancing (m³)",
    )

    ax1.bar(
        x_indexes,
        y_axis1,
        width=width,
        color="#3E7CB1",
        label="Gas usage after balancing (m³)",
    )

    ax1.bar(
        x_indexes + width,
        y_axis3,
        width=width,
        color="green",
        label="Cost reduction (€)",
    )

    ax1.bar(
        x_indexes - 0.5 * width,
        y_axis4,
        width=2 * width,
        color="#FFAE03",
        label="Non-heating gas usage (m³)",
    )

    # plotting the errorbars
    ax1.errorbar(
        x_indexes,
        y_axis1,
        yerr=[er_min_axis1, er_max_axis1],
        fmt=" ",
        ecolor="black",
        capsize=capsize,
    )

    ax1.errorbar(
        x_indexes - width,
        y_axis2,
        yerr=[er_min_axis2, er_max_axis2],
        fmt=" ",
        ecolor="black",
        capsize=capsize,
    )

    ax1.errorbar(
        x_indexes + width,
        y_axis3,
        yerr=[er_min_axis3, er_max_axis3],
        fmt=" ",
        ecolor="black",
        capsize=capsize,
    )
    # set title and lables
    ax1.set_title("Gas usage")
    ax1.set_xlabel("Houses")

    # create boundaries
    ax1.set_ylim(0)
    ax1.set_xlim(-0.5)

    # add legend
    ax1.legend(loc=1)

    # add grid
    ax1.yaxis.grid(color="gray")
    ax1.set_axisbelow(True)

    # set ticks
    plt.setp(ax1, xticks=x_indexes, xticklabels=x_axis)

    return (plots, ax1)


def plot_bar_filter(plots):

    # Defining constatns
    width = 0.25
    capsize = 3
    dict_df = {}

    # creates x-axis values
    x_axis = df_filt.index.tolist()
    x_indexes = np.arange(len(x_axis))

    ls_av_use = df_filt["Av_use"].tolist()

    # creates y-axis values
    dict_df["y_axis1"] = []
    dict_df["y1_min"] = []
    dict_df["y1_max"] = []
    dict_df["Er_y1_min"] = []
    dict_df["Er_y1_max"] = []

    # creating second y axis
    dict_df["y_axis2"] = df_filt["Av_old_usage"].tolist()

    # money saved axis
    dict_df["y_axis3"] = []
    dict_df["Er_y3_min"] = []
    dict_df["Er_y3_max"] = []

    # creating list of min and max old and new usage
    dict_df["Min_old"] = df_filt["Min_old_usage"].tolist()
    dict_df["Max_old"] = df_filt["Max_old_usage"].tolist()

    # creating error bars for axis2
    dict_df["Er_y2_min"] = df_filt["Av_old_usage"].tolist()
    dict_df["Er_y2_max"] = df_filt["Max_old_usage"].tolist()

    for i in range(len(x_axis)):
        # defining constants based on serial number
        if df_filt.loc[x_axis[i]]["Gasmeter_type"] == "Mechanical meter":
            aurum_err = 0.95
        else:
            aurum_err = 1

        flow_dev_min = (100 - 0.17) / 100
        flow_dev_max = (100 + 0.92) / 100

        # filtering the dataframe to serial number and date period
        new_use_snr = df_aurum[df_aurum["Serialnumber"] == x_axis[i]]
        new_use_snr = new_use_snr.set_index("Date_time")["Measurement value"]
        new_use_snr = new_use_snr[
            root.getvar(name="Begin_date") : root.getvar(name="End_date")
        ]
        new_use_days = new_use_snr.index.size / 24
        new_use_snr = new_use_snr.sum()

        # calculating the sum of all measurements and add it to the y_axis list
        dict_df["y_axis1"].append(new_use_snr)
        dict_df["y1_min"].append(new_use_snr / flow_dev_max * aurum_err)
        dict_df["y1_max"].append(new_use_snr / flow_dev_min / aurum_err)

        # calculating error bars y1
        dict_df["Er_y1_min"].append(new_use_snr - dict_df["y1_min"][i])
        dict_df["Er_y1_max"].append(dict_df["y1_max"][i] - new_use_snr)

        # calculating the weighted degree days
        weighted_degr_2019 = df_knmi["2019"]["weight_degr_days"].sum()
        weighted_degr_period = df_knmi[
            root.getvar(name="Begin_date") : root.getvar(name="End_date")
        ]["weight_degr_days"].sum()

        # transforming the total old usage to old usage from this period
        for j in dict_df:
            if (
                j == "y_axis2"
                or j == "Min_old"
                or j == "Max_old"
                or j == "Er_y2_min"
                or j == "Er_y2_max"
            ):
                dict_df[j][i] = (
                    dict_df[j][i] / weighted_degr_2019 * weighted_degr_period
                    + ls_av_use[i] * new_use_days
                )

        # creating error bars
        dict_df["Er_y2_min"][i] -= dict_df["Min_old"][i]
        dict_df["Er_y2_max"][i] -= dict_df["y_axis2"][i]

        # calculating money saved
        dict_df["y_axis3"].append(
            (dict_df["y_axis2"][i] - dict_df["y_axis1"][i]) * gas_price
        )
        dict_df["Er_y3_min"].append(
            dict_df["y_axis3"][i]
            - (dict_df["Min_old"][i] - dict_df["y1_max"][i]) * gas_price
        )
        dict_df["Er_y3_max"].append(
            (dict_df["Max_old"][i] - dict_df["y1_min"][i]) * gas_price
            - dict_df["y_axis3"][i]
        )

    # add plot
    ax1 = plots.add_subplot()

    # plot x and y values
    ax1.bar(
        x_indexes - width,
        dict_df["y_axis2"],
        width=width,
        color="#ED254E",
        label="Gas usage before balancing (m³)",
    )

    ax1.bar(
        x_indexes,
        dict_df["y_axis1"],
        width=width,
        color="#3E7CB1",
        label="Gas usage after balancing (m³)",
    )

    ax1.bar(
        x_indexes + width,
        dict_df["y_axis3"],
        width=width,
        color="green",
        label="Cost reduction (€)",
    )

    # plotting the errorbars
    ax1.errorbar(
        x_indexes,
        dict_df["y_axis1"],
        yerr=[dict_df["Er_y1_min"], dict_df["Er_y1_max"]],
        fmt=" ",
        ecolor="black",
        capsize=capsize,
    )

    ax1.errorbar(
        x_indexes - width,
        dict_df["y_axis2"],
        yerr=[dict_df["Er_y2_min"], dict_df["Er_y2_max"]],
        fmt=" ",
        ecolor="black",
        capsize=capsize,
    )

    ax1.errorbar(
        x_indexes + width,
        dict_df["y_axis3"],
        yerr=[dict_df["Er_y3_min"], dict_df["Er_y3_max"]],
        fmt=" ",
        ecolor="black",
        capsize=capsize,
    )

    # set title and lables
    ax1.set_title("Gas usage")
    ax1.set_xlabel("Houses")

    # create boundaries
    ax1.set_ylim(0)
    ax1.set_xlim(-0.5)

    # add legend
    ax1.legend(loc=1)

    # add grid
    ax1.yaxis.grid(color="gray")
    ax1.set_axisbelow(True)

    # set ticks
    plt.setp(ax1, xticks=x_indexes, xticklabels=x_axis)

    return (plots, ax1)


def plot_bar_red(plots):
    # Defining constatns
    capsize = 3

    # creates x-axis values
    x_axis = df_filt.index.tolist()
    x_indexes = np.arange(len(x_axis))

    # creates y-axis values
    y_axis1 = df_filt["Av_gas_reduction"].tolist()

    # creating list of min reduction
    ls_min_red = df_filt["Min_gas_reduction"].tolist()

    # creating error bars for axis 1 and 2
    er_min_axis1 = df_filt["Av_gas_reduction"].tolist()
    er_max_axis1 = df_filt["Max_gas_reduction"].tolist()

    for i in range(len(x_axis)):
        # creating error bars
        er_min_axis1[i] -= ls_min_red[i]
        er_max_axis1[i] -= y_axis1[i]

    # add plot
    ax1 = plots.add_subplot()

    # plot x and y values
    ax1.bar(
        x_indexes,
        y_axis1,
        color="#C476E3",
    )

    # plotting the errorbars
    ax1.errorbar(
        x_indexes,
        y_axis1,
        yerr=[er_min_axis1, er_max_axis1],
        fmt=" ",
        ecolor="black",
        capsize=capsize,
    )

    # set title and lables
    ax1.set_title("Gas reduction")
    ax1.set_xlabel("Houses")
    ax1.set_ylabel("reduction (%)")

    # create boundaries
    ax1.set_xlim(-0.5)

    # add grid
    ax1.yaxis.grid(color="gray")
    ax1.set_axisbelow(True)

    # set ticks
    plt.setp(ax1, xticks=x_indexes, xticklabels=x_axis)

    return (plots, ax1)


def reset_filter():

    # reset all filters
    for _, i in all_checkboxes.dict.items():
        i.checkboxes["All/None"][0].set(True)
        i.check_all_items()

    # reset hte graph
    checkbox_click()


def draw_plot():
    # set gasprice variable
    global gas_price
    try:
        gas_price = float(root.getvar(name="Gas_price"))
    except:
        messagebox.showerror("Gas price error", "Make sure the gas price is numeric!")
        return None

    # deletes old content
    for items in frame_plots.winfo_children():
        items.destroy()

    for items in frame_plot_info.winfo_children():
        items.destroy()

    # creates figure
    plots = Figure(
        figsize=(15, 15),
        dpi=96,
        facecolor="#EFF0F1",
        constrained_layout=True,
    )

    # if bellcurve is selected
    if selected_plot.get() == "bellcurve":
        # create bell curve
        plots = plot_bellcurve(plots)

        # create info text
        text = "Number of houses: {} \nMean:{} \nStandard deviation: {}".format(
            amount_of_houses, round(mean, 2), round(std, 2)
        )

        # clearing frame av min max
        clear_av_min_max()

        # adding radio buttons to average min max
        draw_radio_av_min_max(frame_av_min_max)

    # if bar graph is selected
    elif selected_plot.get() == "bar":
        # create bar graph
        plots, ax1 = plot_bar(plots)
        # create info text
        text = "Normalised to 2019\nGas price per m³:€{}".format(
            root.getvar(name="Gas_price")
        )

        root.update()
        width = root.winfo_width() - scrol_width - select_plot_width

        # check if x-axis lables can be placed (size restrictions)
        if width // amount_of_houses < 80:
            ax1.set_xlabel("")
            plt.setp(ax1, xticks=[], xticklabels=[])

        # clearing frame av min max
        clear_av_min_max()

        # adding lable to av min max frame
        ttk.Label(frame_av_min_max, text="Chart settings").pack()

        # adding lable:
        ttk.Label(frame_av_min_max, text="Gas price per m³").pack()
        ttk.Entry(frame_av_min_max, textvariable="Gas_price").pack(pady=3)
        ttk.Button(frame_av_min_max, text="Apply", command=filter_data).pack()

    # if bar graph reduction is selected
    elif selected_plot.get() == "bar red":
        # create bar graph
        plots, ax1 = plot_bar_red(plots)
        # create info text
        text = "Projected gas reduction for heating after balancing the radiators."

        # update the root
        root.update()
        width = root.winfo_width() - scrol_width - select_plot_width

        # check if x-axis lables can be placed (size restrictions)
        if width // amount_of_houses < 80:
            ax1.set_xlabel("")
            plt.setp(ax1, xticks=[], xticklabels=[])

        # clearing frame av min max
        clear_av_min_max()

    # if bar graph filterable is selected
    elif selected_plot.get() == "bar filt":
        # create bar graph
        plots, ax1 = plot_bar_filter(plots)
        # create info text
        text = "Gas consumption from\n{} untill {}.\n\nGas price per m³:€{}".format(
            root.getvar(name="Begin_date"),
            root.getvar(name="End_date"),
            root.getvar(name="Gas_price"),
        )

        root.update()
        width = root.winfo_width() - scrol_width - select_plot_width

        # check if x-axis lables can be placed (size restrictions)
        if width // amount_of_houses < 80:
            ax1.set_xlabel("")
            plt.setp(ax1, xticks=[], xticklabels=[])

        # clearing frame av min max
        clear_av_min_max()

        # adding lable to av min max frame
        ttk.Label(frame_av_min_max, text="Chart settings").pack()

        # adding lable:
        ttk.Label(frame_av_min_max, text="Gas price per m³").pack()
        ttk.Entry(frame_av_min_max, textvariable="Gas_price").pack(pady=3)
        ttk.Label(frame_av_min_max, text="Begin date(y-m-d)").pack()
        ttk.Entry(frame_av_min_max, textvariable="Begin_date").pack(pady=3)
        ttk.Label(frame_av_min_max, text="End date(y-m-d)").pack()
        ttk.Entry(frame_av_min_max, textvariable="End_date").pack(pady=3)
        ttk.Button(frame_av_min_max, text="Apply", command=filter_data).pack()

    # create and place plot on canvas
    canvas_plots = FigureCanvasTkAgg(plots, master=frame_plots)
    canvas_plots.draw()
    canvas_plots.get_tk_widget().place(anchor="sw")

    # add toolbar
    toolbar = NavigationToolbar2Tk(canvas_plots, frame_plots, pack_toolbar=False)
    toolbar.pack(side=tk.BOTTOM, fill=tk.X, padx=70)
    toolbar.update()
    canvas_plots.get_tk_widget().pack(anchor="w")

    # creating labels
    label = ttk.Label(
        frame_plot_info,
        text=text,
        relief=tk.SOLID,
        borderwidth=2,
        padding=3,
        wraplength=200,
    )
    # add text to label frame
    label.pack(anchor="ne", pady=p)


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
        if i == "All/None":
            dict_checkbox[i][1].grid(column=0, row=0)
        else:
            dict_checkbox[i][1].grid(column=0, row=row, columnspan=3)
        row += 1
    canvas_scroll.yview_moveto(0)


def button_click(button):
    global last_pressed
    # run draw checkboxes
    draw_checkboxes(button.name, all_checkboxes)

    button.button.state(["pressed", "!disabled"])

    # try to set "unpress" laspressed
    try:
        if last_pressed != button.button:
            last_pressed.state(["!pressed", "!disabled"])
    except Exception:
        pass

    # set button to pressed
    last_pressed = button.button


def draw_buttons(df_results, frame_buttons):

    buttons = Buttons(df_results, frame_buttons)
    button_list = buttons.list
    visable_buttons = [
        "Serial_number",
        "Residents",
        "House_type",
        "Energy_label",
        "Postal_code",
        "Gasmeter_type",
        "District_heating",
        "Underfloor_heating",
        "Construction_year",
        "Influence_on_heating",
        "Change_in_residents",
        "Change_in_behaviour",
        "Average_use_data",
        "Radiator_valve",
    ]
    # column and row number
    j = 0
    i = 0
    # add each button
    for button in button_list:
        if button.name in visable_buttons:
            # checks if button is in row 0 or 1
            if (i % 3) == 0:
                # adds button to row 0
                button.button.grid(row=0, column=j, padx=3, pady=3)
            elif (i % 3) == 1:
                # adds button to row 1
                button.button.grid(row=1, column=j, padx=3, pady=3)
            elif (i % 3) == 2:
                # adds button to row 2
                button.button.grid(row=2, column=j, padx=3, pady=3)
                j += 1

            i += 1

    # add reset filter button
    q = ttk.Style()
    q.configure("my3.TButton", foreground="#e0465d")

    ttk.Button(
        frame_buttons,
        text="Reset filters",
        style="my3.TButton",
        command=reset_filter,
    ).grid(
        row=2,
        column=4,
        sticky="NESW",
        pady=3,
        padx=3,
    )

    return button_list[0]


def results_gui(df):
    global df_results, df_aurum, df_knmi

    # sets results dataframe from analysis as df_results
    df_results = df

    # changes datatype to int
    df_results["Residents"] = df_results["Residents"].astype(int)
    df_results["Solar_panels"] = df_results["Solar_panels"].astype(int)
    df_results["Construction_year"] = df_results["Construction_year"].astype(int)

    # round floats to 3 decimals
    for column in df_results.columns:
        if df_results[column].dtype == float:
            df_results[column] = round(df_results[column], 3)

    # open the complete aurum data frame
    df_aurum = pd.read_csv(
        "./data/aurum.csv", index_col=0, parse_dates=["Measurement date"]
    )
    # changing datatype from string to time
    df_aurum["Measurement time"] = df_aurum["Measurement time"].apply(
        lambda x: np.timedelta64(x.split(":")[0], "h")
    )

    df_aurum["Measurement date"] = pd.to_datetime(
        df_aurum["Measurement date"], format="%d-%m-%Y"
    )

    # creating new collumn with date and time combined
    df_aurum["Date_time"] = df_aurum["Measurement date"] + df_aurum["Measurement time"]

    # opening the knmi data frame
    df_knmi = pd.read_csv(
        "./data/knmi_data.csv", parse_dates=["Date"], index_col="Date"
    )

    # setup the gui
    global root
    root = ThemedTk()
    root.get_themes()
    root.set_theme("breeze")
    root.geometry("1200x600")
    root.title("Balancing Radiators Analysis")
    root.iconbitmap("./resources/tool_logo.ico")

    # changeable parameters
    global p, scrol_width, button_height, select_plot_width, scrol_width_window, scrollbar_width

    p = 12
    scrol_width = 200
    button_height = 120
    button_width = 750
    select_plot_width = 155
    select_plot_height = 145
    scrol_width_window = 275
    scrollbar_width = 15

    # create variable for gas price begin and end date
    tk.StringVar(root, name="Gas_price")
    root.setvar("Gas_price", value="0.79")

    tk.StringVar(root, name="Begin_date")
    root.setvar("Begin_date", value="2020-9-11")
    tk.StringVar(root, name="End_date")
    root.setvar("End_date", value="2020-9")

    # add menubar
    menu_bar()

    # create frames
    frame_buttons = ttk.Frame(root, padding=p)
    frame_scroll = ttk.Frame(root, padding=p)

    global frame_plot_info
    frame_plot_info = ttk.Frame(root, padding=p)

    frame_select_plot = ttk.Frame(root, padding=p)

    global frame_plots
    frame_plots = ttk.Frame(root, padding=p)

    global frame_av_min_max
    frame_av_min_max = ttk.Frame(root, padding=p)

    # place frames
    frame_buttons.place(
        x=scrol_width,
        width=button_width,
        height=button_height,
    )

    frame_scroll.place(width=scrol_width, relheight=1)

    frame_plot_info.place(
        x=scrol_width + button_width,
        height=button_height + 50,
        relwidth=1,
        width=-button_width - scrol_width,
    )

    frame_select_plot.place(
        x=scrol_width,
        y=button_height + 25,
        height=select_plot_height,
        width=select_plot_width,
    )

    frame_plots.place(
        x=scrol_width + select_plot_width,
        y=button_height,
        relwidth=1,
        relheight=1,
        width=-scrol_width - select_plot_width,
        height=-button_height,
    )

    # create canvas scrollbar
    global canvas_scroll
    canvas_scroll = tk.Canvas(frame_scroll, highlightthickness=0)

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
    global all_checkboxes
    all_checkboxes = AllCheckboxes(df_results)

    # create filter buttons
    first_button = draw_buttons(df_results, frame_buttons)

    # adding first checkboxes
    button_click(first_button)

    # creating and adding type of plots
    draw_select_plot(frame_select_plot)

    # creating radio buttons for selecting av min max
    global selected_av_min_max
    selected_av_min_max = tk.StringVar(root, name="av_min_max", value="bellcurve")
    root.setvar(name="av_min_max", value="Av")

    # placing frame av min max
    frame_av_min_max.place(
        x=scrol_width,
        relheight=1,
        height=-button_height - select_plot_height - 50,
        width=select_plot_width,
        y=button_height + select_plot_height + 50,
    )

    # draw plot
    filter_data()

    # run configure event
    root.update()
    canvas_scroll.event_generate("<Configure>")

    root.mainloop()


def main():
    # path to results file
    res_path = "./results/result 2021-01-28_14-01.csv"
    # create data frame
    df = pd.read_csv(res_path, index_col="Serial_number")
    # opens gui
    results_gui(df)


if __name__ == "__main__":
    main()
