from config import Paths
import json
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

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

def clip_by_dates(data_type, dates,values,start_date, end_date):
    new_dates = []
    new_values = []
    for i in range(len(dates)):
        if np.datetime64(dates[i]) >= np.datetime64(start_date) and np.datetime64(dates[i]) <= np.datetime64(end_date):
            new_dates.append(dates[i])
            new_values.append(values[i])
    print(f"Clipped Dates for {data_type}: {new_dates[0]} - {new_dates[-1]}")
    print(f"Clipped Value Lengths for {data_type}: {len(new_values)}")
    return new_dates, new_values

def _create_data(start_year = float("-inf"), end_year = float("inf"), file_name:str = "DATA_NUMPY", create_json:bool = False, **DATA_PATH_DICT):
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
        if data_name.endswith((".npz")):
            data = np.load(Paths.DATASET / data_name)
            dates = data["DATES"].tolist()
            values = data[data_type].tolist()
        else:
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
        dates, values = clip_by_dates(data_type, dates, values, date_start, date_end)
        DATAS[data_type] = [dates, values]

    #Create the .npz file
    len_check = None
    numpified_data = {}
    for data_type, values in DATAS.items():
        dates, values = values

        if len_check == None:
            len_check = len(values)
        elif len_check != len(values):
            print(f"{len_check} != {len(values)}")
            raise ValueError(f"{data_type} data length is NOT consistent.")
        
        numpified_data[data_type] = np.asarray(values)
        numpified_data["DATES"] = np.asarray(dates)
    
    file = np.savez(Paths.DATASET / file_name, **numpified_data)
    print(file)
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
            return file, f
    
    return file

def stripdata_2(p:str) -> list[list]:
    DATES = []
    VALUES = []
    with open(p, "r") as f:
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

def create_data_by_files(start_date = None, end_date = None, file_name:str = "DATA_NUMPY", area:float = None,**DATA_PATH_DICT):
    file_name = Path(file_name).with_suffix(".npz")
    start_date = np.datetime64(start_date)
    end_date = np.datetime64(end_date)

    date_start = float("-inf")
    date_end = float("inf")

    DATAS = {}

    for data_type, data_path in DATA_PATH_DICT.items():
        if data_path.endswith((".npz")):
            data = np.load(data_path)
            dates = data["DATES"].tolist()
            values = data[data_type].tolist()
        else:
            dates, values = stripdata_2(data_path)

        data_date_start = np.datetime64(dates[0])
        data_date_end = np.datetime64(dates[-1])
        
        if start_date == None:
            date_start = max(data_date_start, date_start)
        else:
            if data_date_start > start_date:
                print(f"{data_type} data starting date ({data_date_start}) is greater than the given start date ({start_date}).")
                return None
            date_start = start_date

        if end_date == None:
            date_end = min(data_date_end, date_end)
        else:
            if data_date_end < end_date:
                print(f"{data_type} data ending date ({data_date_end}) is less than the given end date ({end_date}).")
                return None
            date_end = end_date

        DATAS[data_type] = [dates, values]
    
    #To clip the data according to found date limits
    for data_type, values in DATAS.items():
        dates, values = values
        dates, values = clip_by_dates(data_type, dates, values, date_start, date_end)
        DATAS[data_type] = [dates, values]

    #Create the .npz file
    len_check = None
    numpified_data = {}
    for data_type, values in DATAS.items():
        dates, values = values

        if len_check == None:
            len_check = len(values)
        elif len_check != len(values):
            print(f"{len_check} != {len(values)}")
            raise ValueError(f"{data_type} data length is NOT consistent.")
        
        numpified_data[data_type] = np.asarray(values)
        numpified_data["DATES"] = np.asarray(dates, dtype=np.datetime64)
    
    if area != None:
        numpified_data["AREA"] = area
    
    np.savez(file_name, **numpified_data)
    return file_name

