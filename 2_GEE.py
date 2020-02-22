from ismn import readers as ismn
from GEE_ISMN import setup_pkg as pkg
from GEE_ISMN import earthengine as earth
# import matplotlib.pyplot as plt
# import pandas as pd
# import geopandas as gpd
# import ee

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

test_dict_3 = earth.get_s1_backscatter(test_dict_2)
timeseries_s1 = test_dict_3['RSMN-5TM-Dumbraveni'][6]
timeseries_sm = test_dict_3['RSMN-5TM-Dumbraveni'][2]
i = 1
copy_sm = []
plotdata = []
for timestamp in timeseries_sm.index:
    copy_sm.append(timestamp)

for timestamp in timeseries_s1.index:
    sm_series = None
    result = None
    for sm_timestamp_index in range(len(copy_sm)):
        loc = copy_sm[sm_timestamp_index].tz_localize(None)
        if loc > timestamp:
            result = sm_series
            break
        sm_series = sm_timestamp_index

    if result is not None:
        record = {
            "s1": {
                "t": timestamp,
                "VH": timeseries_s1.at[timestamp, "VH"],
                "VV": timeseries_s1.at[timestamp, "VV"]
            },
            "sm": {
                "t": copy_sm[result].tz_localize(None),
                "sm": timeseries_sm.at[copy_sm[result], "soil moisture"]
            }
        }
        plotdata.append(record)
        copy_sm = copy_sm[result:]
#    print(timestamp)
#    i = i + 1
#    if i == 10:
#        break



#############

# s1_data.reset_index().plot(x='Dates', y='VH')
# plt.show()
