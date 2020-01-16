import numpy as np
import pandas as pd
import datetime
import matplotlib
import matplotlib.pyplot as plt
import geopandas as gpd
import ee
from fun import ee_functions

###################################################
## Initiate GEE & ask for user input

#ee.Authenticate()
ee.Initialize()

while True:
    try:
        box_yn = int(input("Do you want to extract backscatter values for the pixel coordinate (input: 0) or "
                           "calculate the mean backscatter value for a box surrounding the pixel coordinate (input: "
                           "1)?"))
    except ValueError:
        print("Sorry, I didn't understand that.")
        continue
    if box_yn not in (0, 1):
        print("Not an appropriate choice.")
        continue

    elif box_yn == 1:
        try:
            box_size = int(input("Please enter a box size (e.g. 20 is equal to a box of size 20 by 20 meters):"))
        except ValueError:
            print("Sorry, I didn't understand that.")
            continue
        else:
            break
    else:
        break

###################################################
## Import location data
test_json = gpd.read_file('./data/map.geojson')
print(test_json["geometry"])

## Use some test locations for now
geo1 = ee.Geometry.Point([11.469602842013614, 50.95131882751624])
geo2 = ee.Geometry.Point([15.469602842013614, 50.95131882751624])
geo3 = ee.Geometry.Point([-97.68473698802995, 35.43516091957335])
geo4 = ee.Geometry.Point([-94.4336613630228, 34.72741940848683])
geo5 = ee.Geometry.Point([-3.6611698418271317, 42.08709425769527])

geo_dict = {"geo1": geo1, "geo2": geo2, "geo3": geo3, "geo4": geo4, "geo5": geo5}

geo_dict_sq = {}
for key, value in geo_dict.items():
    geo_dict_sq[key + "_sq"] = value.buffer(box_size/2).bounds()

###################################################
## Import land cover data and filter the locations

geo_dict_filt = geo_dict.copy()
ee_functions.lc_filter(geo_dict_filt)

print(geo_dict_filt)

###################################################
## Load and filter Sentinel-1 image collection

test = getimagecoll(geo_dict_filt)
test.items()

###################################################
## Extract backscatter data for each location

test = time_series_of_a_point(test["geo5"][1], test["geo5"][0])
test

test.reset_index().plot(x='Dates', y='VH')
test.reset_index().plot(x='Dates', y='VV')
plt.show()