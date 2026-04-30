This software uses GR4J model and NetCDF data type in order to create a successful hydrological model with the help of Differential Evolution algorithm for the given data.

Here are the steps to successfully use the software.

#1-) Create the environment
Run the setup.bat file. It will create the virtual environment in order to run the scripts. This is to avoid any changes in local Windows and can be skipped if the user already has the required libraries and sufficient Python version, preferably 3.8 or higher.

#2-) Create the data
In Dataset\NetCDF there is a file named 'prepare.bat'. This script will use the existing pre, pet, tavg and q NetCDF files to create data.txt files.
IMPORTANT: You need CDO (Climate Data Operators) in your environment variables/PATH. Otherwise, 'prepare.bat' will not be any of help.

The 'prepare.bat' script will create the neccessary pre_data.txt, pet_data.txt and q_data.txt files.

#3-) Run the scripts as you like
You can use 'run.bat' file to run the 'main.py' script in the virtual environment you created at the first step. There is a premade code for Briance branch of the Vienne catchment. After deleting the """ symbols at the start and at the end, it will create a model and show you the last 2 years' simulated and observed hydrographs. Of course you need to have the needed p, pet and q values and should have prepared them at the second step beforehand.

You can activate the virtual environment by yourself as well. Open the command prompt for this specific directory and run this command:
.venv\Scripts\activate
After this activation, you can call your scripts by just typing 'python your_script.py'.


WARNING: Although it works with the current data files, it should not be forgotten that this software uses these units for calculations.
P (Precipitation) = mm/day
PET (Potential Evapotranspiration) = mm/day
Q (Discharge) = m³/seconds

MOST IMPORTANTLY: You should have the Area value (in km²) for the catchment you wish to work on. This is not included in the given data files. It is 603.09 km² for Briance.

IMPORTANT: In the 'GR4J_Model.py', the Q value gets changed into mm/day INSIDE the functions. Do not change anything about Q values if you already have it as m³/s.

If you have any intention of running these scripts on any HPC, do not forget to have the required modules installed in it. These .bat files will NOT work on an HPC which probably is running on Linux.