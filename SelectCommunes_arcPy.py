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

