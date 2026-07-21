import numpy as np
import json
import matplotlib.pyplot as plt
from pathlib import Path as p
import os

import GR4J_Model as G
from DE_Optim import Optimizer
import DataHandler as DH
from config import Paths
import GEE_Exporter as GE

import gradio as gr
import queue
import threading
import uuid

def premade_function():
    #Creating the data
    DATA_PATH_DICT = {
        "P": "pre_new_data.txt",
        "PET": "BRIANCE_GEE_PET_1950-2020.npz",
        "Q": "q_data.txt"
    }
    DH.create_data(**DATA_PATH_DICT, start_year=1970, end_year=2000, file_name="1970-2000-calibration")
    DH.create_data(**DATA_PATH_DICT, start_year=2001, end_year=2017, file_name="2001-2017-validation")

    #Defining the bounds and catchment area
    bounds = [(0, 2000), (-10, 10), (0, 300), (1.1, 15.0)]
    A = 603.09 #km²

    #Pulling the created data
    npz_data = np.load(Paths.DATASET / "1970-2000-calibration.npz")
    P = npz_data["P"].astype(np.float64)
    PET = npz_data["PET"].astype(np.float64)
    Q = npz_data["Q"].astype(np.float64)

    NUMBA_DATA = [P, PET, Q] #This order is necessary for used GR4J function

    #Activating DE optimizer
    #cpu_count = -1 means it will use every core available in the system
    Op = Optimizer(A, bounds=bounds, NUMBA_DATA=NUMBA_DATA, warmup_days=1460, maxiter=500, popsize=40, cpu_count=-1)
    best_params = Op.optimize(f = Op.objective_function_GR4J_Numba)

    #In order to have the final S and R values, we will run the function one more time with the same data
    Q_obs, Q_sim, S, R = G.GR4J_Numba(best_params[0], best_params[1], best_params[2], best_params[3],P, PET, Q, A)

    #Preparing the validation process
    npz_data = np.load(Paths.DATASET / "2001-2017-validation.npz")
    P = npz_data["P"].astype(np.float64)
    PET = npz_data["PET"].astype(np.float64)
    Q = npz_data["Q"].astype(np.float64)
    
    #NSE calculation on validation data
    Q_obs, Q_sim, S, R = G.GR4J_Numba(best_params[0], best_params[1], best_params[2], best_params[3],P, PET, Q, A, S, R)
    nse = G.calculate_nse(Q_obs, Q_sim, warmup_days=0)
    kge = G.calculate_kge(Q_obs, Q_sim, warmup_days=0)
    print(f"NSE on Validation Set: {nse:.4f}")
    print(f"KGE on Validation Set: {kge:.4f}")

    #Plotting the last 730 days' observed and simulated hydrographs
    plot_data(Q_obs, Q_sim, P, nse)

def GET_PET_DATA_FROM_GEE():
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
    exporter = GE.GEE_Exporter("bratislava-danube-river", Paths.DATASET/"Briance.geojson", "1950-01-01", "2020-01-01", variables=variables, output_path=Paths.DATASET/"BRIANCE_GEE_PET_REQS_1950-2020.npz")
    exporter.Authenticate()
    exporter.export()
    
    DH.create_pet_data_PenmanMonteith(Paths.DATASET/"BRIANCE_GEE_PET_REQS_1950-2020.npz", Paths.DATASET/"BRIANCE_GEE_PET_1950-2020")

def GET_P_DATA_FROM_GEE():
    variables = ["total_precipitation_sum"]
    exporter = GE.GEE_Exporter("bratislava-danube-river", Paths.DATASET/"Briance.geojson", "1950-01-01", "2020-01-01", variables=variables, output_path=Paths.DATASET/"BRIANCE_GEE_P_1950-2020.npz")
    exporter.Authenticate()
    exporter.export()

    DH.change_P_unit(Paths.DATASET/"BRIANCE_GEE_P_1950-2020.npz", Paths.DATASET/"BRIANCE_GEE_P_1950-2020")

