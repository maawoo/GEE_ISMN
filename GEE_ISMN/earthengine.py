import ee
import numpy as np
import pandas as pd
import datetime


def lc_filter(ismn_dict, user_input, landcover_ids=None):
    """
    1. ee_geometries(ismn_dict, user_input):
    Converts latitude/longitude to Earth Engine geometry objects based on
    parameters in user_input and adds them to the input dictionary that
    contains the ISMN data (ismn_dict).

    2. ee_filter(ismn_dict, landcover_ids):
    The landcover type of each location is checked based on the CGLS-LC100
    dataset (https://tinyurl.com/cgls-lc100). The input dictionary (
    ismn_dict) is then filtered based on provided landcover_ids.

    :param ismn_dict: Dictionary that contains ISMN data to be analysed.
    Output of preprocess.data_import().

    :param user_input: Dictionary that was created via user input through
    the setup_pkg() function. Contains the following key / value pairs:
        - box_yn / either 0 or 1
            Depending on the value, either point objects (0) or polygons (1)
            with the station coordinate as the midpoint are returned.
        - box_size / any integer > 0
            Defines the polygon size and will be used for the extraction of
            the mean backscatter of the defined region.

    :param landcover_ids: Landcover ids based on the CGLS-LC100
    dataset (https://tinyurl.com/cgls-lc100).
    Default values are:
        40 = Cultivated and managed vegetation / agriculture
        60 = Bare / sparse vegetation

    """
    if landcover_ids is None:
        landcover_ids = [40, 60]

    def ee_geometries(data_dict, input_dict):

        if input_dict["box_yn"] == 0:
            for key in data_dict.keys():
                try:
                    check = type(data_dict[key][3]) == ee.geometry.Geometry
                    if check == True:
                        pass

                    else:
                        print("Something is wrong. I didn't expect an object "
                              "of type " + str(type(data_dict[key][3])) +
                              "here.")
                        raise TypeError

                except IndexError:
                    data_dict[key].append(ee.Geometry.Point(data_dict[key][1],
                                                            data_dict[key][0]))

        elif input_dict["box_yn"] == 1:
            for key in data_dict.keys():
                try:
                    check = type(data_dict[key][3]) == ee.geometry.Geometry
                    if check == True:
                        pass

                    else:
                        print("Something is wrong. I didn't expect an object "
                              "of type " + str(type(data_dict[key][3])) +
                              "here.")
                        raise TypeError

                except IndexError:
                    data_dict[key].append(ee.Geometry.Point(data_dict[key][1],
                                                            data_dict[key][0])
                                          .buffer(input_dict["box_size"] / 2)
                                          .bounds())

        else:
            print("Something is wrong! \n The variable box_yn should be 0 ("
                  "extract backscatter for pixel coordinates) \n or 1 ( "
                  "extract mean backscatter for a bounding box). \n Please "
                  "run setup_pkg() again before continuing!")

        return data_dict

    def ee_filter(data_dict, lc_ids):

        new_dict = {}
        lc = ee.ImageCollection(
            "COPERNICUS/Landcover/100m/Proba-V/Global").first()
        valid_ids = lc_ids

        for key in data_dict.keys():
            lc_value = lc.select("discrete_classification") \
                .reduceRegion(ee.Reducer.first(), data_dict[key][3], 10) \
                .get("discrete_classification") \
                .getInfo()

            if lc_value in valid_ids:
                new_dict[key] = data_dict[key]

            print("Landcover ID: " + str(lc_value))

        print(str(len(new_dict.items())) +
              " out of " + str(len(data_dict.items())) +
              " locations remain after applying the land cover filter.")

        return new_dict

    ismn_dict_edit = ee_geometries(ismn_dict, user_input)
    ismn_dict_filt = ee_filter(ismn_dict_edit, landcover_ids)

    return ismn_dict_filt


def get_image_collection(ismn_dict_filt):
    """Gets the available Sentinel-1 image collection (ascending and
    descending) for each Earth Engine geometry object of a dictionary.

    :param ismn_dict_filt: Output dictionary of lc_filter(). Contains
    Earth Engine geometry objects that are used to retrieve the S-1 image
    collections.
    :return: Dictionary with added S-1 image collections.
    """
    data_dict = ismn_dict_filt
    mode = ee.Filter.eq('instrumentMode', 'IW')
    res = ee.Filter.eq('resolution', 'H')

    for key in data_dict.keys():
        s1 = ee.ImageCollection('COPERNICUS/S1_GRD') \
            .filter(mode) \
            .filter(res) \
            .filterBounds(data_dict[key][3])

        s1_desc = s1.filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))
        s1_asc = s1.filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))

        data_dict[key].append(s1_desc)
        data_dict[key].append(s1_asc)

    return data_dict


def get_s1_date(out):
    """ Obtains the SAR image acquisition date from the product ID
    Args:
        out (List of dictionaries): Each dictionary corresponds to the
        sentinel1 info of an image
    Returns:
        Dates : A list of the acquisition dates

    @author: crisj
    modified by: Marco Wolsza
    """
    dates = np.zeros(len(out)).tolist()
    vh = np.zeros(len(out)).tolist()
    vv = np.zeros(len(out)).tolist()
    angle = np.zeros(len(out)).tolist()
    df = pd.DataFrame()
    for i in range(len(out)):
        a = out[i]['id']
        b = a.split(sep='_')
        # b1=b[4].split(sep='T')
        # b2=b1[0]
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


def simplify(fc):
    """Take a feature collection, as returned by mapping a reducer to an
    ImageCollection, and reshape it into a simpler list of dictionaries
    Args:
        fc (dict): Dictionary representation of a feature collection,
        as returned by mapping a reducer to an ImageCollection
    Returns:
        list: A list of dictionaries.

    @author: crisj
    """

    def feature2dict(f):
        id = f['id']
        out = f['properties']
        out.update(id=id)
        return out

    out = [feature2dict(x) for x in fc['features']]

    return out


def time_series_of_a_point(img_collection, point):
    """
    @author: crisj
    Modified by: Marco Wolsza
    """
    l = img_collection.filterBounds(point).getRegion(point, 30).getInfo()
    out = [dict(zip(l[0], values)) for values in l[1:]]
    df = get_s1_date(out)
    df = df.sort_index(axis=0)

    return df


def time_series_of_a_region(img_collection, geometry):
    """
    @author: crisj
    Modified by: Marco Wolsza
    """

    def _reduce_region(image):
        """
        Spatial aggregation function for a single image and a polygon feature
        """
        # The reduction is specified by providing the reducer (
        # ee.Reducer.mean()), the geometry  (a polygon coord), at the scale
        # (30 meters) Feature needs to be rebuilt because the backend
        # doesn't accept to map functions that return dictionaries
        stat_dict = image.reduceRegion(ee.Reducer.mean(), geometry, 30)
        return ee.Feature(None, stat_dict)

    fc = img_collection.filterBounds(geometry).map(_reduce_region).getInfo()
    out = simplify(fc)
    df = get_s1_date(out)
    df = df.sort_index(axis=0)

    return df
