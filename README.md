# GEE_ISMN

This package is a project by Marco Wolsza and Patrick Fischer for the module GEO419 of the M.Sc. Geoinformatics at the Friedrich-Schiller-University Jena.

As the name *GEE_ISMN* already suggests, this package was developed as a link between the International Soil Moisture Network (ISMN) and the Python API of Google Earth Engine (GEE).
Currently the main functionalities of this package are: 

* Preparation of ISMN datasets (e.g. filter for a specific measurement depth).
* Application of a land cover filter using the [Copernicus CGLS-LC100 collection](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_Landcover_100m_Proba-V_Global).
* Extraction of Sentinel-1 backscatter time series using GEE (either for the point coordinates of each ISMN station or as a mean value for a bounding box surrounding each station).
* Filtering of the ISMN data to only keep measurements immediately before each Sentinel-1 scene's timestamp.
* Plotting of soil moisture and backscatter time series.
* Visualization of individual ISMN station coordinates and Sentinel-1 scenes on a map 
using GEE.

For a simple guide on how to use each function, please refer to the provided example [Jupyter Notebook](https://github.com/maawoo/GEE_ISMN/blob/master/GEE_ISMN_example.ipynb).

### Installation

Currently, the only method to install the *GEE_ISMN* package is to clone the entire repository to the directory of your project. This also  has the advantage that the code can be adapted and changed to your needs, as the current version probably lacks functionality or is limiting in some cases.

For everything to work properly you need to install the following packages:
[earthengine-api](https://anaconda.org/conda-forge/earthengine-api), [ismn](https://github.com/TUW-GEO/ismn) &                       [geehydro](https://geehydro.readthedocs.io/en/latest/installation.html).
```
conda install -c conda-forge earthengine-api 
pip install ismn 
pip install geehydro 
```

### ISMN data

Datasets from the International Soil Moisture Network are available as *[CEOP formatted files](https://ismn.geo.tuwien.ac.at/en/data-access/variables-ceop/)* and *[Header + values files](https://ismn.geo.tuwien.ac.at/en/data-access/variables-header-values/)*. 

**Please note, that his package currently only works with *Header + values files*!**
