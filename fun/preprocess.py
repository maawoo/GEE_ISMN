import os
import io
import re
import glob
import shutil

def setup_dir():
    """
    bla bla
    :return:
    """
    newDir = './data/ISMN_Filt/'

    if not os.path.exists(newDir):
        os.mkdir(newDir)
        print("Directory ", newDir, " created.")
    else:
        print("Directory ", newDir, " already exists.")


def get_sm_files():
    """
    bla bla
    :return:
    """
    return [f for f in glob.glob("./data/ISMN/**/*_sm_*.stm", recursive=True)]


def filter_files(file_list, measurement_depth):
    """
    bla bla
    :param file_list:
    :param measurement_depth:
    :return:
    """
    regex = r".+\d{1,2}\.\d+\s+" + re.escape(measurement_depth)

    for file in file_list:
        checked_file = open(file)
        first = checked_file.readline()

        if re.match(regex, first):
            shutil.copy2(file, './data/ISMN_Filt/')

    return [f for f in glob.glob("./data/ISMN_Filt/**/*_sm_*.stm",
                                 recursive=True)]


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