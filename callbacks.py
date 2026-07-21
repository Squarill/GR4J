import numpy as np
from pathlib import Path as p
import matplotlib.pyplot as plt
from datetime import datetime as dt
import zipfile as zf
import gradio as gr
import pandas as pd


import GR4J_Model as G
from DE_Optim import Optimizer
import DataHandler as DH
from config import Paths
import GEE_Exporter as GEE

import test_optim as to

"""****************** GENERAL FUNCTIONS *****************"""

def fig_plotter(to_plot_dict:dict, DATES, x_label:str = "Time (day)", y_label:str = "Discharge (m³/s)", inversed_y_label = None, xlim:list = None, ylim_bottom:float = None, title:str = None):
    """
    INPUT TYPES
    to_plot_dict = dict[str (label): [bool (inverse or not), linestyle, color, plot style (bar or plot), np.ndarray (values)]]
    DATES   =   np.ndarray[np.datetime64]
    xlim    =   [np.datetime64, np.datetime64]
    """

    xlim_l = DATES[0]
    xlim_r = DATES[-1]
    if xlim is not None:
        xlim_l = np.datetime64(xlim[0])
        xlim_r = np.datetime64(xlim[1])
    
    fig, ax1 = plt.subplots(figsize=(12, 6)) #Non-Inversed, normal
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y_label)
    ax1.set_xlim(xlim_l, xlim_r)
    ax1.grid(True, alpha=0.5)

    ax2 = ax1.twinx() #Inversed
    ax2.grid(True, alpha=0.5, linestyle="--", linewidth=1)

    includes_inversed = False
    y_lim_inversed = 0
    
    for label, values in to_plot_dict.items():
        linestyle = values[1]
        color = values[2]
        style = values[3]
        if values[0]:
            includes_inversed = True
            y_lim_inversed = max(max(values[4]), y_lim_inversed)
            if style == "bar":
                ax2.bar(DATES, values[4], label=label, color=color, alpha=0.3, width=1.0)
            elif style == "plot":
                ax2.plot(DATES, values[4], label=label, color=color, linestyle=linestyle, linewidth=1.2)
        else:
            if style == "bar":
                ax1.bar(DATES, values[4], label=label, color=color, alpha=0.3, width=1.0)
            elif style == "plot":
                ax1.plot(DATES, values[4], label=label, color=color, linestyle=linestyle, linewidth=1.2)

    if includes_inversed:
        ax2.set_ylabel(inversed_y_label)
        ax2.invert_yaxis()
        ax2.set_ylim(y_lim_inversed * 3, 0)
    else:
        ax2.remove()
    
    if ylim_bottom is not None:
        ax1.set_ylim(bottom=ylim_bottom)

    fig.legend(loc="upper right")
    if title is not None:
        fig.suptitle(title)

    fig.autofmt_xdate()

    return fig

def npz_loader(file_path:p):
    
    with zf.ZipFile(file_path) as zip_ref:
        for info in zip_ref.infolist():
            pass
    
    return np.load(file_path)

"""****************** SIMULATE TAB ******************"""

def Sim_simulate_btn(X1, X2, X3, X4, S, R, Dataset, Area, Warmup_days, plot_start_year, plot_end_year):
    if S <= 0:  
        S = None
    if R <= 0:
        R = None

    data = np.load(Dataset)

    P = data["P"]
    PET = data["PET"]
    Q_obs = data["Q"]
    DATES = data["DATES"]

    if not Area:
        Area = data["AREA"]
    else:
        Area = float(Area)

    Q_obs, Q_sim = G.GR4J_Numba(X1, X2, X3, X4, P, PET, Q_obs, Area, S, R)[0:2]
    nse = G.calculate_nse(Q_obs, Q_sim, warmup_days=Warmup_days)
    NSE_output = f"NSE on given Dataset: {nse:.4f}"

    #Plot
    to_plot_dict = {
        "Observed": [False, "-", "black", "plot", Q_obs*Area/86.4],
        "Simulated": [False, "--", "red", "plot", Q_sim*Area/86.4],
        "Precipitation": [True, "-", "blue", "bar", P]
    }

    plot_start_year = np.datetime64(int(plot_start_year), "s")
    plot_end_year = np.datetime64(int(plot_end_year), "s")
    fig = fig_plotter(to_plot_dict, DATES, x_label="Time (day)", y_label="Discharge (m³/s)", inversed_y_label="Precipitation (mm/day)", xlim=[plot_start_year, plot_end_year], title="Hydrograph and Hyteograph", ylim_bottom=0)

    return NSE_output, fig

