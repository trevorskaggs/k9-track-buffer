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
                wind_dict[time] = {'speed':random.randint(0, 25), 'dir': random.randint(-10, 10)} #Random generation to not change sourcefile
    return wind_dict

def get_wind(point, wind_dict):
    return wind_dict[point.time] if point.time in wind_dict else wind_dict[min(wind_dict.keys(), key=lambda k: abs(k-point.time))]

def get_pod_range(day_status, cloud_coverage, shadow_length, wind):
    if day_status == 'D':
        if cloud_coverage == 'C':
            if shadow_length < 3.5:
                if wind < 4:
                    return 5, 25
                elif wind >= 4 and wind < 7:
                    return 7, 27
                elif wind >= 7 and wind < 10:
                    return 10, 30
                elif wind >= 10 and wind < 14:
                    return 35, 45
                elif wind >= 14:
                    return 35, 45
            elif shadow_length >= 3.5 and shadow_length < 8.5:
                if wind < 4:
                    return 7, 27
                elif wind >= 4 and wind < 7:
                    return 10, 30
                elif wind >= 7 and wind < 10:
                    return 20, 40
                elif wind >= 10 and wind < 14:
                    return 55, 65
                elif wind >= 14:
                    return 80, 85
            elif shadow_length >= 8.5:
                if wind < 4:
                    return 10, 30
                elif wind >= 4 and wind < 7:
                    return 35, 45
                elif wind >= 7 and wind < 10:
                    return 35, 45
                elif wind >= 10 and wind < 14:
                    return 80, 85
                elif wind >= 14:
                    return 80, 85
        elif cloud_coverage == 'M':
            if shadow_length < 3.5:
                if wind < 4:
                    return 7, 27
                elif wind >= 4 and wind < 7:
                    return 10, 30
                elif wind >= 7 and wind < 10:
                    return 20, 40
                elif wind >= 10 and wind < 14:
                    return 55, 65
                elif wind >= 14:
                    return 80, 85
            elif shadow_length >= 3.5 and shadow_length < 8.5:
                if wind < 4:
                    return 10, 30
                elif wind >= 4 and wind < 7:
                    return 35, 45
                elif wind >= 7 and wind < 10:
                    return 35, 45
                elif wind >= 10 and wind < 14:
                    return 55, 65
                elif wind >= 14:
                    return 80, 85
            elif shadow_length >= 8.5:
                if wind < 4:
                    return 80, 85
                elif wind >= 4 and wind < 7:
                    return 80, 85
                elif wind >= 7 and wind < 10:
                    return 80, 85
                elif wind >= 10 and wind < 14:
                    return 80, 85
                elif wind >= 14:
                    return 80, 85
        elif cloud_coverage == 'M':
            if shadow_length < 3.5:
                if wind < 4:
                    return 10, 30
                elif wind >= 4 and wind < 7:
                    return 35, 45
                elif wind >= 7 and wind < 10:
                    return 35, 45
                elif wind >= 10 and wind < 14:
                    return 80, 85
                elif wind >= 14:
                    return 80, 85
            elif shadow_length >= 3.5 and shadow_length < 8.5:
                if wind < 4:
                    return 80, 85
                elif wind >= 4 and wind < 7:
                    return 80, 85
                elif wind >= 7 and wind < 10:
                    return 80, 85
                elif wind >= 10 and wind < 14:
                    return 80, 85
                elif wind >= 14:
                    return 80, 85
            elif shadow_length >= 8.5:
                if wind < 4:
                    return 80, 85
                elif wind >= 4 and wind < 7:
                    return 80, 85
                elif wind >= 7 and wind < 10:
                    return 80, 85
                elif wind >= 10 and wind < 14:
                    return 80, 85
                elif wind >= 14:
                    return 80, 85
    elif day_status == 'N':
        if cloud_coverage == 'C':
            if wind >= 0 and wind < 7:
                return 95, 96
            elif wind >= 7 and wind < 10:
                return 90, 92
            elif wind >= 10 and wind < 14:
                return 80, 85
            elif wind >= 14:
                return 80, 85
        elif cloud_coverage == 'M':
            if wind >= 0 and wind < 7:
                return 90, 92
            elif wind >= 7 and wind < 10:
                return 80, 85
            elif wind >= 10 and wind < 14:
                return 80, 85
            elif wind >= 14:
                return 80, 85


def get_stability_category(min_pod, max_pod):
    average_pod = (min_pod + max_pod) / 2
    if average_pod < 10:
        return 'A'
    elif average_pod >= 10 and average_pod < 40:
        return 'B'
    elif average_pod >= 40 and average_pod < 60:
        return 'C'
    elif average_pod >= 60 and average_pod < 90:
        return 'D'
    elif average_pod >= 90 and average_pod < 95:
        return 'E'
    elif average_pod >=95:
        return 'F'

def get_distance_by_desired_pod(stability_cat, min_desired_pod, max_desired_pod):
    for distance, prob in sorted(POD_STABILITY_LOOKUP_DICT[stability_cat].iteritems(), reverse=True):
        if prob >= min_desired_pod and prob <= max_desired_pod:
            return distance
    #If no matches, assume 100 meters is detectable
    return 100

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
