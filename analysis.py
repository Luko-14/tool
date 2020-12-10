import os
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

import pandas as pd
from ttkthemes.themed_tk import ThemedTk

import get_knmi_data
import tool
import results_gui


def format_month(date):
    date = date.split(" ")

    # sets month to corresponging number
    if date[0] == "Januari":
        date[0] = 1
    elif date[0] == "Februari":
        date[0] = 2
    elif date[0] == "Maart":
        date[0] = 3
    elif date[0] == "April":
        date[0] = 4
    elif date[0] == "Mei":
        date[0] = 5
    elif date[0] == "Juni":
        date[0] = 6
    elif date[0] == "Juli":
        date[0] = 7
    elif date[0] == "Augustus":
        date[0] = 8
    elif date[0] == "September":
        date[0] = 9
    elif date[0] == "Oktober":
        date[0] = 10
    elif date[0] == "November":
        date[0] = 11
    elif date[0] == "December":
        date[0] = 12
    else:
        return False

    # converts int to  string
    date[0] = str(date[0])

    # returns date (m-y)
    return "-".join(date)


# creating a new analysis
def analyze_house(i, average_dates, comp_dates):
    Serial_number = i

    # filter df for serial number
    df_snr = tool.filter_df(df_aurum, Serial_number)

    # find the old usage for the serial number
    try:
        old_usage_snr = df_old_usage.loc[Serial_number]
    except Exception:
        # if no data is found next serial number
        return False

    # check if df is empty
    if df_snr.empty or old_usage_snr.empty:
        return False

    # calculate average use and reduction procentile
    average_use = tool.average_use(
        df_snr, average_dates, df_results.loc[Serial_number, "Gasmeter_type"]
    )

    values = tool.gas_reduction(df_snr, df_knmi, comp_dates, average_use, old_usage_snr)

    # check if gas reduction is calculated
    if not values:
        return False
    # unpacks data from values
    gas_red = values[0]
    old_usage = values[1]
    new_usage = values[2]

    # making gas reduction a percentage
    for j in range(len(gas_red)):
        gas_red[j] = (1 - gas_red[j]) * 100

        # cant have a negative gas reduciton.
        if gas_red[j] < 0:
            gas_red[j] = 0

    # add results to dataframe
    df_results["Av_gas_reduction"][i] = gas_red[0]
    df_results["Min_gas_reduction"][i] = gas_red[2]
    df_results["Max_gas_reduction"][i] = gas_red[1]
    df_results["Av_old_usage"][i] = old_usage[0]
    df_results["Min_old_usage"][i] = old_usage[1]
    df_results["Max_old_usage"][i] = old_usage[2]
    df_results["Av_new_usage"][i] = new_usage[0]
    df_results["Min_new_usage"][i] = new_usage[1]
    df_results["Max_new_usage"][i] = new_usage[2]

    # get the first row  of data
    house_data = df_snr.iloc[0]

    # add aurum data to results
    df_results["House_type"][i] = house_data["House type"]
    df_results["Residents"][i] = house_data["Residents"]
    df_results["Energy_label"][i] = house_data["Energy label"]
    df_results["Solar_panels"][i] = house_data["Solar panels"]

    # adding survey data to results
    df_results["Construction_year"][i] = df_survey["Construction_year"][i]
    df_results["Residence_time_1year"][i] = df_survey["Residence_time_1year"][i]
    df_results["Influence_on_heating"][i] = df_survey["Influence_on_heating"][i]
    df_results["Change_number_of_residents"][i] = df_survey[
        "Change_number_of_residents"
    ][i]
    df_results["Change_in_resident_behaviour"][i] = df_survey[
        "Change_in_resident_behaviour"
    ][i]


# creating a results file
def results_file():
    # get current time

    # check if results directory exists
    if not os.path.isdir("./results"):
        os.mkdir("./results")

    # checks if a name is given
    if root.getvar(name="result_name"):
        results_path = "./results/{}.csv".format(root.getvar(name="result_name"))
    else:
        now = str(pd.to_datetime("today"))
        timestamp = now.split(":")[:-1]
        timestamp = "-".join(timestamp)
        timestamp = timestamp.replace(" ", "_")
        results_path = "./results/result {}.csv".format(timestamp)

    # removing None from database
    df_results.dropna(inplace=True)

    # create adn write new csv file
    df_results.to_csv(results_path)

    # returning path
    return results_path


