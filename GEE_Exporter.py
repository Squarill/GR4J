import ee
import json
from config import Paths
import numpy as np
import os

class GEE_Exporter():
    def __init__(self, project_name:str, geojson_path:str, start_date:str, end_date:str, variables:list, output_path:str = Paths.DATASET / "GEE_EXPORT_DATA.npz"):
        self.project_name = project_name
        self.geojson_path = geojson_path.with_suffix(".geojson")
        self.start_date = start_date
        self.end_date = end_date
        self.variables = variables
        self.output_path = output_path.with_suffix(".npz")


    def Authenticate(self):
        print("Connecting your Google account to the system.")
        ee.Authenticate()
        print("Connected.")
    
    def deAuthenticate(self):
        print("Disconnecting your Google account from the system.")
        credentials_path = os.path.expanduser("~/.config/earthengine/credentials")
        if os.path.exists(credentials_path) != True:
            print("No credentials found to be deleted, already non-authenticated.")
            return
        os.remove(credentials_path)
        print("Disconnected.")

    def export(self):
        print("Exporting data from Google Earth Engine.")
        def extract_stats(image):
            stats = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=area,
                scale=9000,
                maxPixels=1e9
            )
            return ee.Feature(None, stats.set('date', image.date().format('YYYY-MM-dd')))
        
        ee.Initialize(project=self.project_name)
        with open(self.geojson_path, "r") as f:
            geojson = ee.FeatureCollection(json.load(f))
        area = geojson.geometry()
        
        #Preparing the data dict
        DATA_DICT = {}
        for variable in self.variables:
            DATA_DICT[variable] = []
        DATA_DICT["DATES"] = []
        DATA_DICT["variables"] = self.variables
        
        start = int(self.start_date[:4])
        end = int(self.end_date[:4])
        print(start, end)
        for year in range(start, end + 1):
            print(f"Collecting: {year}-01-01 to {year + 1}-01-01")
            dataset = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
                .filterDate(f"{year}-01-01", f"{year + 1}-01-01") \
                .filterBounds(area) \
                .select(self.variables)

            fc = dataset.map(extract_stats)

            for data_cluster in fc.getInfo()["features"]:
                properties = data_cluster["properties"]
                date = properties["date"]
                DATA_DICT["DATES"].append(date)
                for variable in self.variables:
                    DATA_DICT[variable].append(properties[variable])

        np.savez(file=self.output_path, **DATA_DICT)

        print(f"Data saved to {self.output_path}.")
        print(f"Data start date: {DATA_DICT['DATES'][0]}")
        print(f"Data end date: {DATA_DICT['DATES'][-1]}")
        print("Exporting completed.")

if __name__ == "__main__":
    """
    exporter = GEE_Exporter("bratislava-danube-river", Paths.DATASET/"Bratislava.geojson", "2001-01-01", "2002-12-31", ["total_precipitation_sum", "temperature_2m", "potential_evaporation_sum"])
    exporter.Authenticate()
    exporter.export()

    #Testing
    npzfile = np.load(Paths.DATASET / "GEE_EXPORT_DATA.npz")
    print(npzfile["DATES"][0], npzfile["DATES"][-1])
    print(npzfile["total_precipitation_sum"][0], npzfile["total_precipitation_sum"][-1])
    print(npzfile["temperature_2m"][0], npzfile["temperature_2m"][-1])
    print(npzfile["potential_evaporation_sum"][0], npzfile["potential_evaporation_sum"][-1])
    """