import os

import pandas as pd

import get_knmi_data
import tool

"""
TO DO:
rewrite tool.calc_old_usage ()
create gui & visualise data
errors and foolproofing
"""

# creating a new analysis
def run_analysis():

    knmi = get_knmi_data.get_data()

    if knmi != 0:
        # problemen met verbinding knmi
        pass

    # creating list of every item in aurum data
    aurum_csv_list = os.listdir("./aurum data")

    # creating list with temp aurum dataframes
    aurum_ls = []

    for item in aurum_csv_list:
        # add dataframe to list
        aurum_ls.append(
            pd.read_csv(
                ("./aurum data/" + item),
                sep=";",
                low_memory=False,
            )
        )

    # initializing aurum dataframe and removing temp dataframes
    df_aurum = pd.concat(aurum_ls)
    del aurum_ls, aurum_csv_list

    # initializing the knmi dataframe
    df_knmi = pd.read_csv(
        "./data/knmi_data.csv", parse_dates=["Date"], index_col="Date"
    )

    # initializing the results dataframe
    df_results = pd.read_excel(
        "./data/Gegevens onderzoek t.b.v. Saxion- Pioneering.xlsx"
    )

    df_survey = pd.read_excel(
        "./data/Enquéte resultaat 1ste deel- Radiator WaterBalans - Oktober 2020_November 9, 2020_09.12.xlsx",
        sheet_name="Bron data",
        header=1,
    )

    df_survey = df_survey[
        [
            "Serialnummer",
            "Bouwjaar",
            "Woning duur",
            "Invloed op verwarming",
            "Verandering van de grotte van huishouden",
            "Verandering in bewoningsgedrag",
        ]
    ]

    df_survey.rename(
        columns={
            "Serialnummer": "Serial_number",
            "Bouwjaar": "Construction_year",
            "Woning duur": "Residence_time_1year",
            "Invloed op verwarming": "Influence_on_heating",
            "Verandering van de grotte van huishouden": "Change_number_of_residents",
            "Verandering in bewoningsgedrag": "Change_in_resident_behaviour",
        },
        inplace=True,
    )

    # Serial_number as index
    df_survey.set_index("Serial_number", inplace=True)

    # Replace Ja/Nee with True/False
    df_survey.replace(
        ("Ja", "Nee", "Langer dan één jaar", "Korter dan één jaar"),
        (True, False, True, False),
        inplace=True,
    )

    # renaming some columns results
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
            "Days",
            "Old_usage",
            "New_usage",
        ]
    ] = [None, None, None, None, None, None, None, None, None]

    # setting index collumn
    df_results.set_index("Serial_number", inplace=True)
    # get dict of dates to check
    average_dates = get_knmi_data.get_seq_weighted_dates(4, df_knmi)
    comp_dates = get_knmi_data.compare_dates(5, 3, df_knmi)

    # loop trough each serial number
    for i in df_results.index:

        Serial_number = i

        # filter df for serial number
        df_snr = tool.filter_df(df_aurum, Serial_number)

        # check if df is empty
        if df_snr.empty:
            continue

        # calculate average use and reduction procentile
        average_use = tool.average_use(df_snr, average_dates)
        values = tool.gas_reduction(df_snr, df_knmi, comp_dates, average_use)

        # check if gas reduction is calculated
        if not values:
            continue
        # unpacks data from values
        gas_red = values[0]
        days = values[1]
        old_usage = values[2]
        new_usage = values[3]

        # making gas reduction a percentage
        gas_red = (1 - gas_red) * 100

        # add results to dataframe
        df_results["Average_Use"][i] = average_use
        df_results["Gas_Reduction"][i] = gas_red
        df_results["Days"][i] = days
        df_results["Old_usage"][i] = old_usage
        df_results["New_usage"][i] = new_usage

        # get the first row  of data
        house_data = df_snr.iloc[0]

        # add aurum data to results
        df_results["House_Type"][i] = house_data["House type"]
        df_results["Residents"][i] = house_data["Residents"]
        df_results["Energy_Label"][i] = house_data["Energy label"]
        df_results["Solar_Panels"][i] = house_data["Solar panels"]

    # get current time
    now = str(pd.to_datetime("today"))
    timestamp = now.split(":")[:-1]
    timestamp = "-".join(timestamp)
    timestamp = timestamp.replace(" ", "_")

    # check if results directory exists
    if not os.path.isdir("./results"):
        os.mkdir("./results")

    results_path = "./results/result {}.csv".format(timestamp)

    df_results = pd.concat([df_results, df_survey], axis=1)

    # removing None from database
    df_results.dropna(inplace=True)

    # create adn write new csv file
    df_results.to_csv(results_path)

    return 0


# run main program if the file is executed
if __name__ == "__main__":
    results = run_analysis()
    print(results)
