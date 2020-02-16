import ee
import numpy as np
import pandas as pd
import datetime


def setup_ee():
    """
    bla bla
    :return:
    """
    try:
        ee.Initialize()
    except:
        ee.Authenticate()
        ee.Initialize()

    user = {}

    while True:
        try:
            user["box_yn"] = \
                int(input("Do you want to extract... \n backscatter values "
                          "for the pixel coordinate (input: 0) \n or "
                          "the mean backscatter value for a box "
                          "surrounding the pixel coordinate (input: "
                          "1)?"))
        except ValueError:
            print("Sorry, I didn't understand that. \n ")
            continue

        if user["box_yn"] not in (0, 1):
            print("Not an appropriate choice. \n ")
            continue

        elif user["box_yn"] == 1:
            try:
                user["box_size"] = int(input("Please enter a box size "
                                             "(e.g. 20 is equal to a "
                                             "box of size 20 by 20 "
                                             "meters):"))
            except ValueError:
                print("Sorry, I didn't understand that. \n ")
                continue

            if user["box_size"] == 0:
                print("Not an appropriate choice. \n ")
                continue
            else:
                break

        else:
            user["box_size"] = 0
            break

    return user


def process_geojson(geojson, user_input):
    """Creates a list of Earth Engine (EE) geometry objects from ISMN station
    coordinates.

    :param user_input: Dictionary that was created via user input through
    the setup_ee() function. Contains the following key / value pairs:
        - box_yn / either 0 or 1
            Depending on the value, either point objects (0) or polygons
            that enclose the station coordinates (1) are returned.
        - box_size / any integer > 0
            Defines the polygon size surrounding the station coordinates and
            will be used for the extraction of the mean backscatter of the
            defined region.
    :param geojson: Imported GeoJSON file that includes ISMN station
    coordinates.
    :return: List of EE geometry objects.
    """
    geo_list = []
    user = user_input

    if user["box_yn"] == 0:
        for i in range(len(geojson)):
            geo_list.append(ee.Geometry.Point(geojson["geometry"][i].y,
                                              geojson["geometry"][i].x))
    elif user["box_yn"] == 1:
        for i in range(len(geojson)):
            geo_list.append(ee.Geometry.Point(geojson["geometry"][i].y,
                                              geojson["geometry"][i].x)
                            .buffer(user["box_size"] / 2)
                            .bounds())
    else:
        print("Something is wrong! \n The variable box_yn should be 0 ("
              "extract backscatter for pixel coordinates) \n or 1 ( "
              "extract mean backscatter for a bounding box). \n Please run "
              "setup_ee() before continuing.")



    return geo_list


def lc_filter(geo_list):
    """Filters a list of Earth Engine (EE) geometry objects by checking the
    land cover type of each location.
    Land cover dataset: https://tinyurl.com/cgls-lc100
    Valid land cover types:
    40 = Cultivated and managed vegetation / agriculture
    60 = Bare / sparse vegetation

    :param geo_list: List of EE geometry objects.
    :return: Filtered list of EE geometry objects.
    """
    lc = ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V/Global").first()
    valid_ids = [40, 60]
    geo_list_filt = []

    for geo in range(len(geo_list)):
        lc_value = lc.select("discrete_classification") \
            .reduceRegion(ee.Reducer.first(), geo_list[geo], 10) \
            .get("discrete_classification") \
            .getInfo()

        if lc_value in valid_ids:
            geo_list_filt.append(geo_list[geo])

    print(str(len(geo_list_filt)) +
          " out of " + str(len(geo_list)) +
          " locations remain after applying the land cover filter.")

    return geo_list_filt


def get_image_collection(geo_list_filt):
    """Gets the available Sentinel-1 image collection (ascending and
    descending) for each Earth Engine (EE) geometry object of a list.

    :param geo_list_filt: Filtered list of EE geometry objects.
    :return: Dictionary with EE geometry object, descending and ascending
    S-1 image collections as values.
    """
    img_coll = {}
    mode = ee.Filter.eq('instrumentMode', 'IW')
    res = ee.Filter.eq('resolution', 'H')

    for geo in range(len(geo_list_filt)):
        s1 = ee.ImageCollection('COPERNICUS/S1_GRD') \
            .filter(mode) \
            .filter(res) \
            .filterBounds(geo_list_filt[geo])

        s1_desc = s1.filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))
        s1_asc = s1.filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))

        img_coll["geo_" + str(geo)] = [geo_list_filt[geo], s1_desc, s1_asc]

    return img_coll


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
