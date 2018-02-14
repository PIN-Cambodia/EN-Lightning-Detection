#--------------------------------------------------------------------------------------------
# LightningDetection.py
# VERSION: 0.0.1 - Feb 14, 2018
# AUTHOR: Blake Gardiner for People in Need  - blake.gardiner@peopleinneed.cz
#
# PARAMETERS: 
# DEPENDENCIES: untangle - pip install untangle
# ABOUT:
# LIMITATIONS: Relies on ArcPy and therefore an ESRI ArcGIS installation.
#--------------------------------------------------------------------------------------------
# KNOWN ISSUES
# No subscription key currently, just read from supplied json file.
#--------------------------------------------------------------------------------------------
import http.client, urllib.request, urllib.parse, urllib.error, base64, json, urllib.request
import shapefile
from idlelib.rpc import response_queue
import untangle


def main():
    # No api key :(
    #getResponse("9.85521608608867,-80.70281982421876")
    sourceJSONFile = "pplnneed_dta_20170908_090828.json"
    processResponse(sourceJSONFile)
        
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
    ENresponse = json.load(open(jsonResponse))
    XMLresponse = (ENresponse['RawMessage'])
    #print(XMLresponse)

    obj = untangle.parse(XMLresponse)
    #print(obj.alert.identifier.cdata)
    print("Lightning Severity: " + str(obj.alert.info.parameter[2].value)) #cell speed
    print("Cell Speed: " + str(obj.alert.info.parameter[4].value)) #cell speed
    
    coordinates = str(obj.alert.info.area.polygon.cdata).split(", ") #split string into a list
    LatLongParts = []
    print("## Area Polygon ##")
    for pair in coordinates:
        latlong = pair.split(" ")
        #print("Lat: " + latlong[0] + " Long: " + latlong[1])
        LatLongParts.append([float(latlong[1]),float(latlong[0])])
    
    print(LatLongParts)
    w = shapefile.Writer(shapefile.POLYGON)
    w.poly(parts=[LatLongParts])
    w.field('FIRST_FLD','C','40')
    w.field('SECOND_FLD','C','40')
    w.record('Poly','PolyTest')
    w.save('WARNING_AREA')

    # create the .prj file
    prj = open("WARNING_AREA.prj", "w")
    # call the function and supply the epsg code
    epsg = getWKT_PRJ("4326")
    prj.write(epsg)
    prj.close()   
    
    
    
    # now write a polygon for the stormcell polygon
    #print(obj.alert.info.parameter[2].value.cdata) #stormcell polygon
    stormcellPoly = obj.alert.info.parameter[2].value.cdata
    stormcellPoly = stormcellPoly[:-2] #cleanup result
    stormcellPoly = stormcellPoly[10:] #cleanup result
    stormcellPoly = stormcellPoly.split(", ") #split string into a list
    print("## Stormcell Polygon ##")
    LatLongParts = []
    for pair in stormcellPoly:
        latlong = pair.split(" ")
        #print("Lat: " + latlong[0] + " Long: " + latlong[1])
        LatLongParts.append([float(latlong[1]),float(latlong[0])])
        
    print(LatLongParts)
    w = shapefile.Writer(shapefile.POLYGON)
    w.poly(parts=[LatLongParts])
    w.field('FIRST_FLD','C','40')
    w.field('SECOND_FLD','C','40')
    w.record('Poly','PolyTest')
    w.save('STORMCELL')

    # create the .prj file
    prj = open("STORMCELL.prj", "w")
    # call the function and supply the epsg code
    epsg = getWKT_PRJ("4326")
    prj.write(epsg)
    prj.close()        
        
def getWKT_PRJ (epsg_code):
     # function to generate .prj file information using spatialreference.org
     # access projection information
     with urllib.request.urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(epsg_code)) as myurl:
         wkt = myurl.read()    
     remove_spaces = str(wkt).replace(" ","")
     prjString = str(remove_spaces).replace("\\n", "")
     prjString = prjString[2:-1]
     return prjString

def arcgis_selection():
    # Import arcpy module
    import arcpy
    arcpy.env.workspace = "C:/Users/Blake/Documents/Blake/LiClipse Workspace/ERLightning"
    
    # Local variables:
    communePoly = "khm_admbnda_adm3_gov.shp"
    warningAreaPoly = "TESTPOLY2Cambodia.shp"
        
    # Make feature layer as input
    arcpy.MakeFeatureLayer_management(communePoly, 'communeLayer')
    # Process: Select Layer By Location
    arcpy.SelectLayerByLocation_management('communeLayer', "INTERSECT", warningAreaPoly, "", "NEW_SELECTION", "NOT_INVERT")
    
    rows = arcpy.SearchCursor('communeLayer')
    counter = 0
    for row in rows:
        counter += 1
        print("Commune ["  + str(row.getValue('HRName') + "] is in the path of ER Lightning Warning Polygon!"))
    print("A total of " + str(counter) + " communes are at risk from the approaching storm.")
    

        
if __name__ == "__main__":
    main()
