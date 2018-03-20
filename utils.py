import csv
import datetime
import gpxpy
import math
import random

def get_wind_dict():
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

POD_STABILITY_LOOKUP_DICT = {
            'A':{
                100: .13, 
                50: .56,
                25: .82,
                12.5: .92
            },
            'B':{
                100: .22,
                50: .60,
                25: .84,
                12.5: .93
            },
            'C':{
                100: .40,
                50: .71,
                25: .91,
                12.5: .96,
            },
            'D':{
                100: .82,
                50: .91,
                25: .97,
                12.5: .98
            },
            'E':{
                100: .91,
                50: .96,
                25: .98,
                12.5: .99,
            },
            'F':{
                100: .95,
                50: .97,
                25: .99,
                12.5: .99
            },
        }
