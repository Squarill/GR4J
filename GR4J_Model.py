import math as mt
from Paths import Paths as Paths
import numpy as np
from numba import njit

def GR4J(X1, X2, X3, X4, DATA, A) -> tuple: # Will return (Q_obs:list, Q_sim:list)
    """
    DEPRECATED! DO NOT USE THIS FUNCTION.
    """
    S = 0.6 * X1    #Soil Moisture (mm)
    R = 0.7 * X3    #Route Moisture (mm)

    SH1:list[float] = []
    for t in range(mt.ceil(X4) + 1):
        if t <= 0:
            SH1.append(0)
        elif t < X4:
            SH1.append((t/X4)**2.5)
        else:
            SH1.append(1)

    SH2:list[float] = []
    for t in range(mt.ceil(2*X4) + 1):
        if t <= 0:
            SH2.append(0)
        elif t < X4:
            SH2.append(0.5 * (t/X4)**2.5)
        elif t >= X4 and t < 2*X4:
            SH2.append(1 - 0.5 * (2 - t/X4)**2.5)
        else:
            SH2.append(1)

    UH1 = []
    for j in range(1, len(SH1)):
        UH1.append(SH1[j] - SH1[j-1])

    UH2 = []
    for j in range(1, len(SH2)):
        UH2.append(SH2[j] - SH2[j-1])

    ## GR4J

    Pr1 = []
    Pr9 = []
    Q_sim = []
    Q_obs = []
    for date,values in DATA.items():
        P = values[0]
        PET = values[1]
        Q_real = values[3] * 86.4 / A

        if P > PET:
            Pn = P - PET
            En = 0
        else:
            Pn = 0
            En = PET - P

        Ps, Es = 0, 0

        if Pn > 0:
            Ps = (X1 * (1 - (S/X1)**2) * mt.tanh(Pn/X1)) / (1 + (S/X1) * mt.tanh(Pn/X1))
        
        if En > 0:
            Es = (S * (2 - S/X1) * mt.tanh(En/X1)) / (1 + (1 - S/X1) * mt.tanh(En / X1))
        
        S = S - Es + Ps

        Perc = S * (1 - (1 + (4*S / (9*X1))**4)**(-1/4))

        S = S - Perc

        Pr = Pn - Ps + Perc

        Pr9.insert(0, Pr * 0.9)
        if len(Pr9) > len(UH1):
            Pr9.pop() 
        
        Pr1.insert(0, Pr * 0.1)
        if len(Pr1) > len(UH2):
            Pr1.pop() 
        
        Q9 = 0
        for i in range(len(Pr9)):
            Q9 += Pr9[i] * UH1[i]
        
        Q1 = 0
        for i in range(len(Pr1)):
            Q1 += Pr1[i] * UH2[i]
        
        F = X2 * (R/X3) ** (7/2)

        R = R + Q9 + F
        R = 0 if R < 0 else R

        Qr = R * (1 - (1 + (R/X3)**4)**(-1/4))

        R = R - Qr

        Qd = max(0, Q1 + F)
        Q = Qr +Qd
        Q_sim.append(Q)
        Q_obs.append(Q_real)
    
    return (Q_obs, Q_sim)

@njit(cache=True)
def GR4J_Numba(X1, X2, X3, X4, P, PET, Q_raw, A, S_init = None, R_init=None):
    """
    Parameters
    ----------
    X1    : float    – Soil moisture capacity (mm)
    X2    : float    – Groundwater exchange coefficient (mm/day)
    X3    : float    – Routing store capacity (mm)
    X4    : float    – Unit hydrograph time base (day)
    P     : ndarray  – Precipitation array(mm/day)
    PET   : ndarray  – Potential evapotranspiration array (mm/day)
    Q_raw : ndarray  – Observed discharge (m³/s)
    A     : float    – Catchment area (km²)

    Returns
    -------
    (Q_obs, Q_sim, S, R) : tuple[ndarray, ndarray, float, float]
    """
    n = len(P)
    Q_obs = Q_raw * (86.4 / A)  # m³/s → mm/day

    if S_init == None:
        S = 0.6 * X1
    else:
        S = S_init
    if R_init == None:
        R = 0.7 * X3
    else:
        R = R_init

    nUH1 = mt.ceil(X4)
    nUH2 = mt.ceil(2 * X4)

    SH1 = np.zeros(nUH1 + 1)
    for t in range(nUH1 + 1):
        if 0 < t < X4:
            SH1[t] = (t / X4) ** 2.5
        elif t >= X4:
            SH1[t] = 1.0

    SH2 = np.zeros(nUH2 + 1)
    for t in range(nUH2 + 1):
        if 0 < t < X4:
            SH2[t] = 0.5 * (t / X4) ** 2.5
        elif X4 <= t < 2 * X4:
            SH2[t] = 1 - 0.5 * (2 - t / X4) ** 2.5
        elif t >= 2 * X4:
            SH2[t] = 1.0

    UH1 = np.empty(nUH1)
    for j in range(nUH1):
        UH1[j] = SH1[j+1] - SH1[j]

    UH2 = np.empty(nUH2)
    for j in range(nUH2):
        UH2[j] = SH2[j+1] - SH2[j]

    Pr9_buf = np.zeros(nUH1)
    Pr1_buf = np.zeros(nUH2)

    Q_sim = np.empty(n)

    for i in range(n):
        Pn = P[i] - PET[i]
        En = -Pn
        if Pn < 0:
            Pn = 0.0
        if En < 0:
            En = 0.0

        Ps = 0.0
        Es = 0.0

        if Pn > 0:
            tnh = mt.tanh(Pn / X1)
            Ps = (X1 * (1 - (S/X1)**2) * tnh) / (1 + (S/X1) * tnh)

        if En > 0:
            tnh = mt.tanh(En / X1)
            Es = (S * (2 - S/X1) * tnh) / (1 + (1 - S/X1) * tnh)

        S += Ps - Es
        Perc = S * (1 - (1 + (4*S / (9*X1))**4) ** (-0.25))
        S -= Perc

        Pr = Pn - Ps + Perc

        for k in range(nUH1 - 1, 0, -1):
            Pr9_buf[k] = Pr9_buf[k-1]
        Pr9_buf[0] = Pr * 0.9

        for k in range(nUH2 - 1, 0, -1):
            Pr1_buf[k] = Pr1_buf[k-1]
        Pr1_buf[0] = Pr * 0.1

        Q9 = 0.0
        for k in range(nUH1):
            Q9 += Pr9_buf[k] * UH1[k]

        Q1 = 0.0
        for k in range(nUH2):
            Q1 += Pr1_buf[k] * UH2[k]

        F = X2 * (R / X3) ** 3.5
        R += Q9 + F
        if R < 0:
            R = 0.0

        Qr = R * (1 - (1 + (R / X3)**4) ** (-0.25))
        R -= Qr

        Qd = Q1 + F
        if Qd < 0:
            Qd = 0.0

        Q_sim[i] = Qr + Qd

    return Q_obs, Q_sim, S, R

def calculate_nse(q_obs, q_sim, warmup_days:int = 1460):
    obs = np.asarray(q_obs[warmup_days:])
    sim = np.asarray(q_sim[warmup_days:])
    
    mask = obs >= 0
    obs = obs[mask]
    sim = sim[mask]

    mean_obs = np.mean(obs)
    numerator = np.sum((obs - sim) ** 2)
    denominator = np.sum((obs - mean_obs) ** 2)
    
    nse = 1 - (numerator / denominator)
    return nse

if __name__ == "__main__":

    pass