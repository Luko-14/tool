import pandas as pd
import tkinter as tk
from tkinter import messagebox


def gui(df_results):
    root = tk.Tk()

    root.title("Welcome to the analysis")

    canvas = tk.Canvas(root, height=500, width=1000)
    canvas.pack()

    class dropbutton:
        def __init__(self, name, items):
            self.name = name
            self.items = items

            self.mb = tk.Menubutton(canvas, text=self.name, relief=tk.RAISED)
            self.mb.menu = tk.Menu(self.mb, tearoff=0)
            self.mb["menu"] = self.mb.menu

            self.value_ls = {}
            self.all_none = tk.BooleanVar(root, name="all_none", value=True)

            self.mb.menu.add_checkbutton(
                label="All/None",
                variable=self.all_none,
                command=self.ceck_all_items,
            )

            for i in self.items:
                self.value_ls[i] = []
                self.value_ls[i].append(tk.BooleanVar(root, True, name=str(i)))
                self.value_ls[i].append(
                    self.mb.menu.add_checkbutton(label=i, variable=self.value_ls[i][0])
                )

        def ceck_all_items(self):
            if self.all_none.get():
                for i in self.value_ls:
                    root.setvar(name=str(i), value=True)
            else:
                for i in self.value_ls:
                    root.setvar(name=str(i), value=False)

    dropbuttons = []

    for column in df_results.columns:
        dropbuttons.append(dropbutton(column, df_results[column].unique()))

    for i in range(len(dropbuttons)):
        dropbuttons[i].mb.place(
            relx=0.1 * i + 0.05 * (i + 1),
            rely=0.1,
            anchor="c",
            relwidth=0.1,
            relheight=0.1,
        )

    root.mainloop()


def main():
    df = pd.read_csv("./results/result 2020-11-19_11-03.csv", index_col="Serial_number")
    gui(df)


if __name__ == "__main__":
    main()


# def lbl1():


# def lbl2():


# btn1 = tk.Button(canvas, text="True", command=lbl1)
# btn1.place(relx=0, rely=0)
# btn2 = tk.Button(canvas, text="False", command=lbl2)
# btn2.place(relx=0, rely=0.1)
