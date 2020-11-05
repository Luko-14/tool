import numpy as np
import pandas as pd

import get_knmi_data

# filter dataframe for serial number gas and a valvue
def filter_df(data_frame, serial_number):

    filt = (
        (data_frame["Serialnumber"] == serial_number)
        & (data_frame["Measurement source type"] == "gas")
        & (data_frame["Measurement value"] != None)
    )

    df = data_frame[filt]

    # combining date and time
    df["Measurement time"] = df["Measurement time"].apply(
        lambda x: np.timedelta64(x.hour, "h")
    )

    df["Date_time"] = df["Measurement date"] + df["Measurement time"]

    # sort by date_time and drop unused colums
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
    return df


# calculate avarage usage
def average_use(df, dates):

    tot_usg = 0
    days = 0
    # sum all gas usage from comp dates
    for _, ls in dates.items():
        for items in ls:
            df1 = df.loc[items[0] : items[1]]["Measurement value"]
            if not df1.empty:
                tot_usg += df1.sum()
                days += df1.index.size

    # return the average usage per day
    if days != 0:
        return tot_usg / days
    else:
        return None  # no data from serial number


# calcualte the old usage
def calc_old_usage(df, old_seq, days):
    return 0


# calculates the gas usage for heating
def gas_reduction(df, dates, av_use):

    if av_use == None:
        return None

    av_ls = []

    for _, ls in dates.items():
        for items in ls:
            new_seq = items[0]
            old_seq = items[1]
            df1 = df.loc[new_seq[0] : new_seq[1]]["Measurement value"]
            if not df1.empty:
                days = df1.index.size
                new_usage = df1.sum() - days * av_use
                old_usage = (
                    calc_old_usage(df, old_seq, days)
                    + days * av_use / 0.3
                    - days * av_use
                )

                if new_usage > 0 and old_usage > 0:
                    av_ls.append(new_usage / old_usage)

    if av_ls:
        return sum(av_ls) / len(av_ls)
    else:
        return None


# for testing / debugging
def main():

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
    df_snr = filter_df(df_aurum, 1011240)

    av = average_use(df_snr, average_dates)
    gu = gas_reduction(df_snr, comp_dates, av)

    print(av)
    print(gu)


# run main program if the file is executed
if __name__ == "__main__":
    main()