# creating all dataframes
def initialise_df():
    global df_aurum, df_old_usage, df_knmi, df_results, df_survey

    try:
        get_knmi_data.get_data()
    except Exception as e:
        raise TimeoutError(e)

    # initializing the knmi dataframe
    df_knmi = pd.read_csv(
        "./data/knmi_data.csv", parse_dates=["Date"], index_col="Date"
    )

    # opening and creating aurum data frame
    try:
        # creating list with temp aurum dataframes
        aurum_ls = []
        for item in root.getvar(name="aurum"):
            # add dataframe to list
            aurum_ls.append(
                pd.read_csv(
                    item,
                    sep=";",
                    low_memory=False,
                )
            )
        # crating list of columns from first dataframe in aurum_ls
        first_col_ls = aurum_ls[0].columns.tolist()
        # checking if all data frames have simular columns
        for i in aurum_ls:
            i_ls = i.columns.tolist()
            if "Measurement source type" not in i_ls:
                raise ValueError("aurum")
            if first_col_ls != i_ls:
                raise ValueError("aurum")

        # initializing aurum dataframe and removing temp dataframes
        df_aurum = pd.concat(aurum_ls)
        del aurum_ls
    except:
        raise ValueError("aurum")

    # initializing the results dataframe
    try:
        df_results = pd.read_excel(root.getvar(name="pioneering"))

        if "Datum inregelen" not in df_results.columns.tolist():
            raise ValueError("pioneering")
    except:
        raise ValueError("pioneering")

    # initializing the survey datafram
    try:
        df_survey = pd.read_excel(
            root.getvar(name="survey"),
            sheet_name="Bron data",
            header=1,
        )
    except:
        raise ValueError("survey")

    # creating dataframe of old usage
    df_old_usage = df_survey.copy()
    df_old_usage.rename(
        columns={
            "Serialnummer": "Serial_number",
            "Gasverbruik- jaarlijks": "Yearly_gas_usage",
        },
        inplace=True,
    )

    # create list of columns
    old_usage_col = []

    # adding serial number and yearly gas usage to list
    old_usage_col.append("Serial_number")
    old_usage_col.append("Yearly_gas_usage")

    # go through each column
    for column in df_old_usage.columns.to_list():
        # split the column
        parts = column.split("-")

        # checks if columns is gas usage
        if parts[0] == "aardgasverbruik (in m3) ":
            # chagnes name of column
            colname = parts[1].strip()
            colname = format_month(colname)
            # checks if format is succesfull
            if not colname:
                continue

            # rename column
            df_old_usage.rename(columns={column: colname}, inplace=True)
            # add column to column list
            old_usage_col.append(colname)

    # filters the dataframe for columns in column list
    df_old_usage = df_old_usage[old_usage_col]
    # set index
    df_old_usage.set_index("Serial_number", inplace=True)
    # replaces =0 with nan
    df_old_usage.replace(0, float("nan"), inplace=True)
    # removes row if all nan
    df_old_usage.dropna(how="all", inplace=True)

    # filtering df survey
    df_survey = df_survey[
        [
            "Serialnummer",
            "Bouwjaar",
            "Woning duur",
            "Invloed op verwarming",
            "Verandering van de grotte van huishouden",
            "Verandering in bewoningsgedrag",
        ]
    ]

    df_survey.rename(
        columns={
            "Serialnummer": "Serial_number",
            "Bouwjaar": "Construction_year",
            "Woning duur": "Residence_time_1year",
            "Invloed op verwarming": "Influence_on_heating",
            "Verandering van de grotte van huishouden": "Change_number_of_residents",
            "Verandering in bewoningsgedrag": "Change_in_resident_behaviour",
        },
        inplace=True,
    )

    # Serial_number as index
    df_survey.set_index("Serial_number", inplace=True)

    # Replace Ja/Nee with True/False
    df_survey.replace(
        (
            "Ja",
            "Nee",
            "Langer dan één jaar",
            "Korter dan één jaar",
        ),
        (True, False, True, False),
        inplace=True,
    )

    # replacing Na with false (assumption)
    df_survey.fillna(False, inplace=True)

    # renaming some columns results
    df_results.rename(
        columns={
            df_results.columns[0]: "Postal_code",
            df_results.columns[1]: "Serial_number",
            df_results.columns[2]: "District_heating",
            df_results.columns[3]: "Underfloor_heating",
            df_results.columns[4]: "Gasmeter_type",
        },
        inplace=True,
    )

    # remove unnecessary columns
    df_results = df_results[
        [
            "Postal_code",
            "Serial_number",
            "District_heating",
            "Underfloor_heating",
            "Gasmeter_type",
        ]
    ]

    # format  postal ocde data
    df_results["Postal_code"] = df_results["Postal_code"].str.replace(" ", "")
    df_results["Postal_code"] = df_results["Postal_code"].str.upper()

    # formatting ja nee to true false
    df_results["District_heating"] = df_results["District_heating"].str.replace(
        "Ja", "True"
    )

    df_results["District_heating"] = df_results["District_heating"].str.replace(
        "Nee", "False"
    )

    # formatting partial cases to partial
    df_results["Underfloor_heating"] = df_results["Underfloor_heating"].str.replace(
        "Ja, alleen in badkamer, keuken of andere kleine ruimte", "Partial"
    )

    df_results["Underfloor_heating"] = df_results["Underfloor_heating"].str.replace(
        "Ja, alleen in de badkamer, keuken of andere kleine ruimte", "Partial"
    )

    # formatting ja nee to true false
    df_results["Underfloor_heating"] = df_results["Underfloor_heating"].str.replace(
        "Ja", "True"
    )
    df_results["Underfloor_heating"] = df_results["Underfloor_heating"].str.replace(
        "Nee", "False"
    )

    # formatting slimme meter to smart meter
    df_results["Gasmeter_type"] = df_results["Gasmeter_type"].str.replace(
        "Slimme meter", "Smart meter"
    )

    # formatting integers to mechanical gas meter in gasmeter_type column
    df_results.loc[
        df_results["Gasmeter_type"] != "Smart meter", "Gasmeter_type"
    ] = "Mechanical meter"

    # adding empty columms
    df_results[
        [
            "House_type",
            "Residents",
            "Energy_label",
            "Solar_panels",
            "Construction_year",
            "Residence_time_1year",
            "Influence_on_heating",
            "Change_number_of_residents",
            "Change_in_resident_behaviour",
            "Av_old_usage",
            "Min_old_usage",
            "Max_old_usage",
            "Av_new_usage",
            "Min_new_usage",
            "Max_new_usage",
            "Av_gas_reduction",
            "Min_gas_reduction",
            "Max_gas_reduction",
        ]
    ] = None

    # setting index collumn
    df_results.set_index("Serial_number", inplace=True)


