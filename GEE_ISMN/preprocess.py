import os
import io
import re
import glob
import shutil


def data_handling(measurement_depth=0.05):
    """
    bla
    :param measurement_depth:
    """

    def get_sm_files():
        files = [f for f in glob.glob("./data/ISMN/**/*_sm_*.stm",
                                      recursive=True)]
        return files

    def filter_files(files, depth):

        depth = str(depth)
        regex = r".+\d{1,2}\.\d+\s+" + re.escape(depth)

        for file in files:
            checked_file = open(file)
            first = checked_file.readline()

            if re.match(regex, first):
                shutil.copy2(file, './data/ISMN_Filt/')

        return [f for f in glob.glob("./data/ISMN_Filt/**/*_sm_*.stm",
                                     recursive=True)]

    file_list = get_sm_files()
    file_list_filt = filter_files(file_list, measurement_depth)

    return print(str(len(file_list)) + " ISMN files were found in "
                                       "\'./data/ISMN/\'. \n"
                 + str(len(file_list_filt)) + " ISMN files with a "
                                              "measurement depth of "
                 + str(measurement_depth) + " were copied to \'./data"
                                            "/ISMN_Filt/\'")


def get_info_from_file(filename):
    """
    bla bla
    @author: Christoph Paulik & Philip Buttinger
    ISMN Package: https://github.com/TUW-GEO/ismn
    """
    with io.open(filename, mode='r', newline=None) as f:
        header = f.readline()
    header_elements = header.split()

    path, filen = os.path.split(filename)
    filename_elements = filen.split('_')

    return header_elements, filename_elements
