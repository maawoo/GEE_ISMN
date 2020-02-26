import pandas as pd
import numpy as np


# data_filter(data_dict, filter=None)
#   - filter:
#       - (Default) filter=None: Nur die ISMN-Messung unmittelbar
#       vor S1-Aufnahme
#       - filter="mean": Durchschnitt der ISMN-Messungen bilden
#       (müssen nur überlegen was mehr Sinn macht. Entweder zB 3 Messungen vor
#       S1-Aufnahme oder villt 2 Messungen davor und 1 danach?)
#   - Output: Neuer dataframe in der dict (time / ismn_data / s1_data)


def filter_s1_desc(data_dict):
    """ lazy evaluation: if the entry in VH is an array set it as the first value of that array, set the normal value
        :param
        :type

        :return:
        """
    copy_sm = []
    plotdata = []
    for key in data_dict.keys():
        timeseries_s1 = data_dict[key][6]
        timeseries_sm = data_dict[key][2]
        for timestamp in timeseries_sm.index:
            copy_sm.append(timestamp)

        last_timestamp = None
        for timestamp in timeseries_s1.index:
            if (last_timestamp == timestamp):
                continue
            last_timestamp = timestamp
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
                    "t_s1_desc": timestamp,
                    "VH_desc": timeseries_s1.at[timestamp, "VH"][0] \
                        if isinstance(timeseries_s1.at[timestamp, "VH"], np.ndarray) \
                        else timeseries_s1.at[timestamp, "VH"],
                    "VV_desc": timeseries_s1.at[timestamp, "VV"][0] \
                        if isinstance(timeseries_s1.at[timestamp, "VV"], np.ndarray) \
                        else timeseries_s1.at[timestamp, "VV"],
                    "t_sm": copy_sm[result].tz_localize(None),
                    "sm": timeseries_sm.at[copy_sm[result], "soil moisture"]
                }
                plotdata.append(record)
                copy_sm = copy_sm[result:]
        data_dict[key].append(pd.DataFrame(data=plotdata, dtype=np.float))


def filter_s1_asc(data_dict):
    copy_sm = []
    plotdata = []
    for key in data_dict.keys():
        timeseries_s1 = data_dict[key][7]
        timeseries_sm = data_dict[key][2]
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
                    "t_s1_asc": timestamp,
                    "VH_asc": timeseries_s1.at[timestamp, "VH"][0] \
                        if isinstance(timeseries_s1.at[timestamp, "VH"], np.ndarray) \
                        else timeseries_s1.at[timestamp, "VH"],
                    "VV_asc": timeseries_s1.at[timestamp, "VV"][0] \
                        if isinstance(timeseries_s1.at[timestamp, "VV"], np.ndarray) \
                        else timeseries_s1.at[timestamp, "VV"],
                    "t_sm": copy_sm[result].tz_localize(None),
                    "sm": timeseries_sm.at[copy_sm[result], "soil moisture"]
                }
                plotdata.append(record)
                copy_sm = copy_sm[result:]

        data_dict[key].append(pd.DataFrame(data=plotdata, dtype=np.float))
