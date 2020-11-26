import numpy as np
import pandas as pd

import get_knmi_data

from math import isnan

# filter dataframe for serial number gas and a valvue
def filter_df(data_frame, serial_number):

    df = data_frame.copy()

    filt = (
        (df["Serialnumber"] == serial_number)
        & (df["Measurement source type"] == "gas")
        & (df["Measurement value"] != None)
    )

    df = df[filt]

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
def calc_old_usage(df_knmi, seq_weighted_days, old_seq, df_old_usage, av_use):
    tot_old_usage = 0
    begin_old_seq = pd.to_datetime(old_seq[0])
    end_old_seq = pd.to_datetime(old_seq[1])

    # sequince is in same month
    if begin_old_seq.month == end_old_seq.month:
        # sets date to string (m-year)
        date = str(begin_old_seq.month) + "-" + str(begin_old_seq.year)
        # gets old usage for that month
        try:
            tot_old_usage += df_old_usage[date]
        except Exception:
            return False

    # sequince is in same year
    elif begin_old_seq.month < end_old_seq.month:
        # calculates amount of months in seq
        months = begin_old_seq.month - end_old_seq.month
        # get usage for each month
        for month in range(months):
            # add month to startmonth
            month = begin_old_seq.month + month
            # sets date to string (m-year)
            date = str(month) + "-" + str(begin_old_seq.year)
            # gets old usage for that month
            try:
                tot_old_usage += df_old_usage[date]
            except Exception:
                return False

    # sequince if different years
    elif begin_old_seq.month > end_old_seq.month:
        # calculates amount of months in seq
        months = end_old_seq.month - begin_old_seq.month
        # get usage for each month
        for month in range(months):
            # add month to startmonth
            month = begin_old_seq.month + month
            # creats year variable. if month > 12 adds one year
            year = begin_old_seq.year + month // 12
            # sets month to int between 1 and 12
            month = 1 + (month - 1) % 12
            # sets date to string (m-year)
            date = str(month) + "-" + str(year)
            # gets old usage for that month
            try:
                tot_old_usage += df_old_usage[date]
            except Exception:
                return False

    # checks if tot_old_usage is a not number
    if isnan(tot_old_usage):
        # sets total gas usage to yearly gas usage
        tot_old_usage = df_old_usage["Yearly_gas_usage"]
        # checks if tot_old_usage is a number
        if isnan(tot_old_usage):
            # no usable values in df_old_usage data frame
            return False
        # filters df_knmi to 2019
        df_knmi = df_knmi[str(2019) : str(2019)]
    else:
        # filters df_knmi to all months between begin and end old seq
        df_knmi = df_knmi[
            (str(begin_old_seq.month) + "-" + str(begin_old_seq.year)) : (
                str(end_old_seq.month) + "-" + str(end_old_seq.year)
            )
        ]

    # calculate sum of weighted degree days from new data frame
    tot_weighted_days = df_knmi["weight_degr_days"].sum()

    # calculate gas usage for heating
    tot_old_heating_usage = tot_old_usage - av_use * df_knmi.index.size

    # calculate sequence gas usage for heating
    seq_old_usage = tot_old_heating_usage / tot_weighted_days * seq_weighted_days

    # returns sequence usage
    return seq_old_usage


# calculates the gas usage for heating
def gas_reduction(df_snr, df_knmi, dates, av_use, old_usage_snr):

    # checks if there is data for average use
    if av_use == None:
        return None

    # crates list for average use
    av_ls = []

    total_days = 0
    total_old_usage = 0
    total_new_usage = 0

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
            sum_weighted = df_knmi[new_seq[0] : new_seq[1]]["weight_degr_days"].sum()

            # calculates the number of days
            days = df1.index.size / 24

            # calculates the gas use for heating
            new_usage = df1.sum() - days * av_use
            old_usage = calc_old_usage(
                df_knmi, sum_weighted, old_seq, old_usage_snr, av_use
            )

            # checks if old usage is calculated
            if not calc_old_usage:
                # next sequence
                continue

            # checks if gas use is positive
            if new_usage > 0 and old_usage > 0:
                # add gas reduction to list
                av_ls.append(new_usage / old_usage)
                total_days += days
                total_old_usage += old_usage
                total_new_usage += new_usage

    # checks if list is not empty
    if av_ls:
        # transforms total_days to int
        total_days = int(round(total_days))
        total_average = sum(av_ls) / len(av_ls)

        # returns values to main
        return (total_average, total_days, total_old_usage, total_new_usage)
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
    gu = gas_reduction(df_snr, df_knmi, comp_dates, av, av)

    print(av)
    print(gu)


# run main program if the file is executed
if __name__ == "__main__":
    main()