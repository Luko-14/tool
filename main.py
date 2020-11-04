import os

import pandas as pd

import get_knmi_data
import tool

"""
TO DO:
go through each serial number:
export results to new csv (unique)
rewrite tool.calc_old_usage ()
create gui & visualise data

"""

# creating a new analysis
def run_analysis():

    get_knmi_data.get_data()

    # initializing the aurum dataframe
    df_aurum = pd.read_excel(
        "./data/aurum_data.xls",
        sheet_name="Alle data Aurum+ Pioneering",
        parse_dates=["Measurement date"],
    )

    # initializing the knmi dataframe
    df_knmi = pd.read_csv(
        "./data/knmi_data.csv", parse_dates=["Date"], index_col="Date"
    )

    # get dict of dates to check
    average_dates = get_knmi_data.get_seq_weighted_dates(4, df_knmi)
    comp_dates = get_knmi_data.compare_dates(5, 3, df_knmi)

    # filter df for serial nummer
    df_snr = tool.filter_df(df_aurum, 1011240)

    av = tool.average_use(df_snr, average_dates)
    gu = tool.gas_reduction(df_snr, comp_dates, av)

    print(av)
    print(gu)


# run main program if the file is executed
if __name__ == "__main__":
    run_analysis()
