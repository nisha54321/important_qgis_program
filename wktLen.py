# from geopy import distance
# from shapely.wkt import loads

# line_wkt="LINESTRING(3.0 4.0, 3.1 4.1)"

# line = loads(line_wkt)


# print (line.length)
from pyproj import Geod
from shapely import wkt

# specify a named ellipsoid
geod = Geod(ellps="WGS84")

poly = wkt.loads('''LINESTRING (71.09667241299999 26.366507205, 71.10052241299999 26.361657205, 71.104872413 26.357157205, 71.108072413 26.343407205, 71.10827241299999 26.343207205, 71.108372413 26.343007205, 71.108422413 26.342907205, 71.108522413 26.342607205, 71.11242241299999 26.321757205, 71.12402241299999 26.310157205, 71.12487241299999 26.308957205, 71.125022413 26.308707205, 71.125122413 26.308407205, 71.125172413 26.308157205, 71.139672413 26.291407205, 71.140022413 26.291007205, 71.140172413 26.290807205, 71.14027241299999 26.290657205, 71.14037241299999 26.290457205, 71.140472413 26.290157205, 71.140522413 26.289907205, 71.140622413 26.289307205, 71.14067241299999 26.289057205, 71.14077241299999 26.288457205, 71.140872413 26.287857205, 71.14452241299999 26.281557205)''')

area = geod.geometry_length(poly)

print(area)

from osgeo import ogr
wkt1 = "LINESTRING (71.09667241299999 26.366507205, 71.10052241299999 26.361657205, 71.104872413 26.357157205, 71.108072413 26.343407205, 71.10827241299999 26.343207205, 71.108372413 26.343007205, 71.108422413 26.342907205, 71.108522413 26.342607205, 71.11242241299999 26.321757205, 71.12402241299999 26.310157205, 71.12487241299999 26.308957205, 71.125022413 26.308707205, 71.125122413 26.308407205, 71.125172413 26.308157205, 71.139672413 26.291407205, 71.140022413 26.291007205, 71.140172413 26.290807205, 71.14027241299999 26.290657205, 71.14037241299999 26.290457205, 71.140472413 26.290157205, 71.140522413 26.289907205, 71.140622413 26.289307205, 71.14067241299999 26.289057205, 71.14077241299999 26.288457205, 71.140872413 26.287857205, 71.14452241299999 26.281557205)"
geom = ogr.CreateGeometryFromWkt(wkt1)
print ("Length = %d" % geom.Length())