def create_data(start_date = None, end_date = None, output_path:str = "DATA_NUMPY", area:float = None, **DATA_PATH_DICT):
    """
    DATA_PATH_DICT = {
        "data_tag"  :   ["data_path_in_str", "old_data_tag if existing or None"]
    """
    if output_path is str:
        output_path = Path(output_path).with_suffix(".npz")
    else:
        output_path = output_path.with_suffix(".npz")

    if start_date:
        start_date = np.datetime64(start_date)
    if end_date:
        end_date = np.datetime64(end_date)


    date_start = ""
    date_end = ""

    DATAS = {}

    for data_tag, values in DATA_PATH_DICT.items():
        data_path, old_data_tag = values
        if data_path.endswith((".npz")):
            data = np.load(data_path)
            dates = data["DATES"].tolist()
            values = data[old_data_tag].tolist()
        else:
            dates, values = stripdata_2(data_path)

        data_date_start = np.datetime64(dates[0], "D")
        data_date_end = np.datetime64(dates[-1], "D")

        if start_date == None:
            date_start = max(data_date_start, date_start)
        else:
            if data_date_start > start_date:
                raise ValueError(f"{data_tag} data starts after the specified start_date.")
            else:
                date_start = start_date

        if end_date == None:
            date_end = min(data_date_end, date_end)
        else:
            if data_date_end < end_date:
                raise ValueError(f"{data_tag} data ends before the specified end_date.")
            else:
                date_end = end_date

        DATAS[data_tag] = [dates, values]
            
    #To clip the data according to found date limits
    for data_type, values in DATAS.items():
        dates, values = values
        dates ,values = clip_by_dates(data_type, dates, values, date_start, date_end)
        DATAS[data_type] = [dates, values]
    
    #Create the .npz file
    len_check = None
    numpified_data = {}
    for data_type, values in DATAS.items():
        dates, values = values

        if len_check == None:
            len_check = len(values)
        elif len_check != len(values):
            print(f"{len_check} != {len(values)}")
            raise ValueError(f"{data_type} data length is NOT consistent.")
        
        numpified_data[data_type] = np.asarray(values)
        numpified_data["DATES"] = np.asarray(dates, dtype=np.datetime64)
    
    if area is not None:
        numpified_data["AREA"] = area
        
    np.savez(output_path, **numpified_data)
    return output_path

def create_pet_data_PenmanMonteith(data_path:str, file_name:str = None):
    """"Needed Variables:
    variables = [
    "temperature_2m",
    "temperature_2m_min",
    "temperature_2m_max", 
    "surface_net_solar_radiation_sum",
    "surface_net_thermal_radiation_sum",
    "u_component_of_wind_10m",
    "v_component_of_wind_10m",
    "surface_pressure",
    "dewpoint_temperature_2m",
    ]
    OUTPUT UNIT = mm/day
    """
    data = np.load(data_path)

    # --- Birim dönüşümleri ---
    T_mean = data["temperature_2m"] - 273.15          # K → °C
    T_min  = data["temperature_2m_min"] - 273.15
    T_max  = data["temperature_2m_max"] - 273.15
    T_dew  = data["dewpoint_temperature_2m"] - 273.15
    P      = data["surface_pressure"] / 1000           # Pa → kPa
    Rns    = data["surface_net_solar_radiation_sum"] / 1e6   # J/m² → MJ/m²
    Rnl    = data["surface_net_thermal_radiation_sum"] / 1e6
    u10    = np.sqrt(data["u_component_of_wind_10m"]**2 + data["v_component_of_wind_10m"]**2)
    u2     = u10 * (4.87 / np.log(67.8 * 10 - 5.42))  # 10m → 2m

    # --- Net radyasyon ---
    Rn = Rns + Rnl   # Rnl ERA5'te zaten negatif gelir (kayıp), toplama yeterli

    # --- Psychrometric constant (γ) ---
    gamma = 0.000665 * P

    # --- Slope of saturation vapor pressure curve (Δ) ---
    delta = 4098 * (0.6108 * np.exp(17.27 * T_mean / (T_mean + 237.3))) / (T_mean + 237.3)**2

    # --- Saturation & actual vapor pressure ---
    e_s = (0.6108 * np.exp(17.27 * T_max / (T_max + 237.3)) +
           0.6108 * np.exp(17.27 * T_min / (T_min + 237.3))) / 2
    e_a = 0.6108 * np.exp(17.27 * T_dew / (T_dew + 237.3))

    # --- Soil heat flux (günlük için ≈ 0) ---
    G = 0

    # --- FAO-56 Penman-Monteith ---
    numerator   = 0.408 * delta * (Rn - G) + gamma * (900 / (T_mean + 273)) * u2 * (e_s - e_a)
    denominator = delta + gamma * (1 + 0.34 * u2)
    PET = numerator / denominator   # mm/gün

    mask = PET < 0
    PET[mask] = 0

    np.savez(
        file=file_name.with_suffix(".npz"),
        PET=PET,
        DATES=data["DATES"]
    )
    print(f"PET saved to {file_name.with_suffix('.npz')}")

def change_P_unit(data_path:str, file_name:str):
    data = np.load(data_path.with_suffix(".npz"))
    if file_name == None:
        file_name = data_path.with_suffix(".npz")
    
    p = data["total_precipitation_sum"] * 1000 #m/day to mm/day
    np.savez(
        file=file_name.with_suffix(".npz"),
        DATES = data["DATES"],
        P=p,
    )
    print(f"P saved to {file_name.with_suffix('.npz')}")

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
    dates, values = stripdata_2("C:\Hydrology\GR4J\Dataset\pre_new_data.txt")
    print(dates[0])
    print(values[0])
    n_dates = np.asarray(dates, dtype=np.datetime64)
    print(n_dates[0])
    plt.plot(n_dates, values)
    plt.show()
    pass