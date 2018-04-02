--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------
# LightningDetection.py
## VERSION
0.0.2 - March 22, 2018
## AUTHOR
Blake Gardiner for People in Need  - blake.gardiner@peopleinneed.cz

## PARAMETERS
## DEPENDENCIES
* untangle - pip install untangle
* geopandas - reccomend to install via conda 'pip install geopandas'.
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
* Some of the test JSON files are not in the Cambodia area, therefore no overlap will exist.
