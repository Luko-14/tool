import os

import pandas as pd

import get_knmi_data
import tool

"""
TO DO:
ceck days in tool (average usage and gas reduction)
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

    # initializing the results dataframe
    df_results = pd.read_excel("./data/aurum_data.xls", sheet_name="Pioneering data")

    # renaming some collumns
    df_results.rename(
        columns={
            df_results.columns[0]: "Postal_Code",
            df_results.columns[1]: "Serial_number",
        },
        inplace=True,
    )

    # remove unnecessary columns
    df_results = df_results[["Postal_Code", "Serial_number"]]

    # format data
    df_results["Postal_Code"] = df_results["Postal_Code"].str.replace(" ", "")
    df_results["Postal_Code"] = df_results["Postal_Code"].str.upper()

    # adding empty columms
    df_results[
        [
            "House_Type",
            "Residents",
            "Energy_Label",
            "Solar_Panels",
            "Average_Use",
            "Gas_Reduction",
        ]
    ] = [None, None, None, None, None, None]

    # get dict of dates to check
    average_dates = get_knmi_data.get_seq_weighted_dates(4, df_knmi)
    comp_dates = get_knmi_data.compare_dates(5, 3, df_knmi)

    # loop trough each serial number
    for i in range(df_results.index.size):

        Serial_number = df_results["Serial_number"][i]
        # filter df for serial number
        df_snr = tool.filter_df(df_aurum, Serial_number)

        # check if df is empty
        if df_snr.empty:
            continue

        # calculate average use and reduction procentile
        average_use = tool.average_use(df_snr, average_dates)
        gas_red = tool.gas_reduction(df_snr, comp_dates, average_use)

        # check if gas reduction is calculated
        if gas_red:
            gas_red = (1 - gas_red) * 100
        else:
            continue

        # add results to dataframe
        df_results["Average_Use"][i] = average_use
        df_results["Gas_Reduction"][i] = gas_red

        house_data = df_snr.iloc[0]

        df_results["House_Type"][i] = house_data["House type"]
        df_results["Residents"][i] = house_data["Residents"]
        df_results["Energy_Label"][i] = house_data["Energy label"]
        df_results["Solar_Panels"][i] = house_data["Solar panels"]

    # removing None from database
    df_results.dropna(inplace=True)

    return df_results


# run main program if the file is executed
if __name__ == "__main__":
    results = run_analysis()
    print(results)