# removes all childeren in root
def clear_root():
    for childeren in root.winfo_children():
        childeren.pack_forget()


# creating frame for selecting old results
def select_analysis(listbox_results, btn_open_analysis, btn_back):
    # clears root
    clear_root()

    # changing geometry
    root.geometry("360x300")

    # placing labels and buttons
    ttk.Label(
        root, padding=2, text="Select the results file", font=("Sans", "10", "bold")
    ).pack(fill=tk.BOTH)
    listbox_results.pack(fill=tk.X, padx=2)
    btn_open_analysis.pack(fill=tk.X, padx=16, pady=8)
    btn_back.pack(fill=tk.X, padx=16)


# opening an old analysis
def open_results(listbox_results):
    selected = listbox_results.curselection()[0]
    selected = listbox_results.get(selected)
    selected = "./results/" + selected

    root.destroy()

    df = pd.read_csv(selected, index_col="Serial_number")
    results_gui.results_gui(df)


def start_analysis():
    # clearing root
    clear_root()

    # placing wait lable
    ttk.Label(
        root, padding=(0, 4, 0, 2), text="Analyzing data", font=("Sans", "10", "bold")
    ).pack()
    ttk.Label(root, padding=2, text="Please wait...").pack()
    root.geometry("360x100")

    # creating and placing progressbar
    progress = tk.DoubleVar(root, name="pb")
    pb = ttk.Progressbar(
        root,
        orient=tk.HORIZONTAL,
        variable=progress,
    )
    pb.pack(fill=tk.X)

    # updating root
    root.update()

    # creating dataframes and updating root
    root.setvar(name="pb", value=5)
    root.update()

    # get dict of average dates and update root
    average_dates = get_knmi_data.get_seq_weighted_dates(4, df_knmi)
    root.setvar(name="pb", value=7.5)
    root.update()

    # get dict of comp dates and update root
    comp_dates = get_knmi_data.compare_dates(5, 3, df_knmi)
    root.setvar(name="pb", value=10)
    root.update()

    # creating variable for progressbar
    j = 1

    # loop trough each serial number
    for i in df_results.index:
        analyze_house(i, average_dates, comp_dates)
        # updating progress bar
        root.setvar(name="pb", value=(10 + 90 / len(df_results.index) * j))
        root.update()
        j += 1

    # creating results file
    path = results_file()

    # deleting root and old dataframes
    root.destroy()

    # open fresh results
    df = pd.read_csv(path, index_col="Serial_number")
    # open gui to view results
    results_gui.results_gui(df)


