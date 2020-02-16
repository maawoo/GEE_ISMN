import csv
from geojson import Point, Feature, FeatureCollection, dump
from fun import preprocess

preprocess.setup_dir()

## List all .stm files
sm_files = preprocess.get_sm_files()

## Filter soil moisture files by measurement depth
depth = "0.05"
sm_files_filt = preprocess.filter_files(sm_files, depth)


coord_1 = []
coord_2 = []
station = []
features = []

for i in sm_files_filt:
    checked_file_1 = open(i)
    header_elements, filename_elements = preprocess.get_info_from_file(i)
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
