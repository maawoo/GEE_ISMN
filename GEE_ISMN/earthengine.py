import ee
import copy
import numpy as np
import pandas as pd
import datetime
import csv


def lc_filter(data_dict, input_dict, landcover_ids=None):
    """Adds GEE geometry objects to the data dictionary (data_dict) based on
    parameters in input_dict. The data dictionary is then filtered based on
    landcover IDs.

    :param data_dict: Dictionary containing ISMN data to be analysed.
    Output of preprocess.data_import().
        :type: Dictionary
    :param input_dict: Dictionary that was created via user input
    through setup_pkg(). Contains the following key/value pairs:
            - box_yn / int of either 0 or 1
                Depending on the value, either point objects (0) or polygons
                (1) with the station coordinate as the midpoint are returned.
            - box_size / any int > 0
                Defines the polygon size and will be used for the extraction of
                the mean backscatter of the defined region.
        :type: Dictionary
    :param landcover_ids: Landcover IDs based on the CGLS-LC100
    dataset (https://tinyurl.com/cgls-lc100).
    Default IDs are:
            40 = Cultivated and managed vegetation / agriculture
            60 = Bare / sparse vegetation
        :type: single int or list of int

    :return: The filtered version of the input dictionary "data_dict"
    """
    data_dict_copy = copy.deepcopy(data_dict)

    if landcover_ids is None:
        landcover_ids = [40, 60]

    elif type(landcover_ids) == int:
        landcover_ids = list(map(int, landcover_ids))

    elif type(landcover_ids) == list:
        landcover_ids = landcover_ids

    else:
        raise ValueError("The argument \"landcover_ids\" should be an integer "
                         "or a list of integers.\n For valid landcover IDs, "
                         "please refer to: https://tinyurl.com/cgls-lc100")

    data_dict_edit = _ee_geometries(data_dict_copy, input_dict)
    data_dict_filt = _ee_filter(data_dict_edit, landcover_ids)

    return data_dict_filt


def _ee_geometries(data_dict, input_dict):
    """Takes latitude & longitude from the the dictionary that
    contains the ISMN data (data_dict) and converts them to GEE geometry
    objects based on parameters in input_dict.

    For parameter description see: lc_filter()

    :return: data_dict with added EE geometry objects.
    """
    data_dict_copy = copy.deepcopy(data_dict)

    if input_dict["box_yn"] == 0:
        for key in data_dict_copy.keys():
            try:
                check = type(data_dict_copy[key][3]) == ee.geometry.Geometry
                if check:
                    pass
                else:
                    raise TypeError("Something is wrong. I didn't "
                                    "expect an object of type\n "
                                    + str(type(data_dict_copy[key][3])) +
                                    "here.")

            except IndexError:  # Nothing here, which is good!
                data_dict_copy[key].append(
                    ee.Geometry.Point(float(data_dict_copy[key][1]),
                                      float(data_dict_copy[key][0])))

    elif input_dict["box_yn"] == 1:
        for key in data_dict_copy.keys():
            try:
                check = type(data_dict_copy[key][3]) == ee.geometry.Geometry
                if check:
                    pass
                else:
                    raise TypeError("Something is wrong. I didn't expect "
                                    "an object of type\n "
                                    + str(type(data_dict_copy[key][3]))
                                    + "here.")

            except IndexError:  # Nothing here, which is good!
                data_dict_copy[key].append(
                    ee.Geometry.Point(float(data_dict_copy[key][1]),
                                      float(data_dict_copy[key][0]))
                        .buffer(input_dict["box_size"] / 2)
                        .bounds())
    else:
        raise ValueError("The variable box_yn should be"
                         " 0 (extract backscatter for pixel coordinates) \n "
                         "or 1 (extract mean backscatter for a bounding box). "
                         "\n Please run setup_pkg() again before continuing!")

    return data_dict_copy


