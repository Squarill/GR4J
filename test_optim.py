from scipy.optimize import differential_evolution
from GR4J_Model import GR4J_CemaNeige_Numba, GR4J_Numba, calculate_nse_numba
import time
from config import Paths
import numpy as np
from numba import njit

@njit(cache=True)
def o_f_GR4J_CN_NSE(params, P, PET, T, Q_obs, A, warmup_days=1460):
    X1 = params[0]
    X2 = params[1]
    X3 = params[2]
    X4 = params[3]
    X5 = params[4]
    X6 = params[5]
    Q_obs_out, Q_sim, S, R, G, eTG = GR4J_CemaNeige_Numba(X1, X2, X3, X4, X5, X6, P, PET, T, Q_obs, A)
    nse = calculate_nse_numba(Q_obs_out, Q_sim, warmup_days=warmup_days)
    return 1 - nse

@njit(cache=True)
def o_f_GR4J_NSE(params, P, PET, Q_obs, A, warmup_days=1460):
    X1 = params[0]
    X2 = params[1]
    X3 = params[2]
    X4 = params[3]
    Q_obs_out, Q_sim, S, R = GR4J_Numba(X1, X2, X3, X4, P, PET, Q_obs, A)
    nse = calculate_nse_numba(Q_obs_out, Q_sim, warmup_days=warmup_days)
    return 1 - nse

def optimize(f:callable, data:dict, bounds, maxiter=100, popsize=15, tol=0, atol=0, cpu_count=-1, warmup_days=1460):
    """
    data = {
        "P" : np.ndarray,
        "PET" : np.ndarray,
        "T" : np.ndarray,
        "Q_obs" : np.ndarray,
        "A" : float
    }
    """
    a = time.time()

    if f == o_f_GR4J_CN_NSE:
        P = data["P"]
        PET = data["PET"]
        T = data["T"]
        Q_obs = data["Q"]
        A = data["AREA"]
        arguments = (P, PET, T, Q_obs, A, warmup_days)
    elif f == o_f_GR4J_NSE:
        P = data["P"]
        PET = data["PET"]
        Q_obs = data["Q"]
        A = data["AREA"]
        arguments = (P, PET, Q_obs, A, warmup_days)

    result = differential_evolution(
        f,
        bounds,
        maxiter=maxiter,
        popsize=popsize,
        tol=tol,
        atol=atol,
        callback=None,
        disp=True,
        workers=cpu_count,
        args = arguments,
        polish = False
    )
    print("Calibration has been succesfully done.")
    print(f"Total time elapsed: {(time.time()-a):.2f} seconds")
    print(f"Found best NSE: {(1-result.fun):.4f}\n")
    print("Found best parameters:\n")
    best_params = []
    for i in range(len(bounds)):
        print(f"X{i+1} = {result.x[i]:.2f}")
        best_params.append(float(result.x[i]))
    return best_params

if __name__ == "__main__":
    pth = "C:\\Users\\emrec\\OneDrive\\Masaüstü\\Test\\Resse\\cal.npz"
    data = np.load(pth)
    P = data["P"]
    PET = data["PET"]
    T = data["T"]
    Q_obs = data["Q"]
    A = data["AREA"]
    bounds = [
        (10.0, 2000.0), 
        (-10.0, 10.0),
        (1.0, 500.0),
        (1.0, 5.0),
        (0.01, 1.0),
        (0.0, 20.0)
    ]

    best_params = optimize(o_f_GR4J_CN_NSE, P, PET, T, Q_obs, A, bounds)
    print(best_params)