# creating a new analysis
def create_analysis():
    # checks if all the input is given
    if (
        root.getvar(name="aurum")
        and root.getvar(name="survey")
        and root.getvar(name="pioneering")
    ):
        # initializing dataframes
        try:
            initialise_df()
        except Exception as e:
            messagebox.showerror(
                title="Invalid file",
                message='Please make sure the correct {} file is selected! \n For more info press "help".'.format(
                    e
                ),
            )
            return None

        # starting analysis
        start_analysis()
    else:
        messagebox.showwarning(
            title="Input warning",
            message="Not all required files are selected",
        )


# userinput file name
def select_file(name):
    selected_file = filedialog.askopenfilename(
        title="Select {} data".format(name),
        filetypes=[("excel", "*.xlsx")],
    )
    return selected_file


# get list of all files in listbox aurum
def aurum_files():
    current_files = root.getvar(name="aurum")
    value = []
    for i in range(len(root.getvar(name="aurum"))):
        value.append(current_files[i])
    return value


# selecting pioneering data
def pioneering_data(lbl_pioneering):
    pioneering_file = select_file("pioneering")
    root.setvar(name="pioneering", value=pioneering_file)
    lbl_pioneering["text"] = pioneering_file.split("/")[-1]


# selecting survey data
def survey_data(lbl_survey):
    survey_file = select_file("survey")
    root.setvar(name="survey", value=survey_file)
    lbl_survey["text"] = survey_file.split("/")[-1]


# selecting aurum data
def aurum_data(listbox_aurum):
    files = filedialog.askopenfilenames(
        title="Select aurum data",
        filetypes=[("csv", "*.csv")],
    )
    value = aurum_files()
    for aurum_file in files:
        if not aurum_file in value:
            listbox_aurum.insert("end", aurum_file.split("/")[-1])
            value.append(aurum_file)
        else:
            messagebox.showwarning(
                title="File warning",
                message='File: "{}" has already been selected. \nTry a different file!'.format(
                    aurum_file.split("/")[-1]
                ),
            )

    root.setvar(name="aurum", value=value)


# removing aurum data
def remove_aurum_data(listbox_aurum):
    value = aurum_files()
    selected = listbox_aurum.curselection()
    for index in selected[::-1]:
        listbox_aurum.delete(index)
        del value[index]

    root.setvar(name="aurum", value=value)


def radio_help(frame, help_var):

    # set variables
    width = 15

    # draw and place radio buttons
    ttk.Radiobutton(
        frame,
        variable=help_var,
        text="Aurum",
        value="./resources/help_csv/aurum.csv",
        width=width,
        command=df_to_tree,
    ).place(anchor="nw")

    ttk.Radiobutton(
        frame,
        variable=help_var,
        text="Pioneering",
        value="./resources/help_csv/pioneering.csv",
        width=width,
        command=df_to_tree,
    ).place(x=10 * width, anchor="nw")

    ttk.Radiobutton(
        frame,
        variable=help_var,
        text="Survey",
        value="./resources/help_csv/survey.csv",
        width=width,
        command=df_to_tree,
    ).place(x=20 * width, anchor="nw")


