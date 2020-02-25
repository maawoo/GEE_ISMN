import ee
import folium
import webbrowser

# vis_comparison(data_dict, station=None, timeframe=None)
#   - station:
#       - (Default) station=None: Alle Stationen
#       - station=["station_1", "station_2", etc]: Plots nur für die
#       gewünschten Stationen
#   - timeframe:
#       - (Default) timeframe=None: Gesamter Zeitraum wird dargestellt
#       - timeframe=[start, end]: ZB ["2017-01-01", ["2017-06-01"], dann
#       wird nur der gewünschte Zeitraum dargestellt
#   - Output: als png in "./figs/" (?)


##############

def show_map(data_dict, station_name):
    """Display a map (Google Maps/Satellite imagery) with the location of an
    ISMN station (or surrounding polygon, depending on previous user input).

    :param data_dict: Dictionary that contains data of ISMN stations to be
    analysed. Should at least contain latitude, longitude and the converted
    GEE geometry object.
    :type data_dict: Dictionary

    :param station_name: Name of the ISMN station that should be visualized
    on a map.
    :type station_name: String

    :return: Saves map.html in the current working directory folder and
    opens the file in the standard webbrowser.
    """
    station = station_name

    if type(station) != str:
        raise TypeError("The input for the parameter \"station\" should be "
                        "of type \"str\".")
    try:
        data_dict[station]
    except KeyError:
        print("The station " + str(station) + " was not found in the input "
                                              "dictionary.")

    lat = data_dict[station][0]
    long = data_dict[station][1]
    geo = data_dict[station][3]

    map_ = folium.Map(location=[lat, long], zoom_start=20)
    map_.setOptions('SATELLITE')
    map_.addLayer(geo, {'color': 'FF0000'})
    map_.setControlVisibility(layerControl=True)

    map_.save('map.html')
    return webbrowser.open('map.html')


def show_s1(data_dict, station_name, date, orbit=None, pol=None):
    """Display and save the Sentinel-1 scene that covers a given ISMN station
    closest in time, relative to a given date. For more specific results
    orbit and polarisation can also be defined.
    Saves map_s1.html in the current working directory folder and
    opens the file in the standard webbrowser.

    :param data_dict: Dictionary that contains data of ISMN stations to be
    analysed and also the extracted S-1 data (or at least the image
    collections).
    :type data_dict: Dictionary

    :param station_name: Name of a ISMN station.
    :type station_name: String

    :param date: Date in the format "YYYY-MM-DD"
    :type data: String

    :param pol: Polarisation; either "VV" or "VH"
    :type pol: String

    :param orbit: Orbit; either "desc" (= descending) or "asc" (= ascending)
    :type orbit: String

    :return: Sentinel-1 scene as ee.Image
    """
    station = station_name

    if orbit is None:
        orbit = "desc"
    if pol is None:
        pol = "VV"

    if type(station) != str:
        raise TypeError("The input for the parameter \"station\" should be "
                        "of type \"str\".")
    try:
        data_dict[station]
    except KeyError:
        print("The station " + str(station) + " was not found in the input "
                                              "dictionary.")

    if pol not in ["VV", "VH"]:
        raise ValueError("Only \"VV\" or \"VH\" are valid options for the "
                         "input parameter \"pol\"!")
    elif type(pol) != str:
        raise TypeError("The input for the parameter \"pol\" should be of "
                        "type \"str\". Valid options are: \"VV\" or \"VH\".")

    date = ee.Date(date)
    lat = data_dict[station][0]
    long = data_dict[station][1]
    geo = data_dict[station][3]

    img_coll_desc = data_dict[station][4].select([pol])
    img_coll_asc = data_dict[station][5].select([pol])

    if orbit == "desc":
        img_coll = _date_dist(img_coll_desc, date)
    elif orbit == "asc":
        img_coll = _date_dist(img_coll_asc, date)
    else:
        raise ValueError("Only \"desc\" (= descending) or \"asc\" (= "
                         "ascending) are valid options for the input "
                         "parameter \"orbit\"!")
    if type(orbit) != str:
        raise TypeError("The input for the parameter \"orbit\" should be of "
                        "type \"str\". Valid options are: \"desc\" or "
                        "\"asc\".")

    img = img_coll.sort('dateDist', True).first()

    _map = folium.Map(location=[lat, long], zoom_start=15)
    _map.setOptions('SATELLITE')
    _map.addLayer(img, {'min': -40, 'max': 0}, 'img1')
    _map.addLayer(geo, {'color': 'FF0000', 'fillColor': '00000000'}, 'POI')
    _map.setControlVisibility(layerControl=True)
    _map.save('map_s1.html')
    webbrowser.open('map_s1.html')

    return img


def _date_dist(img_coll, date):
    """Adds 'dateDist' column to each image of an image collection.
    dateDist = deviation of 'system:time_start' from a given date (in
    milliseconds).
    """
    def _img_iter(image):

        image = image.set('dateDist', ee.Number(image.get(
            'system:time_start')).subtract(date.millis()).abs())

        return image

    coll = img_coll.map(_img_iter)

    return coll