def Sim_file_uploaded(dataset):
    if dataset is None:
        return None, None, None
    
    data = np.load(dataset)
    return dt.strptime(str(data["DATES"][0]), "%Y-%m-%d"), dt.strptime(str(data["DATES"][-1]), "%Y-%m-%d"), data["AREA"]

"""****************** DATA PREPARATION TAB ******************"""

def DataPrep_GR4J_file_uploaded(dataset):
    if dataset is None:
        return None, None
    
    dates = None
    if dataset.endswith(".npz"):
        data = np.load(dataset)
        dates = data["DATES"]
    elif dataset.endswith(".txt"):
        dates = DH.stripdata_2(dataset)[0]
    
    return dt.strptime(str(dates[0]), "%Y-%m-%d"), dt.strptime(str(dates[-1]), "%Y-%m-%d")

def DataPrep_GR4J_prepare_btn(P_data, PET_data, Q_obs_data, Area, start_date, end_date, file_name, session_id:str):
    start_date = np.datetime64(start_date, "D")
    end_date = np.datetime64(end_date, "D")
    output_folder = Paths.DATASET / f"{session_id}"
    if not output_folder.exists():
        output_folder.mkdir()
    
    if file_name:
        output_path = output_folder / file_name
    else:
        output_path = output_folder / "GR4J_DATA"
    output_path = output_path.with_suffix(".npz")

    DATA_PATH_DICT = {
        "P": P_data,
        "PET": PET_data,
        "Q": Q_obs_data
    }

    output_file = DH.create_data_by_files(**DATA_PATH_DICT, start_date=start_date, end_date=end_date, file_name=output_path, area=Area)
    
    #Since the output file above is a windows path object it should be converted to string for gradio to understand.
    return str(output_file)

def data_kit_file_uploaded(dataset):
    if dataset is None:
        return gr.update(choices=[]), None, None, None
    
    if dataset.endswith(".txt"):
        dates, values = DH.stripdata_2(dataset)
        return gr.update(choices=[]), None, str(dates[0]), str(dates[-1])
    
    data = np.load(dataset)
    choices = list(data.files)
    
    return gr.update(choices=choices, value=choices[0]), choices[0], str(data["DATES"][0]), str(data["DATES"][-1])

def DataPrep_core_data_preparation_btn(start_date, end_date, area, output_name, session_id, *args):
    start_date = np.datetime64(start_date, "D")
    end_date = np.datetime64(end_date, "D")
    output_folder = Paths.SESSIONS / f"{session_id}"

    dataset_list = []

    for i in range(0,len(args)-3,3):
        pth = args[i]
        if pth is not None:
            dataset_list.append([pth, args[i+1], args[i+2]])

    print(dataset_list)

    if not output_folder.exists():
        output_folder.mkdir()
    
    if output_name:
        output_path = output_folder / output_name
    else:
        output_path = output_folder / "CORE_DATA"
    output_path = output_path.with_suffix(".npz")

    DATA_PATH_DICT = {}

    for value in dataset_list:
        dataset_path = value[0]
        data_to_be_extracted = value[1]
        new_tag_name = value[2]

        if dataset_path is not None:
            DATA_PATH_DICT[new_tag_name] = [dataset_path, data_to_be_extracted]
    print(DATA_PATH_DICT)
    DH.create_data(start_date=start_date, end_date=end_date, output_path=output_path, area=area, **DATA_PATH_DICT)

    return str(output_path)

