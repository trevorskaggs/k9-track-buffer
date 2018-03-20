import datetime
import gpxpy
import random
from osgeo import ogr
from utils import get_distance_by_desired_pod, get_distance_in_ll, \
get_pod_range, get_stability_category, get_wind, get_wind_dict

file_name = 'example.gpx'
in_file = 'sample-data/' + file_name
out_file = 'output-data/' + file_name + '.kml'

kml_wrapper = \
r"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
    %s
    </Document>
</kml>"""

kml_geom = """<Placemark id="%s">
<name>%s</name>
  %s
</Placemark>"""

DAY_STATUS = 'D' # Daytime
CLOUD_COVERAGE = 'C' # Clear
#SHADOW_LENGTH = 3

LOW_PROBABILITY = [.25, .5]
MEDIUM_PROBABILITY = [.50, .75]
HIGH_PROBABILITY = [.75, 1]

high_pod = ogr.Geometry(ogr.wkbMultiPolygon)

wind_dict = get_wind_dict()
all_points = []
trail = ogr.Geometry(ogr.wkbLineString)
gpx_infile = open(in_file)
gpx = gpxpy.parse(gpx_infile)
for track in gpx.tracks:
    for seg in track.segments:
        for point in seg.points:
            if point:
                shadow = random.randint(1, 10)
                pod = get_pod_range(DAY_STATUS, CLOUD_COVERAGE, shadow, get_wind(point, wind_dict)['speed'])
                stability_cat = get_stability_category(pod[0], pod[1])
                distance = get_distance_by_desired_pod(stability_cat, HIGH_PROBABILITY[0], HIGH_PROBABILITY[1])
                pt = ogr.Geometry(ogr.wkbPoint)
                pt.AddPoint(point.longitude, point.latitude)
                hi_buff = pt.Buffer(get_distance_in_ll(point, distance))
                high_pod.AddGeometry(hi_buff)
                trail.AddPoint(point.longitude, point.latitude)
with open(out_file, 'wb') as outfile:
    output_geom_kml = kml_geom % (1, 'Original Trail', high_pod.ExportToKML())
    outfile.write(kml_wrapper % output_geom_kml)