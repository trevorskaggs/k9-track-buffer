import datetime
import gpxpy
from shapely.geometry import LinearRing, Polygon
import simplekml
import utils

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
gpx_infile = open(in_file)
gpx = gpxpy.parse(gpx_infile)
for track in gpx.tracks:
    for seg in track.segments:
        wind_dict = utils.get_wind_dict()
        last_valid = None
        current_points = reversed(seg.points)
         #Set initial valid point
        for point in current_points:
            if point:
                # Check if point is far enough away (space/time) to create a new point.  
                if not last_valid or ((abs(point.latitude - last_valid.latitude) > .00001 and abs(point.longitude - last_valid.longitude) > .00001) and abs((last_valid.time - point.time).total_seconds()) > 15):
                    last_valid = point
                    seg.points.append(utils.get_pair_point(point, wind_dict))
all_points = [(point.longitude, point.latitude) for point in seg.points]
all_points.append((seg.points[0].longitude, seg.points[0].latitude))
kml = simplekml.Kml()
pol = kml.newpolygon(name='A Polygon')
pol.outerboundaryis.coords = all_points
kml.save('Track.kml')


