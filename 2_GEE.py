import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from fun import ee_functions


# Initiate GEE & ask for user input
user_input = ee_functions.setup_ee()


# Import and process location data
geo = gpd.read_file('./data/coordinates_2.geojson')
ee_geo = ee_functions.process_geojson(geo, user_input)


# Import land cover data and filter the locations
ee_geo_filt = ee_functions.lc_filter(ee_geo)


# Load and filter Sentinel-1 image collection
img_coll = ee_functions.get_image_collection(ee_geo_filt)


# Extract backscatter data for each location
stations = pd.read_csv("./data/stations.csv")
stations

def ts_to_dict(img_collection, geo_list_filt):
    out_dict = {}

    stations = pd.read_csv("./data/stations.csv")


# Point
for key in img_coll.keys():
    s1_data = ee_functions.time_series_of_a_point(img_coll[key][1], img_coll[key][0])
    s1_data.reset_index().plot(x='Dates', y='VH')
    #plt.savefig("./figs/" + str(key) + ".png")
    #plt.close()

# Region
for key in img_coll.keys():
    s1_data = ee_functions.time_series_of_a_region(img_coll[key][1], img_coll[key][0])
    s1_data.reset_index().plot(x='Dates', y='VV')
    plt.savefig("./figs/" + str(key) + "_sq50.png")
    plt.close()

s1_data = ee_functions.time_series_of_a_point(img_coll["geo_1"][1], img_coll["geo_1"][0])
s1_data

#s1_data.reset_index().plot(x='Dates', y='VH')
#plt.show()