def _ee_filter(data_dict, landcover_ids):
    """The landcover type of each location is checked based on the
    CGLS-LC100 dataset (https://tinyurl.com/cgls-lc100). The input
    dictionary ( data_dict) is then filtered based on provided landcover IDs
    (landcover_ids).

    For parameter description see: lc_filter()

    :return: Filtered version of data_dict.
    """
    data_dict_copy = copy.deepcopy(data_dict)
    valid_ids = landcover_ids
    data_dict_filt = {}
    lc_values = []

    lc = ee.ImageCollection(
        "COPERNICUS/Landcover/100m/Proba-V/Global").first()

    for key in data_dict_copy.keys():
        lc_val = lc.select("discrete_classification") \
            .reduceRegion(ee.Reducer.first(), data_dict_copy[key][3], 10) \
            .get("discrete_classification") \
            .getInfo()

        if lc_val in valid_ids:
            data_dict_filt[key] = data_dict_copy[key]

        lc_values.append(lc_val)

    with open('./data/stations.csv', 'a', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow(lc_values)

    print(str(len(data_dict_filt.items())) +
          " out of " + str(len(data_dict_copy.items())) +
          " locations remain after applying the land cover filter.")

    return data_dict_filt


def get_s1_backscatter(data_dict_filt):
    """For each key (= ISMN station) of the input dictionary, this function
    gets all available Sentinel-1 scenes (descending & ascending) and adds
    them to the dictionary as image collections.
    Afterwards backscatter timeseries are extracted for both image
    collections and added to the dictionary as pandas dataframes.

    :param data_dict_filt: Output dictionary of lc_filter(), which at this
    point should contain the following values for each key:
            - latitude (int)
            - longitude (int)
            - Soil moisture data (dataframe)
            - GEE geometry object (ee.geometry.Geometry of type 'Point' or
            'Polygon')
        :type: Dictionary

    :return: data_dict_filt with added image collections and dataframes
    containing backscatter timeseries (both descending & ascending).
    """
    data_dict = copy.deepcopy(data_dict_filt)
    data_dict = _get_image_collection(data_dict)  # Add S-1 image collection

    for key in data_dict.keys():
        try:
            geo_type = data_dict[key][3].getInfo()['type']

            if geo_type == 'Point':

                if data_dict[key][4].size().getInfo() > 0:
                    s1_data_desc = _time_series_of_a_point(data_dict[key][4],
                                                           data_dict[key][3])
                    data_dict[key].append(s1_data_desc)
                else:
                    print(str(key) + ": Image collection of the descending "
                                     "track is empty.\n No backscatter "
                                     "data was extracted.")
                    data_dict[key].append(None)

                if data_dict[key][5].size().getInfo() > 0:
                    s1_data_asc = _time_series_of_a_point(data_dict[key][5],
                                                          data_dict[key][3])
                    data_dict[key].append(s1_data_asc)
                else:
                    print(str(key) + ": Image collection of the ascending "
                                     "track is empty.\n No backscatter "
                                     "data was extracted.")
                    data_dict[key].append(None)

            elif geo_type == 'Polygon':

                if data_dict[key][4].size().getInfo() > 0:
                    s1_data_desc = _time_series_of_a_region(data_dict[key][4],
                                                            data_dict[key][3])
                    data_dict[key].append(s1_data_desc)
                else:
                    print(str(key) + ": Image collection of the descending "
                                     "track is empty.\n No backscatter "
                                     "data was extracted.")
                    data_dict[key].append(None)

                if data_dict[key][5].size().getInfo() > 0:
                    s1_data_asc = _time_series_of_a_region(data_dict[key][5],
                                                           data_dict[key][3])
                    data_dict[key].append(s1_data_asc)
                else:
                    print(str(key) + ": Image collection of the ascending "
                                     "track is empty.\n No backscatter "
                                     "data was extracted.")
                    data_dict[key].append(None)

            else:
                raise ValueError(str(key)
                                 + " - I didn't expect an object of type "
                                 + str(geo_type) + "here.")

        except IndexError:
            print("A GEE geometry object is missing for: "
                  + str(key))

    return data_dict


def _get_image_collection(data_dict_filt):
    """Gets the available Sentinel-1 image collection (ascending and
    descending) for each Earth Engine geometry object of a dictionary.

    :param data_dict_filt: Output dictionary of lc_filter(). Contains
    Earth Engine geometry objects that are used to retrieve the S-1 image
    collections.
        :type: Dictionary

    :return: Dictionary with added S-1 image collections.
    """
    data_dict = copy.deepcopy(data_dict_filt)

    pol_vv = ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')
    pol_vh = ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')
    mode = ee.Filter.eq('instrumentMode', 'IW')

    for key in data_dict.keys():
        s1 = ee.ImageCollection('COPERNICUS/S1_GRD') \
            .filter(pol_vv) \
            .filter(pol_vh) \
            .filter(mode) \
            .filterBounds(data_dict[key][3])

        s1_desc = s1.filter(
            ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))
        s1_asc = s1.filter(
            ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))

        data_dict[key].append(s1_desc)
        data_dict[key].append(s1_asc)

    return data_dict


