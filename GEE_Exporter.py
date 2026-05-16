import ee
import json
from config import Paths
import numpy as np


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
    
    def deAuthenticate():
        print("Disconnecting your Google account from the system.")

    def export(self):
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

        dataset = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
            .filterDate(self.start_date, self.end_date) \
            .select(self.variables)

        fc = dataset.map(extract_stats)
        
        #Preparing the data dict
        DATA_DICT = {}
        for variable in self.variables:
            DATA_DICT[variable] = []
        DATA_DICT["DATES"] = []
        

        for data_cluster in fc.getInfo()["features"]:
            properties = data_cluster["properties"]
            date = properties["date"]
            DATA_DICT["DATES"].append(date)
            for variable in self.variables:
                DATA_DICT[variable].append(properties[variable])

        np.savez(file=self.output_path, **DATA_DICT)


"""
ee.Authenticate()
ee.Initialize(project="bratislava-danube-river")

with open("Bratislava.geojson", "r") as f:
    geojson = ee.FeatureCollection(json.load(f))
area = geojson.geometry()


dataset = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
    .filterDate('2000-01-01', '2021-01-01') \
    .select([
        'total_precipitation_sum',
        'temperature_2m',
        'potential_evaporation_sum'
    ])

def extract_stats(image):
    stats = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=area,
        scale=9000,
        maxPixels=1e9
    )
    return ee.Feature(None, stats.set('date', image.date().format('YYYY-MM-dd')))

fc = dataset.map(extract_stats)

# Drive'a gönder
task = ee.batch.Export.table.toDrive(
    collection=fc,
    description='era5_bratislava_2001_2020',
    folder='GEE_Exports',          # Drive'da otomatik oluşturur
    fileNamePrefix='era5_bratislava_withgeojson_2001_2020',
    fileFormat='CSV'
)
task.start()
print("Task baslatildi:", task.id)

# Kod içinde kontrol
import time

while task.active():
    print("Durum:", task.status()['state'])
    time.sleep(10)

print("Tamamlandi:", task.status()['state'])
"""

if __name__ == "__main__":
    exporter = GEE_Exporter("bratislava-danube-river", Paths.DATASET/"Bratislava.geojson", "2001-01-01", "2002-12-31", ["total_precipitation_sum", "temperature_2m", "potential_evaporation_sum"])
    exporter.Authenticate()
    exporter.export()

    #Testing
    npzfile = np.load(Paths.DATASET / "GEE_EXPORT_DATA.npz")
    print(npzfile["DATES"][0], npzfile["DATES"][-1])
    print(npzfile["total_precipitation_sum"][0], npzfile["total_precipitation_sum"][-1])
    print(npzfile["temperature_2m"][0], npzfile["temperature_2m"][-1])
    print(npzfile["potential_evaporation_sum"][0], npzfile["potential_evaporation_sum"][-1])

    pass