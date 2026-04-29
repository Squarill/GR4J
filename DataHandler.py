from Paths import Paths
import json
import numpy as np
from pathlib import Path

## INPUTS-DATA PREPARATION
## BASIC NOTATION
## DATE = yyyy-mm-dd
## ANY VALUE = 0.000
def stripdata(p:str) -> list[list]:
    p = Path(p).with_suffix(".txt")
    if (Paths.DATASET/p).exists() == False:
        raise FileNotFoundError(f"{p} is not found.")
    DATES = []
    VALUES = []
    with open(Paths.DATASET / p, "r") as f:
        DATA = f.readlines()
        for data in DATA:
            spl = data.split()
            try:
                Q = float(spl[-1])
                date = spl[0][:10]
                check = float(date[:4]) #to check if the first 4 digit of date (year) is a number or not
                DATES.append(date)
                VALUES.append(Q)
            except:
                print(f"{p} WARNING:\tSkipped data line at: {data}")
                continue
    return [DATES, VALUES]

def clip_by_dates(dates,values,start_year, end_year):
    new_dates = []
    new_values = []
    for i in range(len(dates)):
        if int(dates[i][:4]) >= start_year and int(dates[i][:4]) <= end_year:
            new_dates.append(dates[i])
            new_values.append(values[i])
    return new_dates, new_values

def create_data(start_year = float("-inf"), end_year = float("inf"), file_name:str = "DATA_NUMPY", create_json:bool = False, **DATA_PATH_DICT):
    """
    Special data notation (must be used):
    Precipitation = "P"
    Potential Evapotranspiration = "PET"
    Discharge = "Q"

    Example:
    DATA_PATH_DICT = {
        "P": "pre_data.txt",
        "PET": "pet_data.txt",
        "Q": "q_data.txt"
    }
    create_data(**DATA_PATH_DICT)
    """
    file_name = Path(file_name).with_suffix(".npz")

    date_start = float("-inf")
    date_end = float("inf")

    DATAS = {}
    #To determine the start and end dates
    for data_type, data_name in DATA_PATH_DICT.items():
        dates, values = stripdata(data_name)

        data_date_start = int(dates[0][:4])
        data_date_end = int(dates[-1][:4])
        
        if start_year == float("-inf"):
            date_start = max(data_date_start, date_start)
        else:
            if data_date_start > start_year:
                raise ValueError(f"{data_type} data starting year ({data_date_start}) is greater than the given start year ({start_year}).")
            date_start = start_year
        if end_year == float("inf"):
            date_end = min(data_date_end, date_end)
        else:
            if data_date_end < end_year:
                raise ValueError(f"{data_type} data ending year ({data_date_end}) is less than the given end year ({end_year}).")
            date_end = end_year
    
        DATAS[data_type] = [dates, values]

    #To clip the data according to found date limits
    for data_type, values in DATAS.items():
        dates, values = values
        dates, values = clip_by_dates(dates, values, date_start, date_end)
        DATAS[data_type] = [dates, values]

    #Create the .npz file
    len_check = None
    numpified_data = {}
    for data_type, values in DATAS.items():
        dates, values = values

        if len_check == None:
            len_check = len(values)
        elif len_check != len(values):
            raise ValueError(f"{data_type} data length is NOT consistent.")
        
        numpified_data[data_type] = np.asarray(values)
        numpified_data["DATES"] = np.asarray(dates)
    
    np.savez(Paths.DATASET / file_name, **numpified_data)
    if create_json:
        json_data = {}
        for data_type, values in DATAS.items():
            dates, values = values
            json_data[data_type] = {}

            for i in range(len(values)):
                date = dates[i]
                value = values[i]
                json_data[data_type][date] = value
        
        with open(Paths.DATASET / file_name.with_suffix(".json"), "w") as f:

            json.dump(json_data, f, indent=4)



def special_case(start_year = float("-inf"), end_year = float("inf"), file_name:str = "SPECIAL_DATA.npz"):
    """
    DO NOT USE THIS FUNCTION, IT IS FOR DEBUGGING ONLY.
    """
    P_values = []
    PET_values = []
    TAVG_values = []
    Q_values = []
    Dates = []

    with open(Paths.DATASET / "vienne_eobs.txt", "r") as f:
        all_data = f.readlines()[1:]    #[date, discharge, p, pet, tavg]
        for line in all_data:
            temp_lst = line.split()
            if int(temp_lst[0][:4]) < start_year or int(temp_lst[0][:4]) > end_year:
                continue
            Dates.append(temp_lst[0])
            Q_values.append(temp_lst[1])
            P_values.append(temp_lst[2])
            PET_values.append(temp_lst[3])
            TAVG_values.append(temp_lst[4])

    p_vector = np.array(P_values)
    pet_vector = np.array(PET_values)
    tavg_vector = np.array(TAVG_values)
    q_obs_vector = np.array(Q_values)
    dates_vector = np.array(Dates)

    np.savez(
        Paths.DATASET / file_name,
        P = p_vector,
        PET = pet_vector,
        T = tavg_vector,
        Q = q_obs_vector,
        DATES = dates_vector
    )

if __name__ == "__main__":
    """
    create_data(**{"Q" : "q_data", "PET" : "pet_data", "P" : "pre_data"}, create_json=True, start_year=1970, end_year=2000, file_name="1970-2000-calibration")
    """
    
    pass