def df_to_tree():

    tree.delete(*tree.get_children())

    df_table = pd.read_csv(help_window.getvar(name="help"), sep=";")
    df_table.fillna("", inplace=True)
    # sets the columns of the df to columns of tv
    col_ls = df_table.columns.tolist()
    tree["column"] = col_ls
    # shows the headers
    tree["show"] = "headings"

    # adds set column name as header
    for column in tree["columns"]:
        tree.heading(column, text=column.replace("_", " "))

    # adds dataframe to treeview
    for i in df_table.index.to_list():
        # creates row for each index
        row = df_table.loc[i].tolist()
        # add row to treeview
        tree.insert("", "end", values=row)


def create_help_window():
    # check if viewdata is True
    if root.getvar(name="Help_Window") == 1:
        return None

    # set view_data var to true
    root.setvar(name="View_Data", value=True)

    # create new window
    global help_window
    help_window = tk.Toplevel(root)
    help_window.geometry("1000x500")
    help_window.title("Help")
    help_window.iconbitmap("./resources/help.ico")

    help_var_window = tk.StringVar(help_window, name="help")

    radio_frame = ttk.Frame(help_window, padding=2)
    table_frame = ttk.Frame(help_window, padding=4)

    radio_frame.place(
        relwidth=1,
        height=35,
    )
    table_frame.place(
        relwidth=1,
        relheight=1,
        height=-50,
        # width=-scrol_width_window,
        y=35,
        # height=-button_height,
    )

    # creating and placing treeview for df_results
    global tree
    tree = ttk.Treeview(table_frame)

    tree.place(relwidth=1, relheight=1, height=-15)

    # creating scrollbars for treeview
    treescrollx = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)

    # configuring treeview
    tree.configure(xscrollcommand=treescrollx.set)

    treescrollx.place(
        rely=1,
        y=-15,
        height=15,
        relwidth=1,
        width=-15,
    )

    # # adding data to treeview
    # load_df_window()

    radio_help(radio_frame, help_var_window)

    # draw_window_calc_chance(frame_get_chance)
    # # when delete window (cross top right) is pressed destroy window and set var to false
    # window.protocol("WM_DELETE_WINDOW", close_window)


def menu_bar():
    # add menu bar on top
    menubar = tk.Menu()

    # add file menu
    mb_file = tk.Menu(menubar, tearoff=False)

    # add exit button
    mb_file.add_command(label="Exit", command=root.destroy)

    # add file to menu bar
    menubar.add_cascade(label="File", menu=mb_file)

    # add view data
    menubar.add_cascade(label="Help", command=create_help_window)

    # creating boolean and setting value for view data
    tk.BooleanVar(root, name="Help_Window")
    root.setvar(name="Help_Window", value=False)

    # sets menubar
    root.config(menu=menubar)