def DataPrep_GEE_export_btn(session_id, output_name, geojson, variables, start_date, end_date, exporter_service):
    output_path = Paths.SESSIONS / f"{session_id}" / output_name
    output_path = output_path.with_suffix(".npz")

    if not output_path.parent.exists():
        output_path.parent.mkdir()
    
    for log in exporter_service.export(geojson_path=geojson, start_date=start_date, end_date=end_date, variables=variables, output_path=output_path):
        if log[-1] == "END":
            yield str(output_path), log[-1]
        else:
            yield None, log[-1]

def DataPrep_Penman_Monteith_btn(session_id, dataset, output_name):
    output_path = Paths.SESSIONS / f"{session_id}" / output_name
    output_path = output_path.with_suffix(".npz")

    if not output_path.parent.exists():
        output_path.parent.mkdir()

    DH.create_pet_data_PenmanMonteith(dataset, output_path)

    return str(output_path)

def DataPrep_dataset_calculator_calculate_btn(dataset, operator, number, variable):
    if dataset is None:
        return None
    
    def check(number):
        try:
            float(number)
            return True
        except:
            return False

    data = np.load(dataset)

    if variable in data.files or variable == "All":
        new_data = {}
        for key, value in data.items():
            if key == variable or variable == "All":
                if operator == "Add" and check(number):
                    new_data[key] = value + float(number)
                elif operator == "Subtract" and check(number):
                    new_data[key] = value - float(number)
                elif operator == "Multiply" and check(number):
                    new_data[key] = value * float(number)
                elif operator == "Divide" and check(number):
                    new_data[key] = value / float(number)
                elif operator == "Change Variable Name" and number != "All":
                    new_data[str(number)] = value
            else:
                new_data[key] = value

        np.savez(dataset, **new_data)
        return str(dataset)
    else:
        return None

def DataPrep_dataset_calculator_file_uploaded(dataset):
    if dataset is None:
        return gr.update(choices=["All"])
    
    try:
        data = np.load(dataset)
        tag_list = ["All"] + list(data.files)
        
        return gr.update(choices=tag_list)
    except:
        return gr.update(choices=["All"])

def DataPrep_dataset_observer_file_uploaded(dataset):
    """
    Outputs = dataset_start_date, dataset_end_date, observe_start_date, observe_end_date, data (dropdown menu)
    """
    if dataset is None:
        return None, None, None, None, None
    
    data = np.load(dataset)
    dates = data["DATES"]
    choices = list(data.files)

    return str(dates[0]), str(dates[-1]), str(dates[0]), str(dates[-1]), gr.update(choices=choices, value=choices[0])

def DataPrep_observe_btn(dataset, data_name, observe_start_date, observe_end_date):
    """
    Outputs = plot (fig), data_info (.ndarray)
    """
    if dataset is None:
        return None, None

    data = np.load(dataset)
    dates = data["DATES"]

    if data_name == "AREA":
        return None, pd.DataFrame({data_name: data[data_name]}, index=[0])

    if type(dates[0]) is not np.datetime64:
        dates = dates.astype(np.datetime64)

    mask = (dates >= np.datetime64(observe_start_date, "D")) & (dates <= np.datetime64(observe_end_date, "D"))

    dates = dates[mask]
    selected_data = data[data_name]

    selected_data = selected_data[mask]

    #Figure
    to_plot_dict = {
        str(data_name): [False, "-", "black", "plot", selected_data]
    }
    fig = fig_plotter(to_plot_dict, dates, x_label="Time (day)", y_label=data_name, inversed_y_label=None, xlim=[np.datetime64(observe_start_date, "D"), np.datetime64(observe_end_date, "D")])

    #Selected data
    df = pd.DataFrame({
        "Date": dates,
        data_name: selected_data
    })

    return fig, df

"""****************** CALIBRATE AND VALIDATE TAB ******************"""

