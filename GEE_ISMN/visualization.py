import ee
import geehydro # marked as not used, but still important to create the maps!
import folium
import webbrowser
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters


def plot_data(data_dict, station_name, orbit=None, pol=None):
    """Creates a plot comparing the ISMN soil moisture data with the
    Sentinel-1 backscatter data.

    :param data_dict: Dictionary created using the function ts_filter().
    Must include a dataframe that contains S-1 backscatter data (VH/VV),
    S-1 timestamps, ISMN soil moisture data, ISMN timestamps
        :type: Dictionary
    :param station_name: Name of a ISMN station (= dictionary keys of
    datd_dict)
        :type: String
    :param pol: Polarization; either "VV" or "VH"
        :type: String
    :param orbit: Orbit; either "desc" (= descending) or "asc" (= ascending)
        :type: String

    :return: Plot
    """
    global plot_label, plot_pol, plot_title
    station = station_name

    if data_dict[station][8] is None:
        raise KeyError("There is no data for the descending orbit of "
                       "station: ", station)
    elif data_dict[station][9] is None:
        raise KeyError("There is no data for the ascending orbit of station: "
                       , station)
    else:
        if orbit is None:
            orbit = "desc"
        if pol is None:
            pol = "VV"

        if type(station) != str:
            raise TypeError("The input for the parameter \"station\" should "
                            "be of type \"str\".")
        try:
            data_dict[station]
        except KeyError:
            print("The station " + str(station) + " was not found in the "
                                                  "input dictionary.")

        if pol not in ["VV", "VH"]:
            raise ValueError("Only \"VV\" or \"VH\" are valid options for the "
                             "input parameter \"pol\"!")
        elif type(pol) != str:
            raise TypeError("The input for the parameter \"pol\" should be of "
                            "type \"str\". Valid options are: \"VV\" or "
                            "\"VH\".")

        if orbit == "desc":
            plot_date = data_dict[station][8].t_s1_desc
            plot_soil = data_dict[station][8].sm
            if pol == "VV":
                plot_pol = data_dict[station][8].VV_desc
                plot_label = "VV - Descending"
                plot_title = "ISMN Soil Moisture against Sentinel-1 VV (" \
                             "Descending Orbit) "
            elif pol == "VH":
                plot_pol = data_dict[station][8].VH_desc
                plot_label = "VH - Descending"
                plot_title = "ISMN Soil Moisture against Sentinel-1 VH (" \
                             "Descending Orbit) "
        elif orbit == "asc":
            plot_date = data_dict[station][9].t_s1_asc
            plot_soil = data_dict[station][9].sm
            if pol == "VV":
                plot_pol = data_dict[station][9].VV_asc
                plot_label = "VV - Ascending"
                plot_title = "ISMN Soil Moisture against Sentinel-1 VV (" \
                             "Ascending Orbit) "
            elif pol == "VH":
                plot_pol = data_dict[station][9].VH_asc
                plot_label = "VH - Ascending"
                plot_title = "ISMN Soil Moisture against Sentinel-1 VH (" \
                             "Ascending Orbit) "
        else:
            raise ValueError("Only \"desc\" (= descending) or \"asc\" (= "
                             "ascending) are valid options for the input "
                             "parameter \"orbit\"!")
        if type(orbit) != str:
            raise TypeError("The input for the parameter \"orbit\" should be "
                            "of type \"str\". Valid options are: \"desc\" or "
                            "\"asc\".")

        register_matplotlib_converters()
        fig, plot1 = plt.subplots(figsize=(14, 8))
        plot_s1 = plot1.plot(plot_date, plot_pol, color='red',
                             label=plot_label)

        plot1.set_xlabel("Year", fontsize=14)
        plot1.set_ylabel("dB", fontsize=14)

        plot2 = plot1.twinx()
        plot_sm = plot2.plot(plot_date, plot_soil, color='blue', dashes=[6, 3],
                             label="Soil Moisture")

        plot2.set_ylabel("Soil Moisture", fontsize=14)
        plot1.xaxis.set_major_locator(plt.MaxNLocator(10))
        plot1.tick_params(axis='x', labelrotation=-45)
        plots = plot_s1 + plot_sm
        labels = [l.get_label() for l in plots]
        plot1.legend(plots, labels, bbox_to_anchor=(1.15, 1), loc='upper left',
                     borderaxespad=0.)

        plt.title(plot_title, fontsize=20)
        fig.tight_layout()
        plt.show()


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
    opens the file in the standard web browser.

    :param data_dict: Dictionary that contains data of ISMN stations to be
    analysed and also the extracted S-1 data (or at least the image
    collections).
        :type: Dictionary
    :param station_name: Name of a ISMN station.
        :type: String
    :param date: Date in the format "YYYY-MM-DD"
        :type: String
    :param pol: Polarisation; either "VV" or "VH"
        :type: String
    :param orbit: Orbit; either "desc" (= descending) or "asc" (= ascending)
        :type: String

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

