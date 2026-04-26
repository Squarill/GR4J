from Paths import Paths
import json
import numpy as np

## INPUTS-DATA PREPARATION
## BASIC NOTATION
## DATE = yyyy-mm-dd
## ANY VALUE = 0.000
def stripdata(p:str) -> list[list]:
    DATES = []
    VALUES = []
    with open(Paths.DATASET / p, "r") as f:
        DATA = f.readlines()
        for data in DATA:
            spl = data.split()
            try:
                Q = float(spl[-1])
                date = spl[0]
                check = float(date[:4]) #to check if the first 4 digit of date (year) is a number or not
                DATES.append(date)
                VALUES.append(Q)
            except:
                continue
    return [DATES, VALUES]

def stripdataGRDC(p: str) -> list[list]:
    DATES = []
    VALUES = []
    with open(Paths.DATASET / p, "r") as f:
        DATA = f.readlines()[37::]
        for i in range(len(DATA)):
            DATA[i] = DATA[i].replace(" ","").replace("\n", "").replace(":","").replace(";", "")
            DATES.append(DATA[i][:10:1])
            VALUES.append(float(DATA[i][14:]))
    return [DATES, VALUES]

def clip_by_dates(dates,values,start_year, end_year):
    new_dates = []
    new_values = []
    for i in range(len(dates)):
        if int(dates[i][:4]) >= start_year and int(dates[i][:4]) <= end_year:
            new_dates.append(dates[i])
            new_values.append(values[i])
    return new_dates, new_values

def create_data_npz_only_nc(start_year = float("-inf"), end_year = float("inf"), file_name:str = "DATA_NUMPY.npz"):
    pre_dates, PVALUES = stripdata("pre_data.txt")
    pet_dates, PETVALUES = stripdata("pet_data.txt")
    tavg_dates, TAVGVALUES = stripdata("tavg_data.txt") 
    q_dates, QVALUES = stripdata("q_data.txt")


    if start_year == float("-inf") or end_year == float("inf"):
        start_year = max(int(pre_dates[0][:4]), int(pet_dates[0][:4]), int(tavg_dates[0][:4]), int(q_dates[0][:4]))
        end_year = min(int(pre_dates[-1][:4]), int(pet_dates[-1][:4]), int(tavg_dates[-1][:4]), int(q_dates[-1][:4]))

    #datecheck
    data_date_start = max(int(pre_dates[0][:4]), int(pet_dates[0][:4]), int(tavg_dates[0][:4]), int(q_dates[0][:4]))
    data_date_end = min(int(pre_dates[-1][:4]), int(pet_dates[-1][:4]), int(tavg_dates[-1][:4]), int(q_dates[-1][:4]))

    if data_date_start > start_year or data_date_end < end_year:
        print("Given data does not qualify the time limits.")
        print("Wanted time limits:")
        print(f"Start year:{start_year}, End year:{end_year}")
        print("Time limits of given data:")
        print(f"Start year:{data_date_start}, End year:{data_date_end}")
        return

    pre_dates, PVALUES = clip_by_dates(pre_dates, PVALUES, start_year, end_year)
    pet_dates, PETVALUES = clip_by_dates(pet_dates, PETVALUES, start_year, end_year)
    tavg_dates, TAVGVALUES = clip_by_dates(tavg_dates, TAVGVALUES, start_year, end_year)
    q_dates, QVALUES = clip_by_dates(q_dates, QVALUES, start_year, end_year)

    p_vector = np.array(PVALUES)
    pet_vector = np.array(PETVALUES)
    tavg_vector = np.array(TAVGVALUES)
    q_obs_vector = np.array(QVALUES)
    dates_vector = np.array(q_dates)

    np.savez(
        Paths.DATASET / file_name,
        P = p_vector,
        PET = pet_vector,
        T = tavg_vector,
        Q = q_obs_vector,
        DATES = dates_vector
    )

