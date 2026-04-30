# GR4J Hydrological Model with Differential Evolution

This software implements the **GR4J model** using **NetCDF** data and the **Differential Evolution** algorithm for parameter calibration.

## 🚀 Getting Started

### 1. Create the Environment
Run the `setup.bat` file. This creates a virtual environment (`.venv`) to avoid system-wide changes. 
*Requires Python 3.8 or higher.*

### 2. Prepare the Data
> [!IMPORTANT]  
> **CDO (Climate Data Operators)** must be installed and added to your system PATH for this step.
Gather your data in the NetCDF (.nc) format and name them as follows:
- `pre.nc` (Precipitation)
- `pet.nc` (Evapotranspiration)
- `q.nc` (Discharge)

Also put these files in the NetCDF folder if you wish to automatically create the data.txt files.
Navigate to `Dataset\NetCDF` and run `prepare.bat`. This script converts NetCDF files into processed text data.
Do not forget that this method is just to create a standardized dataset. If you have another type of dataset, you might need a different method and it might require some new functions to strip data accordingly.

### 3. Execution
Use `run.bat` to execute the `main.py` script.

---

## 📊 Technical Details

### Unit Requirements
Ensure your input data follows these units:
- **Precipitation (P):** mm/day
- **PET:** mm/day
- **Discharge (Q):** m³/s
- **Catchment Area:** Must be provided in **km²** INSIDE the main.py file as a variable (e.g., Briance = 603.09 km²).

### Performance (Numba)
In `GR4J_Model.py`, the Numba-optimized function provides significant speedup for large datasets or long-term calibrations. 
*Note: Discharge (Q) is converted from m³/s to mm/day internally. Do NOT change anything about the units.*

## ⚠️ HPC Notice
The `.bat` files are designed for Windows. For Linux-based HPC environments, ensure you load the required Python modules and run the `.py` scripts directly using standard Linux commands or with a batch file.