# select parameters for new analysis
def parameters_analysis(
    lbl_pioneering, lbl_survey, listbox_aurum, btn_back, name_entry
):
    clear_root()

    root.geometry("360x615")

    add_remove = ttk.Frame(root)

    a = ttk.Style()
    a.configure("my1.TButton", font=("Sans", 14), foreground="#3daee9")

    btn_start_analysis = ttk.Button(
        root,
        command=create_analysis,
        text="START ANALYSIS",
        padding=8,
        style="my1.TButton",
    )

    btn_select_pioneering = ttk.Button(
        root,
        padding=6,
        text="Select pioneering data file",
        command=lambda: pioneering_data(lbl_pioneering),
    )

    btn_select_survey = ttk.Button(
        root,
        padding=6,
        text="Select survey data file",
        command=lambda: survey_data(lbl_survey),
    )

    btn_select_aurom = ttk.Button(
        add_remove,
        padding=6,
        text="Select aurum data file(s)",
        command=lambda: aurum_data(listbox_aurum),
    )

    btn_remove_aurom = ttk.Button(
        add_remove,
        text="Remove from list",
        command=lambda: remove_aurum_data(listbox_aurum),
        padding=6,
    )

    ttk.Label(
        root,
        padding=4,
        text="Enter name of the results file: (Optional, default = date)",
        font=("Sans", "10", "bold"),
    ).pack(fill=tk.BOTH)
    name_entry.pack(fill=tk.X, padx=16, pady=(4, 8))

    ttk.Label(root, padding=2, text="Pioneering:", font=("Sans", "10", "bold")).pack(
        fill=tk.BOTH
    )
    lbl_pioneering.pack(fill=tk.BOTH, padx=4)
    btn_select_pioneering.pack(fill=tk.BOTH, padx=16, pady=(4, 8))

    ttk.Label(root, padding=2, text="Survey:", font=("Sans", "10", "bold")).pack(
        fill=tk.BOTH
    )
    lbl_survey.pack(fill=tk.BOTH, padx=4)
    btn_select_survey.pack(fill=tk.BOTH, padx=16, pady=(4, 8))

    ttk.Label(root, padding=2, text="Aurum:", font=("Sans", "10", "bold")).pack(
        fill=tk.BOTH
    )
    listbox_aurum.pack(fill=tk.BOTH, padx=4, pady=2)

    btn_select_aurom.pack(expand=True, fill=tk.BOTH, side=tk.LEFT, padx=(16, 8), pady=4)
    btn_remove_aurom.pack(
        expand=True, fill=tk.BOTH, side=tk.RIGHT, padx=(8, 16), pady=4
    )
    add_remove.pack(fill=tk.BOTH)

    btn_start_analysis.pack(fill=tk.X, padx=16, pady=(12, 8))

    btn_back.pack(fill=tk.BOTH, padx=16)


# go back to start
def back(btn_new_analysys, btn_select_analysis):
    clear_root()
    root.geometry("360x120")
    btn_new_analysys.pack(fill=tk.X, pady=(16, 8), padx=16)
    btn_select_analysis.pack(fill=tk.X, pady=(8, 16), padx=16)


def main():

    # setup the gui
    global root
    root = ThemedTk()
    root.get_themes()
    root.set_theme("breeze")
    root.geometry("360x135")
    root.title("Balancing Radiators Analysis")
    root.iconbitmap("./resources/tool_logo.ico")

    # add menu bar
    menu_bar()

    listbox_results = tk.Listbox(root)

    results_list = os.listdir("./results")

    a = ttk.Style()
    a.configure("my1.TButton", font=("Sans", 14), foreground="#3daee9")

    for result in results_list:
        listbox_results.insert("end", result)

    listbox_results.selection_set("end")

    tk.StringVar(root, name="pioneering")
    root.setvar(name="pioneering", value="")

    tk.StringVar(root, name="survey")
    root.setvar(name="survey", value="")

    tk.StringVar(root, name="aurum")
    root.setvar(name="aurum", value=[])

    var_result_name = tk.StringVar(root, name="result_name")
    root.setvar(name="result_name", value="")

    name_entry = ttk.Entry(root, textvariable=var_result_name)

    lbl_pioneering = ttk.Label(root, wraplength=300)
    lbl_survey = ttk.Label(root, wraplength=300)

    listbox_aurum = tk.Listbox(root, selectmode="multiple")

    btn_open_analysis = ttk.Button(
        root,
        text="Open analysis",
        command=lambda: open_results(listbox_results),
        style="my1.TButton",
        padding=6,
    )

    btn_back = ttk.Button(
        root,
        text="Back",
        command=lambda: back(btn_new_analysys, btn_select_analysis),
        padding=6,
    )

    btn_new_analysys = ttk.Button(
        root,
        text="Start new analysis",
        command=lambda: parameters_analysis(
            lbl_pioneering, lbl_survey, listbox_aurum, btn_back, name_entry
        ),
        padding=6,
    )

    btn_select_analysis = ttk.Button(
        root,
        text="Open previous analysis",
        command=lambda: select_analysis(listbox_results, btn_open_analysis, btn_back),
        padding=6,
    )

    btn_new_analysys.pack(fill=tk.X, pady=(16, 8), padx=16)
    btn_select_analysis.pack(fill=tk.X, pady=(8, 16), padx=16)

    root.mainloop()


# run main program if the file is executed
if __name__ == "__main__":
    main()
