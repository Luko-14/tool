import numpy as np
import pandas as pd

import get_knmi_data

from math import isnan

# creating global variables for errors
global flow_dev_min
# maximum negative deviation of flow meter
flow_dev_min = (100 - 0.17) / 100
global flow_dev_max
# maximum positive deviation of flow meter
flow_dev_max = (100 + 0.92) / 100
global knmi_deviation
# deviation of the knmi measuring equipemnt
knmi_deviation = 1

# filter dataframe for serial number gas and a valvue
def filter_df(data_frame, serial_number):

    # make deep copy of df aurum
    df = data_frame.copy()

    # create filter
    filt = (
        (df["Serialnumber"] == serial_number)
        & (df["Measurement source type"] == "gas")
        & (df["Measurement value"] != None)
    )

    # apply filter
    df = df[filt]

    # changing datatype from string to time
    df["Measurement time"] = df["Measurement time"].apply(
        lambda x: np.timedelta64(x.split(":")[0], "h")
    )

    df["Measurement date"] = pd.to_datetime(df["Measurement date"], format="%d-%m-%Y")

    # creating new collumn with date and time combined
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
def average_use(df, dates, gasmeter_type):

    # creating variables
    tot_usg = 0.0
    days = 0.0

    # sum all gas usage from comp dates
    for _, ls in dates.items():
        for items in ls:
            df1 = df.loc[items[0] : items[1]]["Measurement value"]
            if not df1.empty:
                tot_usg += df1.sum()
                days += df1.index.size / 24

    if days != 0:
        av_use = tot_usg / days
        if gasmeter_type == "Mechanical meter":
            aurum_err = 0.95
        else:
            aurum_err = 1

        av_use_min = av_use * aurum_err * flow_dev_min
        av_use_max = av_use / aurum_err * flow_dev_max
        # return the average usage per day
        return (av_use, av_use_min, av_use_max, aurum_err)
    else:
        return None  # no data from serial number


# calcualte the old usage
def calc_old_usage(df_knmi, seq_weighted_days, old_seq, df_old_usage, av_use):
    # creating and setting variables
    tot_old_usage = 0
    begin_old_seq = pd.to_datetime(old_seq[0])
    end_old_seq = pd.to_datetime(old_seq[1])

    # sequince is in same month
    if begin_old_seq.month == end_old_seq.month:
        # sets date to string (m-year)
        date = str(begin_old_seq.month) + "-" + str(begin_old_seq.year)
        # gets old usage for that month
        try:
            tot_old_usage += float(df_old_usage[date])
        except Exception:
            pass

    # sequince is in same year
    elif begin_old_seq.month < end_old_seq.month:
        # calculates amount of months in seq
        months = end_old_seq.month - begin_old_seq.month + 1
        # get usage for each month
        for month in range(months):
            # add month to startmonth
            month = begin_old_seq.month + month
            # sets date to string (m-year)
            date = str(month) + "-" + str(begin_old_seq.year)
            # gets old usage for that month
            try:
                tot_old_usage += float(df_old_usage[date])
            except:
                tot_old_usage = 0
                continue

    # sequence is in different years
    elif begin_old_seq.month > end_old_seq.month:
        # calculates amount of months in seq
        months = 13 - begin_old_seq.month + end_old_seq.month
        # get usage for each month
        for month in range(months):
            # add month to startmonth
            month = begin_old_seq.month + month
            # creats year variable. if month > 12 adds one year
            year = begin_old_seq.year + (month - 1) // 12
            # sets month to int between 1 and 12
            month = 1 + (month - 1) % 12
            # sets date to string (m-year)
            date = str(month) + "-" + str(year)
            # gets old usage for that month
            try:
                tot_old_usage += float(df_old_usage[date])
            except:
                tot_old_usage = 0
                continue

    # checks if tot_old_usage is a not number
    if tot_old_usage == 0:
        # sets total gas usage to yearly gas usage
        tot_old_usage = df_old_usage["Yearly_gas_usage"]
        # checks if tot_old_usage is not a number
        try:
            tot_old_usage = float(tot_old_usage)
        except:
            return False

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

    # calculates the error of tot_weighted_days
    er_tot_weighted_days = df_knmi.index.size * knmi_deviation

    # calculate gas usage for heating
    tot_old_heating_usage = tot_old_usage - av_use[0] * df_knmi.index.size
    tot_old_heating_usage_min = tot_old_usage - av_use[2] * df_knmi.index.size
    tot_old_heating_usage_max = tot_old_usage - av_use[1] * df_knmi.index.size

    # calculate sequence gas usage for heating
    seq_old_usage = tot_old_heating_usage / tot_weighted_days * seq_weighted_days[0]

    seq_old_usage_min = (
        tot_old_heating_usage_min
        / (tot_weighted_days + er_tot_weighted_days)
        * seq_weighted_days[1]
    )

    seq_old_usage_max = (
        tot_old_heating_usage_max
        / (tot_weighted_days - er_tot_weighted_days)
        * seq_weighted_days[2]
    )

    # returns sequence usage
    return (seq_old_usage, seq_old_usage_min, seq_old_usage_max)


