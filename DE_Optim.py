from scipy.optimize import differential_evolution
import GR4J_Model as G
import time
from Paths import Paths

class Optimizer():
    def __init__(self, A:float, bounds:list, NUMBA_DATA:list = None, DATA = None, maxiter: int = 100, popsize: int = 15, tol :float = 0, atol : float = 0, cpu_count : int = 1):

        self.A = A
        self.bounds = bounds
        self.NUMBA_DATA = NUMBA_DATA    #[P, PET, Q_obs]
        self.DATA = DATA

        self.maxiter = maxiter
        self.popsize = popsize
        self.tol = tol
        self.atol = atol
        self.cpu_count = cpu_count
        
    def objective_function_GR4J_Numba(self, params):
        X1, X2, X3, X4 = params

        Q_obs, Q_sim, S, R = G.GR4J_Numba(X1, X2, X3, X4, self.NUMBA_DATA[0], self.NUMBA_DATA[1], self.NUMBA_DATA[2], A=self.A)

        nse = G.calculate_nse(Q_obs, Q_sim)

        return 1 - nse

    def objective_function_GR4J(self, params):
        """
        DEPRECATED! DO NOT USE THIS OBJECTIVE FUNCTION.
        """
        X1, X2, X3, X4 = params

        Q_obs, Q_sim, S, R = G.GR4J(X1, X2, X3, X4, self.DATA, A=self.A)

        nse = G.calculate_nse(Q_obs, Q_sim)

        return 1 - nse

    def optimize(self, f = None):
        if f == None:
            f = self.objective_function_GR4J_Numba

        print("Optimization with DE algorithm has been started.\nParameters will be calibrated.")
        #n_workers = int(os.environ.get("SLURM_CPUS_PER_TASK", os.cpu_count()))     will get you the max possible number of cores. If something goes wrong with the self.cpu_count, put this as workers = n_workers below.
        a = time.time()
        result = differential_evolution(
            f,
            self.bounds,
            maxiter=self.maxiter,
            popsize=self.popsize,
            tol=self.tol,
            atol=self.atol,
            disp=True,
            workers=self.cpu_count
        )
        print("Calibration has been succesfully done.")
        print(f"Total time elapsed: {(time.time()-a):.2f} seconds")
        print(f"Found best NSE: {(1-result.fun):.4f}\n")
        print("Found best parameters:\n")
        best_params = []
        for i in range(len(self.bounds)):
            print(f"X{i+1} = {result.x[i]:.2f}")
            best_params.append(result.x[i])
        return best_params


if __name__ == "__main__":
    pass
