import PySimpleGUI as sg
import os.path

# layout = [[sg.Text("This is the analysis")], [sg.Button("Nice")]]

# window = sg.Window("Analysis", layout)


# while True:
#     event, values = window.read()
#     # end programm if use closes window or presses nice
#     if event == "Nice" or event == sg.WIN_CLOSED:
#         break


# First the window layout in 2 columns

# file_list_column = [
#     [
#         sg.Text("Image Folder"),
#         sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
#         sg.FolderBrowse(),
#     ],
#     [sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-FILE LIST-")],
# ]

# # For now will only show the name of the file that was chosen
# image_viewer_column = [
#     [sg.Text("Choose an image from list on left:")],
#     [sg.Text(size=(40, 1), key="-TOUT-")],
#     [sg.Image(key="-IMAGE-")],
# ]

# # ----- Full layout -----
# layout = [
#     [
#         sg.Column(file_list_column),
#         sg.VSeperator(),
#         sg.Column(image_viewer_column),
#     ]
# ]

# window = sg.Window("Image Viewer", layout)

# # Run the Event Loop
# while True:
#     event, values = window.read()
#     if event == "Exit" or event == sg.WIN_CLOSED:
#         break
#     # Folder name was filled in, make a list of files in the folder
#     if event == "-FOLDER-":
#         folder = values["-FOLDER-"]
#         try:
#             # Get list of files in folder
#             file_list = os.listdir(folder)
#         except:
#             file_list = []

#         fnames = [
#             f
#             for f in file_list
#             if os.path.isfile(os.path.join(folder, f))
#             and f.lower().endswith((".png", ".gif"))
#         ]
#         window["-FILE LIST-"].update(fnames)
#     elif event == "-FILE LIST-":  # A file was chosen from the listbox
#         try:
#             filename = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])
#             window["-TOUT-"].update(filename)
#             window["-IMAGE-"].update(filename=filename)

#         except:
#             pass

# window.close()


from tkinter import *

from tkinter import messagebox
from tkinter import ttk
import time


window = Tk()

window.title("Welcome to the analysis")
window.geometry("500x300")


def warning():

    messagebox.showwarning("Nice", "Dit werkt bijna!")


def clicked():

    messagebox.showinfo("Nice", "Dit werkt!")


def error():

    messagebox.showerror("Nice", "Dit werkt niet!")


btn1 = Button(window, text="Warning", command=warning)
btn2 = Button(window, text="Goed", command=clicked)
btn3 = Button(window, text="Error", command=error)

btn1.grid(column=0, row=0)
btn2.grid(column=1, row=0)
btn3.grid(column=2, row=0)


style = ttk.Style()

style.theme_use("default")

style.configure("black.Horizontal.TProgressbar", background="green")

MAX = 50
progress_var = DoubleVar()

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
