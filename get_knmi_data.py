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

    resp = requests.post(url, data=params)

    # check if data path exist
    if not os.path.isdir("./data"):
        os.mkdir("./data")

    # create / open new csv file
    with open("./data/knmi_data.csv", "w") as data_file:
        # write headers
        data_file.writelines("Station,Date,Temp_mean,Wind_mean")
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
                        data[i] = "-".join(datum)

                # write data to file
                data_file.writelines("\n")
                data_file.writelines(",".join(data))
    return 0


# searches similar dates
def df_filt_dates(df, date, RANGE, stop_date):
    date_temp = df.loc[date]["Temp_mean"]

    filt = (df["Temp_mean"] <= (date_temp + RANGE)) & (
        df["Temp_mean"] >= (date_temp - RANGE)
    )

    stop_date = stop_date - np.timedelta64(1, "D")

    sim_dates = df.loc[filt]
    sim_dates = sim_dates[:stop_date]
    return sim_dates.index.values


# comparing dates
def compare_dates():
    get_data()

    # y-m-d
    BEGIN_DATE = pd.to_datetime("2020-8-1")

    comp_date_seq = {}

    df = pd.read_csv("./data/knmi_data.csv", parse_dates=["Date"], index_col="Date")

    LAST_DATE = df.index[-1]

    RANGE = 10

    date = BEGIN_DATE

    while True:
        longest_sequence = 0

        list_sim_dates = df_filt_dates(df, date, RANGE, BEGIN_DATE)

        for check_date in list_sim_dates:
            i = 0
            while True:
                i += 1

                new_date = date + np.timedelta64(i, "D")
                new_check_date = check_date + np.timedelta64(i, "D")

                if new_date > (pd.to_datetime("today") - np.timedelta64(1, "D")):
                    break

                new_temp = df.loc[new_date]["Temp_mean"]
                new_check_temp = df.loc[new_check_date]["Temp_mean"]

                if not (
                    new_check_temp <= (new_temp + RANGE)
                    and new_check_temp >= (new_temp - RANGE)
                ):
                    if i > longest_sequence:
                        longest_sequence = i - 1
                        sim_date = check_date
                        sim_end_date = sim_date + np.timedelta64(longest_sequence, "D")
                        end_date = date + np.timedelta64(longest_sequence, "D")

                    break

        if longest_sequence >= 3:
            if not longest_sequence in comp_date_seq.keys():
                comp_date_seq[longest_sequence] = [
                    ((date, end_date), (sim_date, sim_end_date))
                ]
            else:
                comp_date_seq[longest_sequence].append(
                    ((date, end_date), (sim_date, sim_end_date))
                )

        date = end_date + np.timedelta64(2, "D")

        if len(list_sim_dates) == 0:
            date = date + np.timedelta64(1, "D")

        if date > LAST_DATE:
            break

    return comp_date_seq


if __name__ == "__main__":
    outp = compare_dates()
    print(outp)
