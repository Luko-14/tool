import pandas as pd 
from pandasgui import show

knmi = pd.read_csv("KNMI_DATA.csv")
gui = show(knmi, settings={'block': True})

data = gui.get_dataframes()
print(data.keys())
print(data['knmi'])
