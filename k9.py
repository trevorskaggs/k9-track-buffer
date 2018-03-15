import datetime
import gpxpy
import geopy
import random
import math


def get_wind_dict(start_time, end_time, lon, lat):
    #TODO Get complete constrained wind dict in single request
    wind_dict = {}
    diff_seconds = (end_time - start_time).total_seconds() + 1
    for minute in range(0, int(diff_seconds)):
        wind_speed = random.randint(5, 10)
        wind_dir = random.randint(1, 60)
        wind_dict[minute] = {'speed': wind_speed, 'dir': wind_dir}
    return wind_dict

def get_pair_point(point, wind_dict):
    wind = wind_dict[(point.time - start_time).total_seconds()]
    R = 6378.1 #Radius of the Earth
    bearing = math.radians(wind['dir'])
    d = wind['speed'] * 0.003048  # Put the dog magic here

    lat1 = math.radians(point.latitude) #Current lat point converted to radians
    lon1 = math.radians(point.longitude) #Current long point converted to radians

    lat2 = math.asin( math.sin(lat1)*math.cos(d/R) +
         math.cos(lat1)*math.sin(d/R)*math.cos(bearing))

    lon2 = lon1 + math.atan2(math.sin(bearing)*math.sin(d/R)*math.cos(lat1),
                 math.cos(d/R)-math.sin(lat1)*math.sin(lat2))

    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return gpxpy.gpx.GPXTrackPoint(lat2, lon2)

in_file = 'sample-data/track.gpx'
out_file = 'sample-data/track-out.gpx'
gpx_infile = open(in_file)
gpx = gpxpy.parse(gpx_infile)
for track in gpx.tracks:
    for seg in track.segments:
        start_time = min(point.time for point in seg.points)
        end_time = max(point.time for point in seg.points)
        max_lon = max(point.longitude for point in seg.points)
        min_lat = min(point.latitude for point in seg.points)
        wind_dict = get_wind_dict(start_time, end_time, max_lon, min_lat)
        current_points = reversed(seg.points)
        for point in current_points:
            if point:
                seg.points.append(get_pair_point(point, wind_dict))
gpx_outfile = open(out_file, 'w')
gpx_outfile.write(gpx.to_xml())