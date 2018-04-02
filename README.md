--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------
# LightningDetection.py
## VERSION
1.0 - April 02, 2018
## AUTHOR
Blake Gardiner for People in Need  - blake.gardiner@peopleinneed.cz

## PARAMETERS
## DEPENDENCIES
* reccomend to use a Python Conda environment. https://conda.io/docs/
* python 3.4 or later
* Plugin 'untangle' - _conda install untangle_
* Plugin 'geopandas'- _conda install geopandas_
   http://geopandas.org/install.html#dependencies major pain setting up these environments....
## ABOUT       
This script assesses the JSON/XML response from Earth Networks
weather output. By overlaying the 'Warning' polygon (if any) with
Cambodian commune boundaries, we can identify at-risk communes.

Uses GeoPandas open source library to avoid ESRI stack reliance.

## LIMITATIONS
* Ensure both datasets are the same cooridnate reference system, as geopandas does not support on the fly projection.
* The JSON response contains XML formatted data which is unusual.
## KNOWN ISSUES
* No subscription key currently, just read from supplied json file. Module 'getResponse' is sourced from Earth Networks documentation but has not been tested.
* Some of the test JSON files have data not in the Cambodia area, therefore no overlap will exist.
