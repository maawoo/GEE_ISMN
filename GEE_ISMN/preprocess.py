import re
import glob
import shutil
import csv
from ismn import readers as ismn


def data_handling(measurement_depth=0.05):
    """Uses a regular expression to filter all ISMN files in ./data/ISMN
    for a specific measurement depth. Copies all matching files into the
    directory ./data/ISMN_Filt , which was created using the setup_pkg()
    function.

    :param measurement_depth: (optional) If not specified, the default
    value of 0.05 m is used.
        :type: float

    """
    depth = str(measurement_depth)
    file_list = [f for f in glob.glob("./data/ISMN/**/*_sm_*.stm",
                                      recursive=True)]
    regex = r".+\d{1,2}\.\d+\s+" + re.escape(depth)

    for file in file_list:
        checked_file = open(file)
        first = checked_file.readline()

        if re.match(regex, first):
            shutil.copy2(file, './data/ISMN_Filt/')

    file_list_filt = [f for f in glob.glob("./data/ISMN_Filt/**/*_sm_*.stm",
                                           recursive=True)]

    return print(str(len(file_list)) + " ISMN files were found in "
                                       "\'./data/ISMN/\'. \n"
                 + str(len(file_list_filt)) + " ISMN files with a "
                                              "measurement depth of "
                 + str(measurement_depth) + " were copied to \'./data"
                                            "/ISMN_Filt/\'")


def data_import():
    """Creates a dictionary with longitude, latitude and soil moisture data
    as values for each ISMN file located in ./data/ISMN_Filt .
    The key of each dictionary entry is created as a combination of network
    name, station name and sensor type.
    Also a CSV file with each key and the corresponding coordinates (
    latitude & longitude) is created in the directory ./data/

    :return: Dictionary containing ISMN data.
    """
    sm_files = [f for f in glob.glob("./data/ISMN_Filt/**/*_sm_*.stm",
                                     recursive=True)]

    dict_ismn = {}
    long = []
    lat = []
    station = []

    for i in sm_files:
        data = ismn.read_data(i)
        header_elements, filename_elements = ismn.get_info_from_file(i)
        dict_ismn[header_elements[1] + "-" + header_elements[2] + "-" +
                  header_elements[8]] = [header_elements[3],
                                         header_elements[4], data.data]
        long.append(header_elements[3])
        lat.append(header_elements[4])
        station.append(header_elements[1] + "-" + header_elements[2] + "-" +
                       header_elements[8])

    with open('./data/stations.csv', 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow(station)
        filewriter.writerow(long)
        filewriter.writerow(lat)

    return dict_ismn
