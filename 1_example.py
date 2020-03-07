from GEE_ISMN import setup_pkg as pkg
from GEE_ISMN import preprocess as prep
from GEE_ISMN import earthengine as earth
from GEE_ISMN import postprocess as post
from GEE_ISMN import visualization as vis
import random

########
## Setup
user_input = pkg.setup_pkg()

########
## Preprocess
prep.data_handling()
data_dict = prep.data_import()

########
## GEE magic
data_dict = earth.lc_filter(data_dict, user_input)
data_dict = earth.get_s1_backscatter(data_dict)

########
## Postprocess
data_dict2 = post.ts_filter(data_dict)

########
## Visualization
random_station = random.choice(list(data_dict2.keys()))
vis.plot_data(data_dict2, random_station)
vis.show_map(data_dict, random_station)
img = vis.show_s1(data_dict, random_station, "2017-06-26")

## Faulty measurements!
station = 'HOBE-2.03-Decagon-5TE-A'
vis.plot_data(data_dict2, station)
vis.show_map(data_dict, station)
img = vis.show_s1(data_dict, station, "2017-06-26")
