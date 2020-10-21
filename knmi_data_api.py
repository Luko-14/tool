import requests

# collecting and formating data from knmi
def get_data():
    # Request data from KNMI
    # Parameters: station and begin date
    url = "http://projects.knmi.nl/klimatologie/daggegevens/getdata_dag.cgi"
    station = 290
    from_date = "1-1-2018"  # in format d-m-y
    date = from_date.split("-")
    params = {
        "stns": station,
        "vars": "TG:FG",
        "byear": date[2],
        "bmonth": date[1],
        "bday": date[0],
    }

    resp = requests.post(url, data=params)
    # create / open new csv file
    with open("knmi_data.csv", "w") as data_file:
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


if __name__ == "__main__":
    get_data()