def plot_data(q_obs, q_sim, p, nse):
    days = range(len(q_obs))
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(days, q_obs, label="Observed", color="black", linewidth=1.5)
    ax1.plot(days, q_sim, label="Simulated", color="red", linestyle="--", linewidth=1.2)

    ax1.set_title(f"Briance Catchment (NSE: {nse:.4f})")
    ax1.set_xlabel("Time (day)")
    ax1.set_ylabel("Discharge (mm/day)")
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()

    ax2.bar(days, p, label="Precipitation", color="blue", alpha=0.3, width=1.0)
    ax2.set_ylabel("Precipitation (mm)")
    ax2.invert_yaxis()
    ax2.set_ylim(max(p) * 3, 0)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right')

    plt.savefig(Paths.ROOT / "plot.png", dpi = 300, bbox_inches='tight')

    pass

    css = """
    #cal_output textarea {
        overflow-y: scroll;
    }
    """

    js = """
    function autoScroll() {
        const observer = new MutationObserver(() => {
            const textarea = document.querySelector('#cal_output textarea');
            if (textarea) {
                textarea.scrollTop = textarea.scrollHeight;
            }
        });
        
        const textarea = document.querySelector('#cal_output textarea');
        if (textarea) {
            observer.observe(textarea, { childList: true, subtree: true, characterData: true });
        }
    }
    """

def Calibrate(Calibration_data, Area, Warmup_days, maxiter, popsize, cpu_count):
    bounds = [(0, 2000), (-10, 10), (0, 300), (1.1, 15.0)]
    P = np.load(Calibration_data)["P"]
    PET = np.load(Calibration_data)["PET"]
    Q_obs = np.load(Calibration_data)["Q"]
    NUMBA_DATA = [P, PET, Q_obs]
    Op = Optimizer(Area, bounds=bounds,NUMBA_DATA=NUMBA_DATA, warmup_days=Warmup_days, maxiter=maxiter, popsize=popsize, cpu_count=cpu_count)

    best_params = Op.optimize(f = Op.objective_function_GR4J_Numba)
    X1 = best_params[0]
    X2 = best_params[1]
    X3 = best_params[2]
    X4 = best_params[3]
    Q_obs_out, Q_sim, S, R = G.GR4J_Numba(X1, X2, X3, X4, P, PET, Q_obs, Area)
    return float(X1), float(X2), float(X3), float(X4), float(S), float(R)

def Validate(X1, X2, X3, X4, S, R, Validation_data, Area, Warmup_days):
    if S <= 0:  
        S = None
    if R <= 0:
        R = None
    
    data = np.load(Validation_data)

    P = data["P"]
    PET = data["PET"]
    Q_obs = data["Q"]
    DATES = data["DATES"]
    
    Q_obs_out, Q_sim = G.GR4J_Numba(X1, X2, X3, X4, P, PET, Q_obs, Area, S, R)[0:2]
    nse = G.calculate_nse(Q_obs_out, Q_sim, warmup_days=Warmup_days)
    ValidationOutput = f"NSE on Validation Set: {nse:.4f}"
    print(DATES[0], DATES[-1], type(DATES), type(DATES[0]))
    return ValidationOutput, plot_fig(Q_obs_out*Area/86.4, Q_sim*Area/86.4, P, DATES)

def plot_fig(Q_obs, Q_sim, P, DATES, xlim:list = None):
    xlim_l = DATES[0]
    xlim_r = DATES[-1]
    if xlim != None:
        xlim_l = np.datetime64(xlim[0])
        xlim_r = np.datetime64(xlim[1])
        
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(DATES, Q_obs, label="Observed", color="black", linewidth=1.5)
    ax1.plot(DATES, Q_sim, label="Simulated", color="red", linestyle="--", linewidth=1.2)
    ax1.set_title("Hydrograph and Hyteograph")
    ax1.set_xlabel("Time (day)")
    ax1.set_xlim(xlim_l, xlim_r)
    ax1.set_ylabel("Discharge (m³/s)")
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.bar(DATES, P, label="Precipitation", color="blue", alpha=0.3, width=1.0)
    ax2.set_ylabel("Precipitation (mm)")
    ax2.invert_yaxis()
    ax2.set_ylim(max(P) * 3, 0)
    
    fig.legend(loc="upper right")

    return fig

