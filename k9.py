import datetime
import gpxpy
import random
from osgeo import ogr, osr
from utils import get_distance_by_desired_pod, get_distance_in_ll, \
get_pod_range, get_stability_category, get_wind, get_wind_dict

file_name = 'example.gpx'
in_file = 'sample-data/' + file_name
out_file = 'output-data/' + file_name + '.kml'

kml_wrapper = \
r"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Placemark id="high_buff">
        <name>"High Buff"</name>
    %s
        </Placemark>
    </Document>
</kml>"""

DAY_STATUS = 'D' # Daytime
CLOUD_COVERAGE = 'C' # Clear
#SHADOW_LENGTH = 3

LOW_PROBABILITY = [.25, .5]
MEDIUM_PROBABILITY = [.50, .75]
HIGH_PROBABILITY = [.75, 1]

high_pod = ogr.Geometry(ogr.wkbMultiPolygon)

source = osr.SpatialReference()
source.ImportFromEPSG(4326)

target = osr.SpatialReference()
target.ImportFromEPSG(32610)

wind_dict = get_wind_dict()
all_points = []
trail = ogr.Geometry(ogr.wkbLineString)
gpx_infile = open(in_file)
gpx = gpxpy.parse(gpx_infile)
for track in gpx.tracks:
    for seg in track.segments:
        prev_point = seg.points[0]
        union_geom = ogr.Geometry(ogr.wkbPoint)
        union_geom.AddPoint(prev_point.longitude, prev_point.latitude)
        for point in seg.points[1:]:
            if point:
                if prev_point:
                    pod = get_pod_range(DAY_STATUS, CLOUD_COVERAGE, random.randint(1, 10), get_wind(point, wind_dict)['speed'])
                    stability_cat = get_stability_category(pod[0], pod[1])
                    distance = get_distance_by_desired_pod(stability_cat, MEDIUM_PROBABILITY[0], MEDIUM_PROBABILITY[1])
                    line = ogr.Geometry(ogr.wkbLineString)
                    line.AddPoint(prev_point.longitude, prev_point.latitude)
                    line.AddPoint(point.longitude, point.latitude)
                    line.Transform(osr.CoordinateTransformation(source, target))
                    high_buff = line.Buffer(distance)
                    high_buff.Transform(osr.CoordinateTransformation(target, source))
                    union_geom = union_geom.Union(high_buff)
                prev_point = point
with open(out_file, 'wb') as outfile:
    outfile.write(kml_wrapper % union_geom.ExportToKML())