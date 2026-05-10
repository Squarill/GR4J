import numpy as np
import json
import matplotlib.pyplot as plt

import GR4J_Model as GR4J
from DE_Optim import Optimizer
import DataHandler as DH
from Paths import Paths


if __name__ == "__main__":
    """
    #Creating the data
    DATA_PATH_DICT = {
        "P": "pre_data.txt",
        "PET": "pet_data.txt",
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
    Q_obs, Q_sim, S, R = GR4J.GR4J_Numba(best_params[0], best_params[1], best_params[2], best_params[3],P, PET, Q, A)

    #Preparing the validation process
    npz_data = np.load(Paths.DATASET / "2001-2017-validation.npz")
    P = npz_data["P"].astype(np.float64)
    PET = npz_data["PET"].astype(np.float64)
    Q = npz_data["Q"].astype(np.float64)
    
    #NSE calculation on validation data
    Q_obs, Q_sim, S, R = GR4J.GR4J_Numba(best_params[0], best_params[1], best_params[2], best_params[3],P, PET, Q, A, S, R)
    nse = GR4J.calculate_nse(Q_obs, Q_sim, warmup_days=0)
    print(f"NSE on Validation Set: {nse:.4f}")

    #Plotting the last 730 days' observed and simulated hydrographs
    obs_plot = Q_obs[-730:]
    sim_plot = Q_sim[-730:]
    days = range(len(obs_plot))

    plt.figure(figsize=(12, 6))

    plt.plot(days, obs_plot, label="Observed", color="black", linewidth=1.5)

    plt.plot(days, sim_plot, label="Simulated", color="red", linestyle="--", linewidth=1.2)

    plt.title(f"Briance Catchment - Last two years (2016-2017) (NSE: {nse:.4f})")
    plt.xlabel("Time (day)")
    plt.ylabel("Discharge (mm/day)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
    """

    A = 131520.65 #km²

    bounds = [
    (100, 2000),   # X1
    (-10, 5),      # X2
    (1, 500),     # X3
    (1.1, 15.0),   # X4
    (-5.0, 5.0),    # CTG
    (0.0, 10.0),    # Kf
]

    #Pulling the created data
    npz_data = np.load(Paths.DATASET / "bratislava_1970_2000.npz")
    P = npz_data["P"].astype(np.float64)
    PET = npz_data["PET"].astype(np.float64)
    T = npz_data["T"].astype(np.float64)
    Q = npz_data["Q"].astype(np.float64)
    print(f"P_len = {len(P)}")
    print(f"PET_len = {len(PET)}")
    print(f"T_len = {len(T)}")
    print(f"Q_len = {len(Q)}")
    NUMBA_DATA = [P, PET, T, Q] #This order is necessary for used GR4J function

    #Activating DE optimizer
    #cpu_count = -1 means it will use every core available in the system
    Op = Optimizer(A, bounds=bounds, NUMBA_DATA=NUMBA_DATA, warmup_days=1460, maxiter=1000000, popsize=60, cpu_count=-1)
    best_params = Op.optimize(f = Op.objective_function_GR4J_CemaNeige_Numba)

    Q_obs, Q_sim, S, R, G, Etat = GR4J.GR4J_CemaNeige_Numba(best_params[0], best_params[1], best_params[2], best_params[3], best_params[4], best_params[5], P, PET, T, Q, A)

    #Preparing the validation process
    npz_data = np.load(Paths.DATASET / "bratislava_2001_2020.npz")
    P = npz_data["P"].astype(np.float64)
    PET = npz_data["PET"].astype(np.float64)
    T = npz_data["T"].astype(np.float64)
    Q = npz_data["Q"].astype(np.float64)
    
    #NSE calculation on validation data
    Q_obs, Q_sim, S, R, G, Etat = GR4J.GR4J_CemaNeige_Numba(best_params[0], best_params[1], best_params[2], best_params[3], best_params[4], best_params[5], P, PET, T, Q, A, S, R, G, Etat)

    nse = GR4J.calculate_nse(Q_obs, Q_sim, warmup_days=0)
    print(f"NSE on Validation Set: {nse:.4f}")


    #"""