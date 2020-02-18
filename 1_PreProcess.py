import csv
import glob
from geojson import Point, Feature, FeatureCollection, dump
from GEE_ISMN import setup_pkg as pkg
from GEE_ISMN import preprocess as prep

user_input = pkg.setup_pkg()

prep.data_handling()  # Uses 0.05 as default value to filter for measurement depth


#############################
## Funktion erstellen, die:
# 1. Alle .stm Daten aus dem "./data/ISMN_Filt" Order als dataframes importiert
# 2. Eine CSV Datei exportiert mit den Stationen und den jeweiligen
#    Koordinaten
# 3. Eine dictionary erstellt mit folgendem Aufbau:
#           - key       = Name der station
#           - val_1     = [lat, long]
#           - val_2     = Dataframe mit den Messungen
#                         (datum-zeit / Messwert / flag?)

coord_1 = []
coord_2 = []
station = []
features = []

sm_files_filt = [f for f in glob.glob("./data/ISMN_Filt/**/*_sm_*.stm",
                                      recursive=True)]

for i in sm_files_filt:
    checked_file_1 = open(i)
    header_elements, filename_elements = prep.get_info_from_file(i)
    coord_1.append(header_elements[3])
    coord_2.append(header_elements[4])
    station.append(
        header_elements[1] + "-" + header_elements[2] + "-" + header_elements[
            8])
    point = Point((float(header_elements[3]), float(header_elements[4])))
    features.append(Feature(geometry=point))

feature_collection = FeatureCollection(features)

with open('coordinates_2.geojson', 'w') as fb:
    dump(feature_collection, fb)

with open('stations.csv', 'w', newline='') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',')
    filewriter.writerow(station)
    filewriter.writerow(coord_1)
    filewriter.writerow(coord_2)