def CaV_calibrate_btn(calibration_dataset, Area, calibration_warmup_days, maxiter, popsize, cpu_count, tolerance, object_function, module:str):
    bounds = [(0, 10000), (-10, 10), (0, 1000), (1.1, 15.0)]
    data = np.load(calibration_dataset)

    Area = Area if Area else data["AREA"]

    if module == "GR4J + CemaNeige":
        bounds += [(0.01,1), (0,20)]
        best_params = to.optimize(to.o_f_GR4J_CN_NSE, data, bounds=bounds, maxiter=maxiter, popsize=popsize, cpu_count=cpu_count, warmup_days=calibration_warmup_days, tol=tolerance)
        Q_obs_out, Q_sim, S, R, g, eTG = G.GR4J_CemaNeige_Numba(best_params[0], best_params[1], best_params[2], best_params[3], best_params[4], best_params[5], data["P"], data["PET"], data["T"], data["Q"], Area)
        return best_params + [S, R, g, eTG]
    else:
        best_params = to.optimize(to.o_f_GR4J_NSE, data, bounds = bounds, maxiter=maxiter, popsize=popsize, cpu_count=cpu_count, warmup_days=calibration_warmup_days)
        Q_obs_out, Q_sim, S, R = G.GR4J_Numba(best_params[0], best_params[1], best_params[2], best_params[3], data["P"], data["PET"], data["Q"], Area)
        return best_params + [None, None] + [S, R, None, None]

def CaV_validate_btn(X1, X2, X3, X4, X5, X6, S, R, g, eTG, validation_dataset, Area, validation_warmup_days, module):
    #if S <= 0:
    #    S = -1.0
    #if R <= 0:
    #    R = -1.0
    #if g <= 0:
    #    g = -1.0
    #if eTG <= 0:
    #    eTG = -1.0
    
    if module == "GR4J + CemaNeige":
        data = np.load(validation_dataset)
        P = data["P"]
        PET = data["PET"]
        T = data["T"]
        Q_obs = data["Q"]
        DATES = data["DATES"]

        if not Area:
            Area = data["AREA"]
        else:
            Area = float(Area)
        
        Q_obs_out, Q_sim, S, R, g, eTG = G.GR4J_CemaNeige_Numba(X1, X2, X3, X4, X5, X6, P, PET, T, Q_obs, Area)

        nse = G.calculate_nse(Q_obs_out, Q_sim, warmup_days=validation_warmup_days)
        kge = G.calculate_kge(Q_obs_out, Q_sim, warmup_days=validation_warmup_days)
        NSE_output = f"NSE on Validation Set: {nse:.4f}"
        KGE_output = f"KGE on Validation Set: {kge:.4f}"
    else:
        data = np.load(validation_dataset)

        P = data["P"]
        PET = data["PET"]
        Q_obs = data["Q"]
        DATES = data["DATES"]

        if not Area:
            Area = data["AREA"]
        else:
            Area = float(Area)
        
        Q_obs_out, Q_sim, S, R = G.GR4J_Numba(X1, X2, X3, X4, P, PET, Q_obs, Area, S, R)
        nse = G.calculate_nse(Q_obs_out, Q_sim, warmup_days=validation_warmup_days)
        kge = G.calculate_kge(Q_obs_out, Q_sim, warmup_days=validation_warmup_days)
        NSE_output = f"NSE on Validation Set: {nse:.4f}"
        KGE_output = f"KGE on Validation Set: {kge:.4f}"

    to_plot_dict = {
        "Observed": [False, "-", "black", "plot", Q_obs_out*Area/86.4],
        "Simulated": [False, "--", "red", "plot", Q_sim*Area/86.4],
        "Precipitation": [True, "-", "blue", "bar", P]
    }
    
    fig = fig_plotter(to_plot_dict, DATES, inversed_y_label="Precipitation (mm/day)", x_label="Time (day)", y_label="Discharge (m³/s)", title="Hydrograph and Hyteograph")

    return NSE_output, KGE_output, fig

def CaV_module_change(module):
    if module == "GR4J + CemaNeige":
        print("Açık")
        return gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)
    else:
        print("Kapalı")
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

def CaV_file_uploaded(dataset):
    if dataset is None:
        return None, None, None
    
    data = np.load(dataset)

    if "AREA" not in data.files:
        area = None
    else:
        area = data["AREA"]
    
    dates = data["DATES"]
    start_date = dt.strptime(str(dates[0]), "%Y-%m-%d")
    end_date = dt.strptime(str(dates[-1]), "%Y-%m-%d")
    return area, start_date, end_date