# calculates the gas usage for heating
def gas_reduction(df_snr, df_knmi, dates, av_use, old_usage_snr):
    # checks if there is data for average use
    if av_use == None:
        return None

    # retrieving aurum error
    aurum_err = av_use[3]

    # crates list for average, min and max use
    av_ls = []
    min_ls = []
    max_ls = []

    # creating variables for total usage
    # in format [average,min,max]
    total_days = [0, 0, 0]
    total_old_usage = [0, 0, 0]
    total_new_usage = [0, 0, 0]

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

            # creates list weighted degree days (av,min,max)
            sum_weighted = []

            sum_weighted.append(
                df_knmi[new_seq[0] : new_seq[1]]["weight_degr_days"].sum()
            )

            sum_weighted.append(
                df_knmi[new_seq[0] : new_seq[1]]["weight_degr_days"].sum()
                - df_knmi[new_seq[0] : new_seq[1]].index.size * knmi_deviation
            )

            sum_weighted.append(
                df_knmi[new_seq[0] : new_seq[1]]["weight_degr_days"].sum()
                + df_knmi[new_seq[0] : new_seq[1]].index.size * knmi_deviation
            )

            # calculates the number of days
            days = df1.index.size / 24

            # create list of new gas usage (av,min,max)
            new_usage = []
            # calculates average new gas use
            new_usage.append(df1.sum() - days * av_use[0])
            # calculates min new gas use ()
            new_usage.append(df1.sum() / flow_dev_max * aurum_err - days * av_use[2])
            # calculates max new gas use
            new_usage.append(df1.sum() / flow_dev_min / aurum_err - days * av_use[1])

            # calculating the old usage
            old_usage = calc_old_usage(
                df_knmi, sum_weighted, old_seq, old_usage_snr, av_use
            )

            # checks if old usage is calculated
            if not old_usage:
                # next sequence
                continue

            # checks if av gas use is positive
            if new_usage[0] > 0 and old_usage[0] > 0:
                # add av gas reduction to list and adds all values
                av_ls.append(new_usage[0] / old_usage[0])
                total_days[0] += days
                total_old_usage[0] += old_usage[0]
                total_new_usage[0] += new_usage[0]

            # checks if min gas use is positive
            if new_usage[1] > 0 and old_usage[2] > 0:
                # add min gas reduction to list and adds all values
                min_ls.append(new_usage[1] / old_usage[2])
                total_days[1] += days
                total_old_usage[2] += old_usage[2]
                total_new_usage[1] += new_usage[1]

            # checks max av gas use is positive
            if new_usage[2] > 0 and old_usage[1] > 0:
                # add max gas reduction to list and adds all values
                max_ls.append(new_usage[2] / old_usage[1])
                total_days[2] += days
                total_old_usage[1] += old_usage[1]
                total_new_usage[2] += new_usage[2]

    # checks if list is not empty
    if av_ls and min_ls and max_ls:
        # creating average list
        total_average = []
        # adding av min and max to total average
        total_average.append(sum(av_ls) / len(av_ls))
        total_average.append(sum(min_ls) / len(min_ls))
        total_average.append(sum(max_ls) / len(max_ls))

        # normalizing gas usage to years
        for i in range(3):
            total_old_usage[i] = total_old_usage[i] / total_days[i] * 365
            total_new_usage[i] = total_new_usage[i] / total_days[i] * 365

        # returns values to main
        return (total_average, total_old_usage, total_new_usage)
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

    av = average_use(df_snr, average_dates, "Mechanical meter")
    gu = gas_reduction(df_snr, df_knmi, comp_dates, av, av)

    print(av)
    print(gu)


# run main program if the file is executed
if __name__ == "__main__":
    main()