if __name__ == "__main__":
    def init():
        return str(uuid.uuid4())

    with gr.Blocks(fill_height=True, fill_width=True) as demo:
        session_id = gr.State()
        demo.load(init, inputs=[], outputs=[session_id])

        gr.Markdown("## GR4J Modeling Tool")
        with gr.Tab(label="Simulate"):
            with gr.Row(equal_height=True):
                Sim_Dataset = gr.File(file_count="single", file_types=[".npz"], label="Dataset")
                Sim_Area = gr.Number(label="Catchment Area (km²)")
                Sim_Warmup_days = gr.Number(label="Warmup Days", value=1460)

            with gr.Row(equal_height=True, height="auto"):
                with gr.Column():
                    Sim_X1 = gr.Slider(label="X1", interactive=True, minimum=0, maximum=2000, step=1)
                    Sim_X2 = gr.Slider(label="X2", interactive=True, minimum=-10, maximum=10, step=0.1)
                    Sim_X3 = gr.Slider(label="X3", interactive=True, minimum=0, maximum=300, step=1)
                    Sim_X4 = gr.Slider(label="X4", interactive=True, minimum=1.1, maximum=15.0, step=0.1)
                    Sim_S = gr.Slider(label="S", interactive=True, minimum=0, maximum=2000, step=1)
                    Sim_R = gr.Slider(label="R", interactive=True, minimum=0, maximum=300, step=1)
                    Sim_btn = gr.Button("Simulate")
                    Sim_NSE = gr.Textbox(label="NSE")
                Sim_graph = gr.Plot(label="Hydrograph and Hyteograph")

            Sim_btn.click(fn = Validate, inputs=[Sim_X1, Sim_X2, Sim_X3, Sim_X4, Sim_S, Sim_R, Sim_Dataset, Sim_Area, Sim_Warmup_days], outputs=[Sim_NSE, Sim_graph])

        with gr.Tab(label="Calibrate and Validate"):
            with gr.Row(equal_height=True):
                with gr.Column():
                    Area = gr.Number(label="Catchment Area (km²)")
                    Warmup_days_on_cal = gr.Number(label="Warmup Days on Calibration", value=1460)
                    Warmup_day_on_val = gr.Number(label="Warmup Days on Validation", value=0)
                Calibration_data = gr.File(file_count="single", file_types=[".npz"], label="Calibration Data")
                Validation_data = gr.File(file_count="single", file_types=[".npz"], label="Validation Data")
            
            with gr.Row():
                maxiter = gr.Number(label="Max Iterations", value=500)
                popsize = gr.Number(label="Population Size", value=40)
                cpu_count = gr.Number(label="CPU Count (-1 for all of them)", value=-1)
            
            with gr.Row():
                Calibrate_btn = gr.Button("Calibrate")
                
            with gr.Column():
                with gr.Row(equal_height=True):
                    X1 = gr.Number(label="X1", interactive=False)
                    X2 = gr.Number(label="X2", interactive=False)
                    X3 = gr.Number(label="X3", interactive=False)
                    X4 = gr.Number(label="X4", interactive=False)
                    S = gr.Number(label="S", interactive=True)
                    R = gr.Number(label="R", interactive=True)
                    with gr.Column():
                        CandVal_warning = gr.Markdown("## Warning!\nIf the validation set does not start right after the calibration set, set S and R values as 0 and add a validation warmup day value above.")
                        Validate_btn = gr.Button("Validate")
                with gr.Row(equal_height=True):
                    ValidationOutput = gr.Textbox(label="NSE on Validation Set", scale = 1)
                    
                Graph = gr.Plot(label="Hydrograph and Hyteograph")
            
            Calibrate_btn.click(Calibrate, inputs=[Calibration_data, Area, Warmup_days_on_cal, maxiter, popsize, cpu_count], outputs=[X1, X2, X3, X4, S, R])
            Validate_btn.click(Validate, inputs=[X1, X2, X3, X4, S, R, Validation_data, Area, Warmup_day_on_val], outputs=[ValidationOutput, Graph])

        with gr.Tab(label="Data Preparation"):
            DataP_Plot_Dict = {}
            DataP_Output_Path = ""

            def DataP_wrapper(start_year, end_year, P_file, PET_file, Q_file, file_name, session_id):
                global DataP_Plot_Dict
                global DataP_Output_Path
                DataP_Plot_Dict.clear()

                def plot(tag, npz_file):
                    data = np.load(npz_file)
                    values = data[tag]
                    days = range(len(values))

                    fig, ax = plt.subplots()
                    ax.plot(days, values)
                    ax.set_title(tag)
                    ax.set_xlabel("Time (day)")
                    ax.set_ylabel(tag)

                    return fig
                
                DATA_PATH_DICT = {
                    "P": P_file,
                    "PET": PET_file,
                    "Q": Q_file
                }
                if p.exists(Paths.DATASET / session_id):
                    pass
                else:
                    p.mkdir(Paths.DATASET / session_id)

                DataP_Output_Path = Paths.DATASET / session_id / f"{file_name}"
                DataP_Output_Path = p.with_suffix(DataP_Output_Path,".npz")
                output_file = DH.create_data_by_files(**DATA_PATH_DICT, start_year=start_year, end_year=end_year, file_name=DataP_Output_Path)

                #Create the plot dict
                data = np.load(output_file)
                plot_dict = {}
                for key in data.keys():
                    if key != "DATES":
                        plot_dict[key] = plot(key, output_file)
                DataP_Plot_Dict = plot_dict
                # Gradio in this version does not accept Path objects. Thus, stringification is required.
                return str(output_file), gr.update(choices=list(DataP_Plot_Dict.keys()), value=list(DataP_Plot_Dict.keys())[0])
            
            with gr.Row(equal_height=True):
                DataP_P = gr.File(file_count="single", file_types=[".txt",".npz"], label="Precipitation Data")
                DataP_PET = gr.File(file_count="single", file_types=[".txt",".npz"], label="PET Data")
                DataP_Q_obs = gr.File(file_count="single", file_types=[".txt",".npz"], label="Observed Discharge Data")
                
            with gr.Row(equal_height=True):
                with gr.Column(scale=1):
                    DataP_Start_Year = gr.Number(label="Start Year", value=1900)
                    DataP_End_Year = gr.Number(label="End Year", value=2030)
                    DataP_File_Name = gr.Textbox(label="File Name", value="Dataset")
                
                DataP_Preapare_btn = gr.Button("Prepare", scale=1)

                with gr.Column(scale=3):
                    DataP_Output_File = gr.File(type = "filepath", file_count="single", file_types=[".npz"], label="Output File", interactive=False)

                
            gr.Markdown("# Observe the created dataset")
            with gr.Row(equal_height=True):
                def DataP_change_plot(variable):
                    data = np.load(DataP_Output_Path)
                    min = np.min(data[variable])
                    max = np.max(data[variable])
                    mean = np.mean(data[variable])
                    std = np.std(data[variable])

                    return DataP_Plot_Dict[variable], str(min), str(max), str(mean), str(std)

                with gr.Column():
                    DataP_tags = gr.Dropdown(label="Variables", choices=[])
                    DataP_max = gr.Textbox(label="Maximum Value", interactive=False)
                    DataP_min = gr.Textbox(label="Minimum Value", interactive=False)
                    DataP_mean = gr.Textbox(label="Mean Value", interactive=False)
                    DataP_std = gr.Textbox(label="Standard Deviation", interactive=False)
                DataP_plot = gr.Plot()

                DataP_tags.change(
                    DataP_change_plot,
                    inputs=DataP_tags,
                    outputs=[DataP_plot,DataP_max, DataP_min, DataP_mean, DataP_std]
                )
            
            DataP_Preapare_btn.click(fn = DataP_wrapper, inputs=[DataP_Start_Year, DataP_End_Year, DataP_P, DataP_PET, DataP_Q_obs, DataP_File_Name, session_id], outputs=[DataP_Output_File, DataP_tags])

    try:
        demo.launch(server_name="0.0.0.0", server_port=7240)
    finally:
        demo.close()