def _get_s1_date(out):
    """ Obtains the SAR image acquisition date from the product ID
    Args:
        out (List of dictionaries): Each dictionary corresponds to the
        sentinel1 info of an image
    Returns:
        Dates : A list of the acquisition dates

    @author: Cristian Silva (crisj)
    Modified by: Marco Wolsza (maawoo)
    """
    dates = np.zeros(len(out)).tolist()
    vh = np.zeros(len(out)).tolist()
    vv = np.zeros(len(out)).tolist()
    angle = np.zeros(len(out)).tolist()
    df = pd.DataFrame()

    for i in range(len(out)):
        a = out[i]['id']
        b = a.split(sep='_')
        b2 = b[4].replace('T', ' ')
        dates[i] = datetime.datetime.strptime(b2, "%Y%m%d %H%M%S")
        vh[i] = out[i]['VH']
        vv[i] = out[i]['VV']
        angle[i] = out[i]['angle']

    df['Dates'] = dates
    df['VH'] = vh
    df['VV'] = vv
    df['angle'] = angle
    df.set_index('Dates', inplace=True)

    return df


def _simplify(fc):
    """Take a feature collection, as returned by mapping a reducer to an
    ImageCollection, and reshape it into a simpler list of dictionaries
    Args:
        fc (dict): Dictionary representation of a feature collection,
        as returned by mapping a reducer to an ImageCollection
    Returns:
        list: A list of dictionaries.

    @author: Cristian Silva (crisj)
    """

    def _feature2dict(f):
        id = f['id']
        out = f['properties']
        out.update(id=id)
        return out

    out = [_feature2dict(x) for x in fc['features']]

    return out


def _time_series_of_a_point(img_collection, point):
    """Returns backscatter values for a specific coordinate (point) for each
    image in an image collection (img_collection).

    @author: Cristian Silva (crisj)
    Modified by: Marco Wolsza (maawoo)
    """
    l = img_collection.filterBounds(point).getRegion(point, 10).getInfo()
    out = [dict(zip(l[0], values)) for values in l[1:]]
    df = _get_s1_date(out)
    df = df.sort_index(axis=0)

    return df


def _time_series_of_a_region(img_collection, geometry):
    """Returns mean backscatter values for a specific polygon (geometry) for
    each image in an image collection (img_collection).

    @author: Cristian Silva (crisj)
    Modified by: Marco Wolsza (maawoo)
    """

    def _reduce_region(image):
        """Spatial aggregation function for a single image and a polygon
        feature

        @author: Cristian Silva (crisj)
        Modified by: Marco Wolsza (maawoo)
        """
        # The reduction is specified by providing the reducer (
        # ee.Reducer.mean()) and the geometry (a polygon coord).
        stat_dict = image.reduceRegion(ee.Reducer.mean(), geometry)

        # Feature needs to be rebuilt because the backend
        # doesn't accept to map functions that return dictionaries.
        return ee.Feature(None, stat_dict)

    fc = img_collection.filterBounds(geometry).map(_reduce_region).getInfo()
    out = _simplify(fc)
    df = _get_s1_date(out)
    df = df.sort_index(axis=0)

    return df
