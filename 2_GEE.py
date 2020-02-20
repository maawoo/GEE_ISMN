import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import ee
from ismn import readers as ismn
from GEE_ISMN import setup_pkg as pkg
from GEE_ISMN import earthengine as earth

user_input = pkg.setup_pkg()

#############

test_dict = {}
test_file1 = "./data/ISMN_Filt/" \
             "PBO-H2O_PBO-H2O_BILLINGSAP_sm_0.000000_0" \
             ".050000_GPS_20140401_20191015.stm "
test_file2 = "./data/ISMN_Filt/RSMN_RSMN_Dumbraveni_sm_0.000000_0" \
             ".050000_5TM_20140401_20191015.stm"
data1 = ismn.read_data(test_file1)
data2 = ismn.read_data(test_file2)

test_dict[data1.network + "-" + data1.sensor + "-" + data1.station] = [
    data1.latitude, data1.longitude, data1.data]
test_dict[data2.network + "-" + data2.sensor + "-" + data2.station] = [
    data2.latitude, data2.longitude, data2.data]

test_dict_2 = earth.lc_filter(test_dict, user_input)
test_dict_3 = earth.get_image_collection(test_dict_2)
key = 'RSMN-5TM-Dumbraveni'

s1_data = earth.time_series_of_a_point(test_dict_3[key][4], test_dict_3[
    key][3])

test_dict_3[key].append(s1_data)

test_dict_3[key][6]

#############

# Point
for key in img_coll.keys():
    s1_data = ee.time_series_of_a_point(img_coll[key][1], img_coll[key][0])
    s1_data.reset_index().plot(x='Dates', y='VH')
    # plt.savefig("./figs/" + str(key) + ".png")
    # plt.close()

# Region
for key in img_coll.keys():
    s1_data = ee.time_series_of_a_region(img_coll[key][1], img_coll[key][0])
    s1_data.reset_index().plot(x='Dates', y='VV')
    plt.savefig("./figs/" + str(key) + "_sq50.png")
    plt.close()

s1_data = ee.time_series_of_a_point(img_coll["geo_1"][1], img_coll["geo_1"][0])
s1_data

# s1_data.reset_index().plot(x='Dates', y='VH')
# plt.show()
