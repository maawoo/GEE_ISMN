import pandas as pd
import numpy as np


def ts_filter(data_dict):
    """Filters the ISMN data by comparing the timestamp of each soil
    moisture measurement with the recording time of each Sentinel-1
    backscatter value from ascending & descending orbits.
    Only soil moisture values that were measured right before the
    S-1 datapoint are copied into a new dataframe. This function also checks
    for duplicate Sentinel-1 timestamps. In case of duplicates, only the
    first entry will be used.

    :param data_dict: Dictionary that was created/modified by using the
    function get_s1_backscatter(). Must contain a dataframe for the ISMN soil
    moisture data and dataframes for the Sentinel-1 backscatter data
    (descending & ascending orbits) for each dictionary key.
        :type: Dictionary

    :return: Dictionary with added dataframe that contains the filtered soil
    moisture and backscatter data.
    """

    def _filter_s1_desc(data_dict_desc):

        for key in data_dict_desc.keys():
            if data_dict_desc[key][6] is None:
                data_dict_desc[key].append(None)
                continue
            else:
                copy_sm = []
                plotdata = []
                timeseries_s1 = data_dict_desc[key][6]
                timeseries_sm = data_dict_desc[key][2]
                for timestamp in timeseries_sm.index:
                    copy_sm.append(timestamp)

                last_timestamp = None
                for timestamp in timeseries_s1.index:
                    if last_timestamp == timestamp:
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
                                if isinstance(timeseries_s1.at[timestamp, "VH"],
                                              np.ndarray) \
                                else timeseries_s1.at[timestamp, "VH"],
                            "VV_desc": timeseries_s1.at[timestamp, "VV"][0] \
                                if isinstance(timeseries_s1.at[timestamp, "VV"],
                                              np.ndarray) \
                                else timeseries_s1.at[timestamp, "VV"],
                            "t_sm": copy_sm[result].tz_localize(None),
                            "sm": timeseries_sm.at[copy_sm[result], "soil moisture"]
                        }

                        plotdata.append(record)
                        copy_sm = copy_sm[result:]

                data_dict_desc[key].append(pd.DataFrame(data=plotdata, dtype=np.float))

        return data_dict

    def _filter_s1_asc(data_dict_asc):

        for key in data_dict_asc.keys():
            if data_dict_asc[key][7] is None:
                data_dict_asc[key].append(None)
                continue
            else:
                copy_sm = []
                plotdata = []
                timeseries_s1 = data_dict_asc[key][7]
                timeseries_sm = data_dict_asc[key][2]
                for timestamp in timeseries_sm.index:
                    copy_sm.append(timestamp)

                last_timestamp_asc = None
                for timestamp in timeseries_s1.index:
                    if last_timestamp_asc == timestamp:
                        continue
                    last_timestamp_asc = timestamp
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

                data_dict_asc[key].append(pd.DataFrame(data=plotdata, dtype=np.float))

        return data_dict

    _filter_s1_desc(data_dict)
    _filter_s1_asc(data_dict)

    return data_dict

