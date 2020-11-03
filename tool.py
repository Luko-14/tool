import os

import numpy as np
import pandas as pd

import get_knmi_data


def average_use(data_frame, serial_number):

    dates = get_knmi_data.get_seq_weighted_dates(4)

    filt = (
        (data_frame["Serialnumber"] == serial_number)
        & (data_frame["Measurement source type"] == "gas")
        & (data_frame["Measurement value"] != None)
    )

    df = data_frame[filt]

    df["Measurement time"] = df["Measurement time"].apply(lambda x: x.hour)
    df["Measurement time"] = df["Measurement time"].apply(
        lambda x: np.timedelta64(x, "h")
    )

    df["Date_time"] = df["Measurement date"] + df["Measurement time"]

    df = df.set_index(df["Date_time"])
    df = df.drop(
        columns=[
            "Postal code",
            "Measurement source type",
            "Measurement date",
            "Measurement time",
            "Unit",
            "Correction",
        ]
    )

    tot_usg = 0
    days = 0
    for key, ls in dates.items():
        for items in ls:
            tot_usg += df.loc[items[0] : items[1]]["Measurement value"].sum()
            days += key

    return tot_usg / days


def main():
    df = pd.read_excel(
        "./data/aurum_data.xls",
        sheet_name="Alle data Aurum+ Pioneering",
        parse_dates=["Measurement date"],
    )

    av = average_use(df, 1011240)
    print(av)


if __name__ == "__main__":
    main()