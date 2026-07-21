import numpy as np

data = np.load("GEE_EXPORT_DATA_ERMENEK.npz")
print(data.files)

print(data["DATES"][0], type(data["DATES"][0]))

