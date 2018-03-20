import datetime
import gpxpy
from osgeo import ogr
from utils import get_pod_range, get_wind, get_wind_dict

file_name = 'example.gpx'
in_file = 'sample-data/' + file_name
out_file = 'output-data/' + file_name + '.kml'

kml_template = \
r"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
        <Placemark id="feat_2">
            <name>BufferedK9Trail</name>
                %s
        </Placemark>
    </Document>
</kml>"""

wind_dict = get_wind_dict()
all_points = []
trail = ogr.Geometry(ogr.wkbLineString)
gpx_infile = open(in_file)
gpx = gpxpy.parse(gpx_infile)
for track in gpx.tracks:
    for seg in track.segments:
        for point in seg.points:
            if point:
                pod = get_pod_range('D', 'C', 3, get_wind(point, wind_dict))
                trail.AddPoint(point.longitude, point.latitude)
with open(out_file, 'wb') as outfile:
    outfile.write(kml_template % trail.ExportToKML())