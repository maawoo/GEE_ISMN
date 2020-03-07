import pandas as pd
import numpy as np


def filter_s1(data_dict):

    def filter_s1_desc(data_dict_desc):
        """ This function filters the ISMN data by comparing
        time of recording of ISMN and Sentinel-1 data from the
        Descending Orbit. Only ISMN data which were collected
        right before the Sentinel-1 data should be used.
        Also the function checks for double Sentinel-1 timestamps.
        In case of doubled Sentinel-1 dcenes for one timestamp,
        the first one will be choosen.
            :param data_dict_desc: dictionary which contains the following values:
                - Sentinel-1 timestamps of descending orbit
                - Sentinel-1 backscatter values (VH/VV) of descending orbit
                - ISMN timestamps
                - ISMN soil moisture values

            :type data_dict_desc: dictionary

            :return: a dataframe containing the Sentinel-1 Timestamps
            (t_s1_desc) and backscatter values (VH_desc & VV_desc) for the
            descending Orbit and the assigned ISMN soil moisture values (sm)
            and timestamps (t_sm)
            """

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
                data_dict_desc[key].append(pd.DataFrame(data=plotdata, dtype=np.float))
        return data_dict

    def filter_s1_asc(data_dict_asc):
        """ This function filters the ISMN Data by comparing
            time of recording of ISMN and Sentinel-1 data from the
            Ascending Orbit. Only ISMN Data which were collected
            right before the Sentinel-1 Data should be used.
            Also the function checks for double Sentinel-1 timestamps.
            In case of doubled Sentinel-1 Scenes for one timestamp,
            the first one will be choosen.
                :param data_dict_asc: dictionary which contains the following values:
                    - Sentinel-1 Timestamps of Ascending Orbit
                    - Sentinel-1 Backscatter Values (VH/VV) of Ascending Orbit
                    - ISMN Timestamps
                    - ISMN Soil moisture Values

                :type data_dict_asc: dictionary

                :return: a Dataframe containing the Sentinel-1 Timestamps
                (t_s1_asc) and Backscatter Values (VH_asc & VV_asc) for the
                descending Orbit and the assigned ISMN Soil moisture Values (sm)
                and Timestamps (t_sm)
                """

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
                    if (last_timestamp_asc == timestamp):
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

    filter_s1_desc(data_dict)
    filter_s1_asc(data_dict)

    return data_dict

