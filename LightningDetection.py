#--------------------------------------------------------------------------------------------
# LightningDetection.py
# VERSION: 0.0.2 - March 22, 2018
# AUTHOR: Blake Gardiner for People in Need  - blake.gardiner@peopleinneed.cz
#
# PARAMETERS: 
# DEPENDENCIES: untangle - pip install untangle
#                geopandas - reccomend to install via conda 'pip install geopandas'.
#                http://geopandas.org/install.html#dependencies
#                major pain setting up these environments....
# ABOUT:        This script assesses the JSON/XML response from Earth Networks
#                weather output. By overlaying the 'Warning' polygon (if any) with
#                Cambodian commune boundaries, we can identify at-risk communes.
#               Uses GeoPandas open source library to avoid ESRI stack reliance.
# FUTURE:       
# LIMITATIONS: - Ensure both datasets are the same cooridnate reference system, as 
#                geopandas does not support on the fly projection.
#              - The JSON response contains XML formatted data which is unusual.
#--------------------------------------------------------------------------------------------
# KNOWN ISSUES
# No subscription key currently, just read from supplied json file. Module 'getResponse' is
# sourced from Earth Networks documentation but has not been tested.
#
# Some of the test JSON files are not in the Cambodia area, therefore no overlap will exist.
#
#--------------------------------------------------------------------------------------------
import http.client, urllib.request, urllib.parse, urllib.error, base64, json, urllib.request, sys, os
import geopandas as gp, shapefile
from idlelib.rpc import response_queue
import untangle

def main():
    #USER DEFINED VARIABLES ###########################################################
    sourceJSONFile = "pplnneed_dta_20170908_090828.json"
    storm_warning_area_polygon = r"C:\Users\Blake\Documents\Blake\LiClipse Workspace\ERLightning\TESTPOLY2Cambodia.shp"
    cambodia_commune_polygon = r"C:\Users\Blake\Documents\Blake\LiClipse Workspace\ERLightning\khm_adm3_wgs84.shp"
    
    global WarningPoly #storm cell warning area polggon
    WarningPoly = "WARNING_AREA"
    global StormPoly #storm cell area polygon
    StormPoly = "STORMCELL"
    global CRS #reference system for new polygons
    CRS = "4326"
    #END USER DEFINED VARIABLES ########################################################
    
    #Process the JSON, create storm cell and warning area polygons.
    if processResponse(sourceJSONFile):
        #See if the warning polygon overlaps any Cambodian Commmunes.
        #Print a list.
        geopanda_analysis(cambodia_commune_polygon, storm_warning_area_polygon)
        
def getResponse(LatLong):
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': '{subscription key}',
    }
    
    params = urllib.parse.urlencode({
        # Request parameters
        'cultureInfo': '{string}',
        'verbose': '{string}',
    })
    
    try:
        conn = http.client.HTTPSConnection('earthnetworks.azure-api.net')
        conn.request("GET", "/getPublishedAlerts/data/alerts/v1/alerts?locationtype={latitudelongitude}&location={" + LatLong + "}&%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        
def processResponse(jsonResponse):
    try:
        ENresponse = json.load(open(jsonResponse))
        if not (ENresponse == "{}"): #ensure the response is not blank
            XMLresponse = (ENresponse['RawMessage'])
            obj = untangle.parse(XMLresponse)
            #print(obj.alert.identifier.cdata)
            #print("Lightning Severity: " + str(obj.alert.info.parameter[2].value)) #cell speed
            #print("Cell Speed: " + str(obj.alert.info.parameter[4].value)) #cell speed
            
            coordinates = str(obj.alert.info.area.polygon.cdata).split(", ") #split string into a list
            LatLongParts = []
            print("## Area Polygon ##")
            for pair in coordinates:
                latlong = pair.split(" ")
                LatLongParts.append([float(latlong[1]),float(latlong[0])])
            
            print(LatLongParts)
            w = shapefile.Writer(shapefile.POLYGON)
            w.poly(parts=[LatLongParts])
            w.field('FIRST_FLD','C','40')
            w.field('SECOND_FLD','C','40')
            w.record('Poly','PolyTest')
            w.save(WarningPoly)
        
            # create the .prj file
            prj = open(WarningPoly + ".prj", "w")
            # call the function and supply the epsg code
            epsg = getWKT_PRJ(CRS)
            prj.write(epsg)
            prj.close()   
            
            # now write a polygon for the stormcell polygon
            stormcellPoly = obj.alert.info.parameter[2].value.cdata
            stormcellPoly = stormcellPoly[:-2] #cleanup result
            stormcellPoly = stormcellPoly[10:] #cleanup result
            stormcellPoly = stormcellPoly.split(", ") #split string into a list
            print("## Stormcell Polygon ##")
            LatLongParts = []
            for pair in stormcellPoly:
                latlong = pair.split(" ")
                LatLongParts.append([float(latlong[1]),float(latlong[0])])
                
            print(LatLongParts)
            w = shapefile.Writer(shapefile.POLYGON)
            w.poly(parts=[LatLongParts])
            w.field('FIRST_FLD','C','40')
            w.field('SECOND_FLD','C','40')
            w.record('Poly','PolyTest')
            w.save(StormPoly)
        
            # create the .prj file
            prj = open(StormPoly + ".prj", "w")
            # call the function and supply the epsg code
            epsg = getWKT_PRJ(CRS)
            prj.write(epsg)
            prj.close()  
            return True 
    except Exception as e:
       print ("There was an error while processing. " + String(e))
       return False
   
def getWKT_PRJ (epsg_code):
     # Generate .prj file information using spatialreference.org
     # otherwise shapefile will have no spatial reference. 
     try:
         with urllib.request.urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(epsg_code)) as myurl:
             wkt = myurl.read()    
         remove_spaces = str(wkt).replace(" ","")
         prjString = str(remove_spaces).replace("\\n", "")
         prjString = prjString[2:-1]
         return prjString
     except Exception as e:
       print ("There was an error in getWKT_PRJ function. " + String(e))
      
def geopanda_analysis(commune_polygon, warning_polygon):
   # Select communes where the dataset intersects the warning area polygon.
   # Print the communes at risk.
   # Both datasets must be in the safe coordinate reference system for this to work.
    try:
        poly1 = gp.read_file(commune_polygon)
        poly2 = gp.read_file(warning_polygon)
        data = []
        dangerFlag = False
        for index, orig in poly1.iterrows():
            for index2, ref in poly2.iterrows():    
                if ref['geometry'].intersects(orig['geometry']): 
                    dangerFlag = True
                    owdspd=orig['COM_CODE']
                    data.append({'geometry':ref['geometry'].intersection(orig['geometry']),'wdspd':owdspd})
                    print("Commune " + str(owdspd) + " is within the storm warning area.")
        if not dangerFlag:
                print("There were no communes at risk from the storm.")
    except Exception as e:
       print ("There was an error in geopanda_analysis function. " + String(e))
      
if __name__ == "__main__":
    main()
