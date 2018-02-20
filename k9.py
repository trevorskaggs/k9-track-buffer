import gpxpy
import datetime


def convert_to_utc(time):
    return (time - datetime.datetime(1970, 1, 1)).total_seconds()

def get_wind_values(time):
    #TODO Get speed and direction of wind at closest to given time from wind dict time
    pass

def get_wind_dict(start_time, end_time):
    #TODO Get complete constrained wind dict in single request
    pass

gpx_file = open('sample-data/example.GPX')
gpx = gpxpy.parse(gpx_file)
for track in gpx.tracks:
    for seg in track.segments:
        length = len(seg.points)
        for point in seg.points:
            print '%s, %s, %s' % (point.latitude, point.longitude, point.time)
