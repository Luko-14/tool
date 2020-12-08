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
            tk.BooleanVar(root, True, name=(name + "_All/None"))
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
                tk.BooleanVar(root, True, name=name + str(item))
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
                root.setvar(name=self.name + str(i), value=True)
        else:
            # changes state of all checkboxes to false
            for i in self.checkboxes:
                root.setvar(name=self.name + str(i), value=False)


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
            width=15,
            command=(lambda: button_click(self)),
        )


def checkbox_click():
    if root.getvar(name="View_Data") == 0:
        filter_data()
        return None


def close_window():
    window.destroy(),
    root.setvar(name="View_Data", value=False),
    canvas_scroll.bind_all(
        "<MouseWheel>",
        lambda e: canvas_scroll.yview_scroll(int(-1 * (e.delta / 120)), "units"),
    ),


def window_view_data():
    # check if viewdata is True
    if root.getvar(name="View_Data") == 1:
        return None

    # set view_data var to true
    root.setvar(name="View_Data", value=True)

    # create new window
    global window
    window = tk.Toplevel(root)
    window.geometry("1000x500")
    window.iconbitmap("./resources/tool_logo.ico")

    # certing frames
    frame_select_col = ttk.Frame(window, padding=p)
    frame_get_change = ttk.Frame(window, padding=p)
    frame_view_df = ttk.Frame(window, padding=p)

    # creating scrollable column view
    canvas_scroll_win = tk.Canvas(frame_select_col)

    # create frame for checkboxes
    frame_scroll_items_win = ttk.Frame(canvas_scroll_win, padding=10)

    # add scrolling frame to canvas
    canvas_scroll_win.create_window((0, 0), window=frame_scroll_items_win, anchor="nw")

    # placing items to window
    frame_select_col.place(relheight=1, width=scrol_width_window)
    canvas_scroll_win.place(relheight=1, relwidth=0.9)

    frame_get_change.place(
        x=scrol_width_window,
        height=button_height,
        relwidth=1,
        width=-scrol_width_window,
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

    # creating list with columns
    col_list = df_results.columns.tolist()

    # replacing _ with spaces
    for i in range(len(col_list)):
        col_list[i] = col_list[i].replace("_", " ")

    # creating checkboxes
    column_checkbox = Checkboxes(col_list, "Columns")
    column_checkbox = column_checkbox.checkboxes

    # places each checkbox in dict
    row = 0
    for i in column_checkbox:
        column_checkbox[i][1].grid(column=0, row=row)
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
                message="With the current filters the dataframe has no results. \nTry a different filter!",
            )
            return 0

    elif selected_plot.get() == "bar" and amount_of_houses == 0:
        messagebox.showerror(
            title="Data error",
            message="With the current filters the dataframe has no results. \nTry a different filter!",
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
    # add change results file button
    # mb_file.add_command(label="Change results file", command=lambda: print("Goodbye"))
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

    width = 70
    height = 30

    global selected_plot
    selected_plot = tk.StringVar(root, name="plot", value="bellcurve")

    ttk.Radiobutton(
        frame_select_plot,
        variable=selected_plot,
        text="bell",
        value="bellcurve",
        width=width,
        command=filter_data,
    ).place(rely=0.5, y=-height, anchor="w")

    ttk.Radiobutton(
        frame_select_plot,
        variable=selected_plot,
        text="bar",
        value="bar",
        width=width,
        command=filter_data,
    ).place(rely=0.5, anchor="w")

    frame_select_plot.grid_rowconfigure(0)


def draw_radio_av_min_max():
    width = 70
    height = 30

    global selected_av_min_max
    selected_av_min_max = tk.StringVar(root, name="av_min_max", value="bellcurve")
    root.setvar(name="av_min_max", value="Av")

    ttk.Radiobutton(
        frame_av_min_max,
        variable=selected_av_min_max,
        text="Average",
        value="Av",
        width=width,
        command=filter_data,
    ).place(anchor="w")

    ttk.Radiobutton(
        frame_av_min_max,
        variable=selected_av_min_max,
        text="Minimum",
        value="Min",
        width=width,
        command=filter_data,
    ).place(y=height, anchor="w")

    ttk.Radiobutton(
        frame_av_min_max,
        variable=selected_av_min_max,
        text="Maximum",
        value="Max",
        width=width,
        command=filter_data,
    ).place(y=2 * height, anchor="w")


def plot_bellcurve(plots):
    # colors
    std2_color = "orange"
    std1_color = "red"

    # creates x-axis values
    x_axis = np.arange(mean - 3 * std, 3 * std + mean, 0.01)
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
    ax1.fill_between(x_fil2, y_fil2, alpha=0.25, color=std1_color, label="68.2")
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
        er_min_axis1[i] -= ls_min_new[i]
        er_max_axis1[i] -= y_axis1[i]

        er_min_axis2[i] -= ls_min_old[i]
        er_max_axis2[i] -= y_axis2[i]

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
        x_indexes - width, y_axis2, width=width, color="red", label="Old usage (m^3)"
    )

    ax1.bar(x_indexes, y_axis1, width=width, color="blue", label="New usage (m^3)")

    ax1.bar(
        x_indexes + width, y_axis3, width=width, color="green", label="Money saved (€)"
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
    ax1.set_xlabel("Serial number")

    # create boundaries
    ax1.set_ylim(0)
    ax1.set_xlim(-0.5)

    # add legend
    ax1.legend()
    # set ticks
    plt.setp(ax1, xticks=x_indexes, xticklabels=x_axis)

    return (plots, ax1)


def draw_plot():
    # set gasprice variable
    global gas_price
    gas_price = 0.80

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

    if selected_plot.get() == "bellcurve":
        plots = plot_bellcurve(plots)
        text = "Number of houses: {} \nMean:{} \nStandard deviation: {}".format(
            amount_of_houses, round(mean, 2), round(std, 2)
        )

        # placing min max av frame
        frame_av_min_max.place(
            x=scrol_width,
            rely=1,
            height=100,
            width=select_plot_width,
            y=-180,
        )

    elif selected_plot.get() == "bar":
        plots, ax1 = plot_bar(plots)
        text = "Normalised to 1 year\n Gas price:{}".format(round(gas_price, 2))

        root.update()
        width = root.winfo_width() - scrol_width - select_plot_width

        if width // amount_of_houses < 80:
            ax1.set_xlabel("")
            plt.setp(ax1, xticks=[], xticklabels=[])

        # removing min max av frame
        frame_av_min_max.place_forget()

    # create and place plot on canvas
    canvas_plots = FigureCanvasTkAgg(plots, master=frame_plots)
    canvas_plots.draw()
    canvas_plots.get_tk_widget().place(anchor="sw")

    # add toolbar
    toolbar = NavigationToolbar2Tk(canvas_plots, frame_plots)
    toolbar.update()
    canvas_plots.get_tk_widget().pack()

    # creating labels
    label = ttk.Label(
        frame_plot_info, text=text, relief=tk.SOLID, borderwidth=2, padding=3
    )
    # add text to label frame
    label.pack(side=tk.RIGHT)


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
                button.button.grid(row=1, column=j, padx=3, pady=3)
            elif (i % 3) == 1:
                # adds button to row 1
                button.button.grid(row=2, column=j, padx=3, pady=3)
            elif (i % 3) == 2:
                # adds button to row 2
                button.button.grid(row=3, column=j, padx=3, pady=3)
                j += 1

            i += 1

    return button_list[0]


def results_gui(df):
    global df_results
    df_results = df
    # changes datatype to int
    df_results["Residents"] = df_results["Residents"].astype(int)
    df_results["Solar_panels"] = df_results["Solar_panels"].astype(int)
    df_results["Construction_year"] = df_results["Construction_year"].astype(int)

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
    root.iconbitmap("./resources/tool_logo.ico")

    # changeable parameters
    global p, scrol_width, button_height, select_plot_width, scrol_width_window, scrollbar_width

    p = 12
    scrol_width = 200
    button_height = 120
    button_width = 510
    select_plot_width = 100
    select_plot_height = 100
    scrol_width_window = 275
    scrollbar_width = 15

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
        height=button_height,
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
    global all_checkboxes
    all_checkboxes = AllCheckboxes(df_results)

    # create filter buttons
    first_button = draw_buttons(df_results, frame_buttons)

    # adding first checkboxes
    button_click(first_button)

    # creating and adding type of plots
    draw_select_plot(frame_select_plot)

    # creating radio buttons for selecting av min max
    draw_radio_av_min_max()

    # draw plot
    filter_data()

    # run configure event
    root.update()
    canvas_scroll.event_generate("<Configure>")

    root.mainloop()


def main():
    df = pd.read_csv("./data/with errors.csv", index_col="Serial_number")
    results_gui(df)


if __name__ == "__main__":
    main()
