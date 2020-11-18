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

    # changing datatype from string to time
    df["Measurement time"] = df["Measurement time"].apply(
        lambda x: np.timedelta64(x.split(":")[0], "h")
    )

    df["Measurement date"] = pd.to_datetime(df["Measurement date"], format="%d-%m-%Y")

    # creating new collumn with date and time combined
    df["Date_time"] = df["Measurement date"] + df["Measurement time"]

    # change datatype of measurement valvue to float
    df["Measurement value"] = df["Measurement value"].str.replace(",", ".")
    df["Measurement value"] = df["Measurement value"].astype(float)

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

    tot_usg = 0.0
    days = 0.0
    # sum all gas usage from comp dates
    for _, ls in dates.items():
        for items in ls:
            df1 = df.loc[items[0] : items[1]]["Measurement value"]
            if not df1.empty:
                tot_usg += df1.sum()
                days += df1.index.size / 24

    # return the average usage per day
    if days != 0:
        return tot_usg / days
    else:
        return None  # no data from serial number


# calcualte the old usage
def calc_old_usage(df_knmi, sum_weighted, old_seq):
    return 0


# calculates the gas usage for heating
def gas_reduction(df_snr, df_knmi, dates, av_use):

    # checks if there is data for average use
    if av_use == None:
        return None

    # crates list for average use
    av_ls = []

    # go through each item in dict compare dates (from get_knmi_data)
    for _, ls in dates.items():
        for items in ls:
            # breaks tuple down in new and old sequence
            new_seq = items[0]
            old_seq = items[1]

            # creates dataframe for gas consumption for days in new_seq
            df1 = df_snr.loc[new_seq[0] : new_seq[1]]["Measurement value"]

            # checks if dataframe is not empty
            if df1.empty:
                continue

            # calculates sum of weighted degree days
            sum_weighted = df_knmi.loc[new_seq[0] : new_seq[1]][
                "weight_degr_days"
            ].sum()

            # calculates the number of days
            days = df1.index.size / 24

            # calculates the gas use for heating
            new_usage = df1.sum() - days * av_use
            old_usage = calc_old_usage(df_knmi, sum_weighted, old_seq) - days * av_use

            # checks if gas use is positive
            if new_usage > 0 and old_usage > 0:
                # add gas reduction to list
                av_ls.append(new_usage / old_usage)

    # checks if list is not empty
    if av_ls:
        # returns average gas reduction
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
    gu = gas_reduction(df_snr, df_knmi, comp_dates, av)

    print(av)
    print(gu)


# run main program if the file is executed
if __name__ == "__main__":
    main()