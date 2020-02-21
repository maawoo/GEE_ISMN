import ee
import os


def setup_pkg():
    """
    This function runs setup_dir() and setup_ee().

    setup_dir() is used to check if the subdirectory './data/ISMN/' exists,
        where ISMN files should be stored. It also creates a new subdirectory
        where filtered ISMN files are copied into during preprocessing.

    setup_ee() is used to initialize the Google Earth Engine API.
        ee.Initialize() checks if user credentials already exist. If that
        isn't the case, ee.Authenticate() is called first.
        Afterwards the user is asked for input that is relevant for the
        extraction of backscatter timeseries from GEE.

    :return: Dirctionary with user input generated through setup_ee().
    """
    input_dict = {}

    def setup_dir():
        data_dir = './data/ISMN/'
        new_dir = './data/ISMN_Filt/'

        if not os.path.exists(data_dir):
            raise IndexError('Path does not exist! \n Please make sure that '
                             'you store your ISMN files in the '
                             'subdirectory: \n %s !' % data_dir)

        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
            print("Directory ", new_dir, " created.")
        else:
            print("Directory ", new_dir, " already exists.")

    def setup_ee(input_dict):

        try:
            ee.Initialize()
        except:  # FileNotFoundError, IOError and some others didn't work...
            ee.Authenticate()
            ee.Initialize()

        while True:
            try:
                input_dict["box_yn"] = \
                    int(input(
                        "Do you want to extract... \n backscatter values "
                        "for the pixel coordinate (input: 0) \n or "
                        "the mean backscatter value for a box "
                        "surrounding the pixel coordinate (input: "
                        "1)?"))
            except ValueError:
                print("Sorry, I didn't understand that. \n ")
                continue

            if input_dict["box_yn"] not in (0, 1):
                print("Not an appropriate choice. \n ")
                continue

            elif input_dict["box_yn"] == 1:
                try:
                    input_dict["box_size"] = int(input("Please enter a box "
                                                       "size (e.g. 20 is "
                                                       "equal to a box of "
                                                       "size 20 by 20 "
                                                       "meters):"))
                except ValueError:
                    print("Sorry, I didn't understand that. \n ")
                    continue

                if input_dict["box_size"] == 0:
                    print("Not an appropriate choice. \n ")
                    continue
                else:
                    break
            else:
                input_dict["box_size"] = 0
                break

        return input_dict

    setup_dir()
    input_dict = setup_ee(input_dict)

    return input_dict
