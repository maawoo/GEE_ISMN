from GEE_ISMN import setup_pkg as pkg
from GEE_ISMN import preprocess as prep
from GEE_ISMN import earthengine as earth
from GEE_ISMN import postprocess as post
from GEE_ISMN import visualization as vis

## Setup
user_input = pkg.setup_pkg()


## Preprocess
prep.data_handling()
dict_ISMN = prep.data_import()


## GEE magic
earth.lc_filter(dict_ISMN, user_input)
earth.get_s1_backscatter(dict_ISMN)


## Postprocess


## Visualization
station = 'RSMN-5TM-Dumbraveni'

vis.show_map(dict_ISMN, station)
img = vis.show_s1(dict_ISMN, station, "2017-06-26")