def create_data_json(start_year = float("-inf"), end_year = float("inf"), file_name:str = "DATA.json"):
    pre_dates, PVALUES = stripdata("pre_data.txt")
    pet_dates, PETVALUES = stripdata("pet_data.txt")
    tavg_dates, TAVGVALUES = stripdata("tavg_data.txt") 
    q_dates, QVALUES = stripdataGRDC("GRDC_Q_Day.txt")


    if start_year == float("-inf") or end_year == float("inf"):
        start_year = max(int(pre_dates[0][:4]), int(pet_dates[0][:4]), int(tavg_dates[0][:4]), int(q_dates[0][:4]))
        end_year = min(int(pre_dates[-1][:4]), int(pet_dates[-1][:4]), int(tavg_dates[-1][:4]), int(q_dates[-1][:4]))

    #datecheck
    data_date_start = max(int(pre_dates[0][:4]), int(pet_dates[0][:4]), int(tavg_dates[0][:4]), int(q_dates[0][:4]))
    data_date_end = min(int(pre_dates[-1][:4]), int(pet_dates[-1][:4]), int(tavg_dates[-1][:4]), int(q_dates[-1][:4]))

    if data_date_start > start_year or data_date_end < end_year:
        print("Given data does not qualify the time limits.")
        print("Wanted time limits:")
        print(f"Start year:{start_year}, End year:{end_year}")
        print("Time limits of given data:")
        print(f"Start year:{data_date_start}, End year:{data_date_end}")
        return
    
    pre_dates, PVALUES = clip_by_dates(pre_dates, PVALUES, start_year, end_year)
    pet_dates, PETVALUES = clip_by_dates(pet_dates, PETVALUES, start_year, end_year)
    tavg_dates, TAVGVALUES = clip_by_dates(tavg_dates, TAVGVALUES, start_year, end_year)
    q_dates, QVALUES = clip_by_dates(q_dates, QVALUES, start_year, end_year)
    
    DATA = {}
    for i in range(len(pre_dates)):
        DATA[q_dates[i]] = [PVALUES[i], PETVALUES[i], TAVGVALUES[i], QVALUES[i]]

    with open(Paths.DATASET / file_name, "w") as f:
        json.dump(DATA, f, ensure_ascii=False, indent= 4) #In order to use the same data to train an LSTM model, it is required to store them.

def create_data_npz(start_year = float("-inf"), end_year = float("inf"), file_name:str = "DATA_NUMPY.npz"):
    pre_dates, PVALUES = stripdata("pre_data.txt")
    pet_dates, PETVALUES = stripdata("pet_data.txt")
    tavg_dates, TAVGVALUES = stripdata("tavg_data.txt") 
    q_dates, QVALUES = stripdataGRDC("GRDC_Q_Day.txt")


    if start_year == float("-inf") or end_year == float("inf"):
        start_year = max(int(pre_dates[0][:4]), int(pet_dates[0][:4]), int(tavg_dates[0][:4]), int(q_dates[0][:4]))
        end_year = min(int(pre_dates[-1][:4]), int(pet_dates[-1][:4]), int(tavg_dates[-1][:4]), int(q_dates[-1][:4]))

    #datecheck
    data_date_start = max(int(pre_dates[0][:4]), int(pet_dates[0][:4]), int(tavg_dates[0][:4]), int(q_dates[0][:4]))
    data_date_end = min(int(pre_dates[-1][:4]), int(pet_dates[-1][:4]), int(tavg_dates[-1][:4]), int(q_dates[-1][:4]))

    if data_date_start > start_year or data_date_end < end_year:
        print("Given data does not qualify the time limits.")
        print("Wanted time limits:")
        print(f"Start year:{start_year}, End year:{end_year}")
        print("Time limits of given data:")
        print(f"Start year:{data_date_start}, End year:{data_date_end}")
        return
    
    pre_dates, PVALUES = clip_by_dates(pre_dates, PVALUES, start_year, end_year)
    pet_dates, PETVALUES = clip_by_dates(pet_dates, PETVALUES, start_year, end_year)
    tavg_dates, TAVGVALUES = clip_by_dates(tavg_dates, TAVGVALUES, start_year, end_year)
    q_dates, QVALUES = clip_by_dates(q_dates, QVALUES, start_year, end_year)
    
    p_vector = np.array(PVALUES)
    pet_vector = np.array(PETVALUES)
    tavg_vector = np.array(TAVGVALUES)
    q_obs_vector = np.array(QVALUES)
    dates_vector = np.array(q_dates)

    np.savez(
        Paths.DATASET / file_name,
        P = p_vector,
        PET = pet_vector,
        T = tavg_vector,
        Q = q_obs_vector,
        DATES = dates_vector
    )
    
def special_case(start_year = float("-inf"), end_year = float("inf"), file_name:str = "SPECIAL_DATA.npz"):
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
    create_data_npz_only_nc(start_year=1970, end_year=2000, file_name="1970-2000-calibration.npz")
    create_data_npz_only_nc(start_year=2000, end_year=2017, file_name="2001-2017-validation.npz")
    
    create_data_json(start_year=1970, end_year=2000, file_name="1970-2000-calibration.json")
    create_data_json(start_year=2000, end_year=2017, file_name="2001-2017-validation.json")
    """
    pass