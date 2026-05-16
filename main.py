import numpy as np
import json
import matplotlib.pyplot as plt

import GR4J_Model as G
from DE_Optim import Optimizer
import DataHandler as DH
from config import Paths
import GEE_Exporter as GE

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
    obs_plot = Q_obs[-730:]
    sim_plot = Q_sim[-730:]
    P_plot = P[-730:]
    days = range(len(obs_plot))

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(days, obs_plot, label="Observed", color="black", linewidth=1.5)
    ax1.plot(days, sim_plot, label="Simulated", color="red", linestyle="--", linewidth=1.2)

    ax1.set_title(f"Briance Catchment - Last two years (2016-2017) (NSE: {nse:.4f})")
    ax1.set_xlabel("Time (day)")
    ax1.set_ylabel("Discharge (mm/day)")
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()

    ax2.bar(days, P_plot, label="Precipitation", color="blue", alpha=0.3, width=1.0)
    ax2.set_ylabel("Precipitation (mm)")
    ax2.invert_yaxis()
    ax2.set_ylim(max(P_plot) * 3, 0)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right')

    plt.savefig(Paths.ROOT / "plot.png", dpi = 300, bbox_inches='tight')

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

if __name__ == "__main__":
   #GET_PET_DATA_FROM_GEE()
   #GET_P_DATA_FROM_GEE()

   premade_function()