import re
import glob
import shutil
import csv
from ismn import readers as ismn


def data_handling(measurement_depth=0.05):
    """
    This function uses the function "filter_files" and generates a list of
    the filtered files in "ISMN_Filt"
    :param measurement_depth: variable containing required the maximum depth of the ISMN Data
    :type measurement_depth: int
    :return

    """
    file_list = [f for f in glob.glob("./data/ISMN/**/*_sm_*.stm",
                                      recursive=True)]

    file_list_filt = _filter_files(file_list, measurement_depth)

    return print(str(len(file_list)) + " ISMN files were found in "
                                       "\'./data/ISMN/\'. \n"
                 + str(len(file_list_filt)) + " ISMN files with a "
                                              "measurement depth of "
                 + str(measurement_depth) + " were copied to \'./data"
                                            "/ISMN_Filt/\'")


def data_import():
    """
    This function creates an dictionary which contains the longitude,
    latitude and the stationname of the remaining ISMN Data in "ISMN_Filt".
    Also it creates an csv file which contains the same info to
    get an overview of the data.

    :return: a dictionary which contains longitude, latitude
            and stationname of filtered IMSN Files
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


def _filter_files(files, depth):
    """
    This function uses a regular expression for filtering the ISMN Files by
    required maximum depth and copies them in the new created folder "ISMN_Filt"
    :param files: list of all ISMN Filenames.
    :type files: list
    :param depth: variable containing required the maximum depth of the ISMN Data
    :type depth: int
    :return: a list of the Filenames in "ISMN_Filt"
    """
    depth = str(depth)
    regex = r".+\d{1,2}\.\d+\s+" + re.escape(depth)

    for file in files:
        checked_file = open(file)
        first = checked_file.readline()

        if re.match(regex, first):
            shutil.copy2(file, './data/ISMN_Filt/')

    return [f for f in glob.glob("./data/ISMN_Filt/**/*_sm_*.stm",
                                 recursive=True)]
