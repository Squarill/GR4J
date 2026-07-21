import ee
import json
from config import Paths
import numpy as np
import os
import time
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

class ExporterService():
    def __init__(self, project_name:str):
        self.project_name = project_name
    
    def Authenticate(self):
        print("Connecting your Google account to the system.")
        ee.Authenticate()
        print("Connected.")
        pass
    
    def deAuthenticate(self):
        print("Disconnecting your Google account from the system.")
        credentials_path = os.path.expanduser("~/.config/earthengine/credentials")
        if os.path.exists(credentials_path) != True:
            print("No credentials found to be deleted, already non-authenticated.")
            return
        os.remove(credentials_path)
        print("Disconnected.")

    def export(self, geojson_path, start_date:str, end_date:str, variables, output_path):
        print("Exporting data from Google Earth Engine.")
        #geojson_path = geojson_path.with_suffix(".geojson")
        #output_path = output_path.with_suffix(".npz")

        log = []

        start_year = int(start_date[:4])
        end_year = int(end_date[:4])

        start_date = np.datetime64(start_date, "D")
        end_date = np.datetime64(end_date, "D")

        date_list = [str(start_date)]
        if end_year > start_year + 1:
            for i in range(start_year + 1, end_year+1):
                date_list.append(str(i)+"-01-01")

        if str(end_date+1) not in date_list:
            date_list.append(str(end_date+1))

        ee.Initialize(project=self.project_name)

        with open(geojson_path, "r") as f:
            data = json.load(f)
            area = None
            if data.get("type") == "FeatureCollection":
                log.append("QGIS")
                geojson = ee.FeatureCollection(data)
                geometry = geojson.geometry()
            else:
                log.append("GRDC")
                data_dict = data.get("features")[0]
                attributes = data_dict.get("attributes")
                if attributes:
                    area = attributes["area"]
                polygon = data_dict.get("geometry").get("rings")
                geometry = ee.Geometry.Polygon(polygon)

        yield log
        time.sleep(1)

        def extract_stats(image):
            stats = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=9000,
                maxPixels=1e9
            )
            return ee.Feature(None, stats.set('date', image.date().format('YYYY-MM-dd')))
        
        DATA_DICT = {}
        for variable in variables:
            DATA_DICT[variable] = []
        DATA_DICT["DATES"] = []
        DATA_DICT["variables"] = variables

 
        for i in range(len(date_list)-1):
            text = f"Collecting: {date_list[i]} to {date_list[i+1]}"
            log.append(text)
            yield log
            dataset = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
                .filterDate(date_list[i], date_list[i+1]) \
                .filterBounds(geometry) \
                .select(variables)

            fc = dataset.map(extract_stats)
            for data_cluster in fc.getInfo()["features"]:
                properties = data_cluster["properties"]
                date = properties["date"]
                DATA_DICT["DATES"].append(np.datetime64(date, "D"))
                for variable in variables:
                    DATA_DICT[variable].append(properties[variable])
            text = f"Collected: {date_list[i]} to {date_list[i+1]}"
            log.append(text)
            yield log
        
        if area:
            DATA_DICT["AREA"] = area
        
        np.savez(file=output_path, **DATA_DICT)
        log.append("END")
        yield log

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
    exporter_service = ExporterService("bratislava-danube-river")
    exporter_service.Authenticate()
    #a = exporter_service.export(Paths.DATASET/"stationbasins.geojson", "2001-02-01", "2007-01-05",["total_precipitation_sum"], Paths.DATASET/"TEST.npz")
    a = exporter_service.export(Paths.DATASET/"Briance.geojson", "2001-02-01", "2007-01-05",["total_precipitation_sum"], Paths.DATASET/"TEST.npz")
    for x in a:
        print(x)
    #exporter_service.deAuthenticate()
