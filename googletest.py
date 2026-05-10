import ee
import json
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