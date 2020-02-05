import matplotlib.pyplot as plt
import geopandas as gpd
import ee
from fun import ee_functions

#############################################
# Initiate GEE & ask for user input

#ee.Authenticate()
ee.Initialize()

while True:
    try:
        box_yn = int(input("Do you want to extract backscatter values for "
                           "the pixel coordinate (input: 0) or "
                           "calculate the mean backscatter value for a box "
                           "surrounding the pixel coordinate (input: "
                           "1)?"))
    except ValueError:
        print("Sorry, I didn't understand that.")
        continue

    if box_yn not in (0, 1):
        print("Not an appropriate choice.")
        continue

    elif box_yn == 1:
        try:
            box_size = int(input("Please enter a box size (e.g. 20 is equal "
                                 "to a box of size 20 by 20 meters):"))
        except ValueError:
            print("Sorry, I didn't understand that.")
            continue
        else:
            break

    else:
        break

#############################################
# Import and process location data

geo = gpd.read_file('./data/coordinates_2.geojson')

if box_yn == 1:
    ee_geo = ee_functions.process_geojson(geo, box_yn, box_size)
else:
    ee_geo = ee_functions.process_geojson(geo, box_yn)

#############################################
# Import land cover data and filter the locations

ee_geo_filt = ee_functions.lc_filter(ee_geo)
print(str(len(ee_geo_filt)) +
      " from " + str(len(ee_geo)) +
      " locations left, after applying the land cover filter.")

#############################################
# Load and filter Sentinel-1 image collection

img_coll = ee_functions.get_image_collection(ee_geo_filt)

#############################################
# Extract backscatter data for each location

# Point
for key in img_coll.keys():
    s1_data = ee_functions.time_series_of_a_point(img_coll[key][1], img_coll[key][0])
    s1_data.reset_index().plot(x='Dates', y='VH')
    plt.savefig("./figs/" + str(key) + ".png")
    plt.close()

# Region
for key in img_coll.keys():
    s1_data = ee_functions.time_series_of_a_region(img_coll[key][1], img_coll[key][0])
    s1_data.reset_index().plot(x='Dates', y='VV')
    plt.savefig("./figs/" + str(key) + "_sq50.png")
    plt.close()


#s1_data = ee_functions\
#    .time_series_of_a_point(img_coll["geo_1"][1], img_coll["geo_1"][0])
#s1_data

#s1_data.reset_index().plot(x='Dates', y='VH')
#s1_data.reset_index().plot(x='Dates', y='VV')
#plt.show()
