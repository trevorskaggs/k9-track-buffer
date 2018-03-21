import datetime
import gpxpy
import random
from osgeo import ogr, osr
from utils import get_distance_by_desired_pod, get_pod_range,\
get_stability_category, get_wind, get_wind_dict

file_name = 'example.gpx'
in_file = 'sample-data/' + file_name
out_file = 'output-data/' + file_name + '.kml'

kml_wrapper = \
r"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="feat_1">
    <Style id="highbuffstyle">
      <LineStyle>
        <color>5014F000</color>
        <width>4</width>
      </LineStyle>
      <PolyStyle>
        <color>5014F000</color>
      </PolyStyle>
    </Style>
    <Style id="medbuffstyle">
      <LineStyle>
        <color>5014F0E6</color>
        <width>4</width>
      </LineStyle>
      <PolyStyle>
        <color>5014F0E6</color>
      </PolyStyle>
    </Style>
    <Style id="lowbuffstyle">
      <LineStyle>
        <color>501400B4</color>
        <width>4</width>
      </LineStyle>
      <PolyStyle>
        <color>501400B4</color>
      </PolyStyle>
    </Style>
%s
    </Document>
</kml>"""

feat_wrapper = """
<Placemark id="%s">
        <name>"%s"</name>
        <styleUrl>#%sstyle</styleUrl>
    %s
</Placemark>"""

DAY_STATUS = 'D' # Daytime
CLOUD_COVERAGE = 'C' # Clear
#SHADOW_LENGTH = 3

LOW_PROBABILITY = [.0, .1]
MEDIUM_PROBABILITY = [.1, .85]
HIGH_PROBABILITY = [.85, 1]

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
        high_union_geom = ogr.Geometry(ogr.wkbPoint)
        high_union_geom.AddPoint(prev_point.longitude, prev_point.latitude)
        med_union_geom = ogr.Geometry(ogr.wkbPoint)
        med_union_geom.AddPoint(prev_point.longitude, prev_point.latitude)
        low_union_geom = ogr.Geometry(ogr.wkbPoint)
        low_union_geom.AddPoint(prev_point.longitude, prev_point.latitude)
        for point in seg.points[1:]:
            if point:
                if prev_point:
                    pod = get_pod_range(DAY_STATUS, CLOUD_COVERAGE, random.randint(1, 10), get_wind(point, wind_dict)['speed'])
                    stability_cat = get_stability_category(pod[0], pod[1])
                    high_distance = get_distance_by_desired_pod(stability_cat, HIGH_PROBABILITY[0], HIGH_PROBABILITY[1])
                    med_distance = get_distance_by_desired_pod(stability_cat, MEDIUM_PROBABILITY[0], MEDIUM_PROBABILITY[1])
                    low_distance = get_distance_by_desired_pod(stability_cat, LOW_PROBABILITY[0], LOW_PROBABILITY[1])
                    line = ogr.Geometry(ogr.wkbLineString)
                    line.AddPoint(prev_point.longitude, prev_point.latitude)
                    line.AddPoint(point.longitude, point.latitude)
                    line.Transform(osr.CoordinateTransformation(source, target))
                    high_buff = line.Buffer(high_distance)
                    med_buff = line.Buffer(med_distance)
                    low_buff = line.Buffer(low_distance)
                    high_buff.Transform(osr.CoordinateTransformation(target, source))
                    med_buff.Transform(osr.CoordinateTransformation(target, source))
                    low_buff.Transform(osr.CoordinateTransformation(target, source))
                    high_union_geom = high_union_geom.Union(high_buff)
                    med_union_geom = med_union_geom.Union(med_buff)
                    low_union_geom = low_union_geom.Union(low_buff)
                prev_point = point
geoms = [('highbuff', high_union_geom), ('medbuff', med_union_geom.Difference(high_union_geom)), ('lowbuff', low_union_geom.Difference(med_union_geom).Difference(high_union_geom))]
with open(out_file, 'wb') as outfile:
    feat_out = ''
    for feat in geoms:
        feat_out += feat_wrapper % (feat[0], feat[0], feat[0], feat[1].ExportToKML())
    outfile.write(kml_wrapper % feat_out)