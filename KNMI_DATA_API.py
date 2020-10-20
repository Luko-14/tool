import requests


def get_data():
    # Request data from KNMI
    # Parameters: station and begin date
    url = "http://projects.knmi.nl/klimatologie/daggegevens/getdata_dag.cgi"
    station = 290
    from_date = "1-1-2015"  # in format d-m-y
    date = from_date.split("-")
    PARAMS = {
        "stns": station,
        "vars": "TG:FG",
        "byear": date[2],
        "bmonth": date[1],
        "bday": date[0],
    }

    resp = requests.post(url, data=PARAMS)
    # create / open new csv file
    with open("KNMI_DATA.csv", "w") as f:
        # write headers
        f.writelines("Station,Date,Temp_mean,Wind_mean")
        # split text in list of lines
        lines = resp.text.split("\r\n")
        # split each line in list of data
        for line in lines:
            # check if line contains data
            if line != "" and line[0] != "#":
                data = line.split(",")
                # delete white spaces from data
                for i in range(len(data)):
                    data[i] = data[i].split(" ")[-1]
                # write data to file
                f.writelines("\n")
                f.writelines(",".join(data))
    return 0


if __name__ == "__main__":
    get_data()
