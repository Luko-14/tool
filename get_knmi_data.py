import os
import pandas as pd
import requests
import numpy as np

# collecting and formating data from knmi
def get_data():
    # Request data from KNMI
    # Parameters: station and begin date
    url = "http://projects.knmi.nl/klimatologie/daggegevens/getdata_dag.cgi"
    station = 290
    from_date = "1-1-2014"  # in format d-m-y
    date = from_date.split("-")
    params = {
        "stns": station,
        "vars": "TG:FG",
        "byear": date[2],
        "bmonth": date[1],
        "bday": date[0],
    }

    try:
        resp = requests.post(url, data=params)
    except Exception as e:
        return e

    # check if data path exist
    if not os.path.isdir("./data"):
        os.mkdir("./data")

    # create / open new csv file
    with open("./data/knmi_data.csv", "w") as data_file:
        # write headers
        data_file.writelines("Station,Date,Temp_mean,Wind_mean,weight_degr_days")
        # split text in list of lines
        lines = resp.text.split("\r\n")
        # split each line in list of data
        for line in lines:
            # check if line contains data
            if line != "" and line[0] != "#":
                data = line.split(",")
                # delete white spaces from data
                for i in range(0, len(data)):
                    data[i] = data[i].split(" ")[-1]
                    # format date form yyyymmmdd to yyyy-mm-dd
                    if i == 1:
                        list_date = list(data[i])
                        datum = [
                            "".join(list_date[0:4]),
                            "".join(list_date[4:6]),
                            "".join(list_date[6:8]),
                        ]
                        month = int(datum[1])
                        data[i] = "-".join(datum)

                temp = int(data[2])

                # calculate weighted degree days
                if temp >= 155:
                    weight_degr_days = 0
                elif month == 3 or month == 10:
                    weight_degr_days = 180 - temp
                elif month >= 4 and month <= 9:
                    weight_degr_days = (180 - temp) * 0.8
                else:
                    weight_degr_days = (180 - temp) * 1.1

                # add weighted degree days to data
                data.append(str(round(weight_degr_days)))

                # write data to file
                data_file.writelines("\n")
                data_file.writelines(",".join(data))
    return 0


# searches similar dates
def df_filt_dates(df, date, RANGE, stop_date):
    date_temp = df.loc[date]["weight_degr_days"]

    if date_temp == 0:
        return []

    filt = (df["weight_degr_days"] <= (date_temp + RANGE)) & (
        df["weight_degr_days"] >= (date_temp - RANGE)
    )

    stop_date = stop_date - np.timedelta64(1, "D")

    sim_dates = df.loc[filt]
    sim_dates = sim_dates[:stop_date]
    # return list with comparable dates
    return sim_dates.index.values


# comparing dates
def compare_dates(RANGE, seq, df):

    # y-m-d first date of aurum data
    BEGIN_DATE = np.datetime64(pd.to_datetime("2020-8-1"))

    comp_date_seq = {}

    LAST_DATE = df.index[-1]

    date = BEGIN_DATE
    # search comparable dates for each date after begin_date
    # untill current date
    while True:
        longest_sequence = 0

        list_sim_dates = df_filt_dates(df, date, RANGE, BEGIN_DATE)

        for check_date in list_sim_dates:
            i = 0
            # checks if there are sequences of comparable temperature
            while True:
                i += 1

                # get data from next day
                new_date = date + np.timedelta64(i, "D")
                new_check_date = check_date + np.timedelta64(i, "D")

                # check if next date is not current date (KNMI data not present)
                if new_date > (pd.to_datetime("today") - np.timedelta64(1, "D")):
                    return comp_date_seq

                # get temperature of next dates
                new_temp = df.loc[new_date]["weight_degr_days"]
                new_check_temp = df.loc[new_check_date]["weight_degr_days"]

                # check if temperature is in range
                if not (
                    new_check_temp <= (new_temp + RANGE)
                    and new_check_temp >= (new_temp - RANGE)
                ):

                    set_date = new_date + np.timedelta64(1, "D")

                    # check if new weighted temp is not 0
                    while True:
                        i -= 1
                        new_date = date + np.timedelta64(i, "D")
                        new_temp = df.loc[new_date]["weight_degr_days"]
                        if new_temp != 0:
                            i += 1
                            break

                    # if new sequence is longest sequence, save date
                    if i > longest_sequence:
                        longest_sequence = i - 1
                        end_date = date + np.timedelta64(longest_sequence, "D")
                        sim_date = check_date
                        sim_end_date = sim_date + np.timedelta64(longest_sequence, "D")

                    break

        # add longest sequence to dict, if its longer than seq
        if (longest_sequence + 1) >= seq:
            if not (longest_sequence + 1) in comp_date_seq.keys():
                comp_date_seq[(longest_sequence + 1)] = [
                    ((date, end_date), (sim_date, sim_end_date))
                ]
            else:
                comp_date_seq[(longest_sequence + 1)].append(
                    ((date, end_date), (sim_date, sim_end_date))
                )

        # set date to new date
        if len(list_sim_dates) == 0:
            date = date + np.timedelta64(1, "D")
        else:
            date = set_date

        if date > LAST_DATE:
            break

    # returns the dict with sequences
    return comp_date_seq


# get dict of a sequence of non weighted dates
def get_seq_weighted_dates(seq, df):

    # y-m-d first date of aurum data
    BEGIN_DATE = np.datetime64(pd.to_datetime("2020-8-1"))

    comp_date_seq = {}

    filt = df["weight_degr_days"] == 0

    df1 = df.loc[filt]
    df1 = df1[BEGIN_DATE:]

    i = 0

    while True:
        longest_sequence = 0
        j = 1

        while True:
            if df1.index[i + j] > df1.index[-1]:
                break

            next_date = df1.index[i] + np.timedelta64(j, "D")
            check_date = df1.index[i + j]

            if next_date == check_date:
                j += 1
            else:
                if j > longest_sequence:
                    longest_sequence = j - 1
                    date = df1.index[i]
                    end_date = df1.index[i + longest_sequence]

                i += j
                break

        # add longest sequence to dict, if its longer than seq
        if (longest_sequence + 1) >= seq:
            if not (longest_sequence + 1) in comp_date_seq.keys():
                comp_date_seq[(longest_sequence + 1)] = [(date, end_date)]
            else:
                comp_date_seq[(longest_sequence + 1)].append((date, end_date))

        if df1.index[i] == df1.index[-1]:
            break

    return comp_date_seq


# for testing / debugging
def main():

    get_data()

    # open csv
    df = pd.read_csv("./data/knmi_data.csv", parse_dates=["Date"], index_col="Date")

    seq = compare_dates(5, 3, df)
    dates = get_seq_weighted_dates(4, df)
    print(dates)
    print(seq)
    return dates

    # x = 0
    # i = 1
    # while x < 250:
    #     x = 0
    #     dicto = compare_dates(i, 3)

    #     for h, j in dicto.items():
    #         x += h * len(j)

    #     print("bij een range van {} heb je {} verg dagen".format(i, x))

    #     i += 1

    # print(i)


# run main program if the file is executed
if __name__ == "__main__":
    main()