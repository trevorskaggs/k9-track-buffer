import csv
import datetime
import gpxpy
import math
import random
import simplekml

def get_wind_dict(start_time, end_time, lon, lat):
    #TODO Get actual data...
    with open('sample-data/kestrel-data.csv', 'rb') as windfile:
        windreader = csv.reader(windfile, delimiter=',', quotechar='|')
        header_length = 11
        wind_dict = {}
        #Time,Temp,Wet Bulb Temp.,Rel. Hum.,Baro.,Altitude,Station P.,Wind Speed,Heat Index,Dew Point,Dens. Alt.,Crosswind,Headwind,Mag. Dir.,True Dir.,Wind Chill,
        for row in windreader:
            if windreader.line_num > header_length and row:
                time = datetime.datetime.strptime(row[0],'%Y-%m-%d %H:%M:%S')
                #wind_dict[time] = {'speed':row[7], 'dir': row[13]} Valid when complete file
                wind_dict[time] = {'speed':random.randint(0, 5), 'dir': random.randint(-10, 10)} #Random generation to not change sourcefile
    return wind_dict

def get_pair_point(point, wind_dict):
    wind = wind_dict[point.time] if point.time in wind_dict else wind_dict[min(wind_dict.keys(), key=lambda k: abs(k-point.time))]
    R = 6378.1 #Radius of the Earth
    bearing = math.radians(wind['dir'])
    d = wind['speed'] * 0.005000 # Convert windspeed at 1 m/s = 5 Meters
    # Put the dog magic here

    lat1 = math.radians(point.latitude) #Current lat point converted to radians
    lon1 = math.radians(point.longitude) #Current long point converted to radians

    lat2 = math.asin( math.sin(lat1)*math.cos(d/R) +
         math.cos(lat1)*math.sin(d/R)*math.cos(bearing))

    lon2 = lon1 + math.atan2(math.sin(bearing)*math.sin(d/R)*math.cos(lat1),
                 math.cos(d/R)-math.sin(lat1)*math.sin(lat2))

    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return gpxpy.gpx.GPXTrackPoint(lat2, lon2, point.elevation, point.time)

in_file = 'sample-data/example.gpx'
out_file = in_file + '.kml'
gpx_infile = open(in_file)
gpx = gpxpy.parse(gpx_infile)
for track in gpx.tracks:
    for seg in track.segments:
        start_time = min(point.time for point in seg.points)
        end_time = max(point.time for point in seg.points)
        max_lon = max(point.longitude for point in seg.points)
        min_lat = min(point.latitude for point in seg.points)
        wind_dict = get_wind_dict(start_time, end_time, max_lon, min_lat)
        last_valid = None
        current_points = reversed(seg.points)
         #Set initial valid point
        for point in current_points:
            if point:
                # Check if point is far enough away to create a new point.  
                if not last_valid or ((abs(point.latitude - last_valid.latitude) > .00000001 or abs(point.longitude - last_valid.longitude) > .00000001) and abs((last_valid.time - point.time).total_seconds()) > 30):
                    last_valid = point
                    seg.points.append(get_pair_point(point, wind_dict))
all_points = [(point.longitude, point.latitude) for point in seg.points]
all_points.append((seg.points[0].longitude, seg.points[0].latitude))
kml = simplekml.Kml()
kml.newpolygon(name='BufferedK9Trail', outerboundaryis=all_points)
kml.save(out_file)
