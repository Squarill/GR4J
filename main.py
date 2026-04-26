import numpy as np
import json
import matplotlib.pyplot as plt

import GR4J_Model as G
from DE_Optim import Optimizer
import DataHandler as DH
from Paths import Paths


if __name__ == "__main__":
    """
    DH.create_data_npz_only_nc(start_year=1970, end_year=2000, file_name="1970-2000-calibration.npz")
    DH.create_data_npz_only_nc(start_year=2000, end_year=2017, file_name="2001-2017-validation.npz")

    bounds = [(0, 2000), (-10, 10), (0, 300), (1.1, 15.0)]
    A = 603.09 #km²

    npz_data = np.load(Paths.DATASET / "1970-2000-calibration.npz")
    P = npz_data["P"].astype(np.float64)
    PET = npz_data["PET"].astype(np.float64)
    Q = npz_data["Q"].astype(np.float64)

    NUMBA_DATA = [P, PET, Q]

    Op = Optimizer(A, bounds=bounds, NUMBA_DATA=NUMBA_DATA, maxiter=150, popsize=15, cpu_count=-1)
    best_params = Op.optimize(f = Op.objective_function_GR4J_Numba)
    npz_data = np.load(Paths.DATASET / "2001-2017-validation.npz")
    P = npz_data["P"].astype(np.float64)
    PET = npz_data["PET"].astype(np.float64)
    Q = npz_data["Q"].astype(np.float64)
    
    
    NUMBA_DATA = [P, PET, Q]
    
    Q_obs, Q_sim = G.GR4J_Numba(best_params[0], best_params[1], best_params[2], best_params[3],P, PET, Q, A)
    nse = G.calculate_nse_numba(Q_obs, Q_sim)
    print(f"NSE on Validation Set: {nse:.4f}")

    obs_plot = Q_obs[-730:]
    sim_plot = Q_sim[-730:]
    days = range(len(obs_plot))

    plt.figure(figsize=(12, 6))

    plt.plot(days, obs_plot, label="Observed", color="black", linewidth=1.5)

    plt.plot(days, sim_plot, label="Simulated", color="red", linestyle="--", linewidth=1.2)

    plt.title(f"Briance Catchment - Last two years (2016-2017) (NSE: {nse:.4f})")
    plt.xlabel("Day (time)")
    plt.ylabel("Discharge (mm/day)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
    """