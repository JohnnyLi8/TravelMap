

import urllib.request
import json
from Trip import Trip
import os.path
import gmplot
import mplleaflet
import matplotlib.pyplot as plt


def read_trip_geocodes_from_file(path):
    trip_geocodes = {}
    print("reading dict from path:", path)
    with open(path) as raw_data:
        for daily_trip in raw_data:
            daily_locations = []
            if ':' in daily_trip:
                info = daily_trip.split(':', 1)
                day_str = info[0]
                locations = info[1][2:-3]
                locations = locations.split("], [")
                for location in locations:
                    lat, lng = location.split(", ")
                    daily_locations.append([float(lat), float(lng)])
                trip_geocodes[day_str] = daily_locations
    print(trip_geocodes)
    return trip_geocodes


def read_geocodes_dict_from_file(path):
    geocodes_dict = {}
    print("reading dict from path:", path)
    with open(path) as raw_data:
        for place in raw_data:
            if ':' in place:
                info = place.split(":")
                place_name = info[0]
                location = info[1][1:-2]
                lat, lng = location.split(", ")
            geocodes_dict[place_name] = [float(lat), float(lng)]
    print(geocodes_dict)
    return geocodes_dict


def calculate_map_boundary(latitude_list, longitude_list):
    avg_lat = float((max(latitude_list) + min(latitude_list))/2)
    avg_lng = float((max(longitude_list) + min(longitude_list))/2)
    max_diff = max(max(latitude_list)-min(latitude_list), max(longitude_list)-min(longitude_list))
    return [avg_lat, avg_lng], max_diff


class GoogleMaps:
    def __init__(self):
        self.Direction_KEY = ''
        self.GEOCODING_KEY = ''
        self.PLACES_KEY = ''
        self.MAPPLOTTING_KEY = ''
        self.geocodes_dict = {}  # format: place: [lat in float, lng in float]
        self.trip = Trip()
        self.trip_waypoints = self.trip.waypoints
        self.trip_geocodes, self.geocodes_dict = self.get_trip_geocodes()
        # trip_geocodes format: day: [[lat1, lng1], [lat2, lng2], [lat3, lng3]]
        # geocodes_dict format: place: [lat in float, lng in float]

    def get_trip_geocodes(self):
        trip_geocodes = {}
        geocodes_dict = {}
        if os.path.exists('user/trip_geocodes.txt') and os.path.exists('user/geocodes_dict.txt'):
            trip_geocodes = read_trip_geocodes_from_file('user/trip_geocodes.txt')
            geocodes_dict = read_geocodes_dict_from_file('user/geocodes_dict.txt')
            return trip_geocodes, geocodes_dict
        else:
            print("getting trip geocodes...")
            for day in list(self.trip_waypoints.keys())[:-1]:  # last day: go home
                trip_geocodes[day] = []
                daily_trip = self.trip_waypoints[day]
                for waypoint in daily_trip:
                    if waypoint == 'go home':
                        # print(waypoint)
                        break
                    if waypoint in geocodes_dict:  # grab lat,lng from dict
                        location = geocodes_dict[waypoint]
                        # print("grabbing lat,lng from dict", waypoint)
                    else:  # request geocode from googlemaps
                        location = self.get_geocode(waypoint)
                        geocodes_dict[waypoint] = location
                    trip_geocodes[day].append(location)
            # print(self.trip_geocodes)
            with open('user/trip_geocodes.txt', 'w') as f1:
                for key, value in trip_geocodes.items():
                    f1.write('%s:%s\n' % (key, value))
            f1.close()
            print("trip_geocodes.txt output to file")
            with open('user/geocodes_dict.txt', 'w') as f2:
                for key, value in geocodes_dict.items():
                    f2.write('%s:%s\n' % (key, value))
            f2.close()
            print("geocodes_dict.txt output to file")
            return trip_geocodes, geocodes_dict

    def get_geocode(self, place):
        endpoint = 'https://maps.googleapis.com/maps/api/geocode/json?'
        processed_input = self.process_address(place)
        geocode_request = 'address={}&key={}'.format(processed_input, self.GEOCODING_KEY)
        request = endpoint + geocode_request
        # print(request)
        response = urllib.request.urlopen(request).read()
        geocode = json.loads(response)
        results = geocode['results'][0]
        location = results['geometry']['location']
        lat = location['lat']
        lng = location['lng']
        return [lat, lng]  # return type float

    def process_address(self, place_str):
        place_str = place_str.replace(", ", ",+").replace(" ", "+")
        if ", " not in place_str:
            place_str = place_str + ",+" + self.trip.main_country
        return place_str

    def plot_daily_trip(self, day):
        daily_locations = self.trip_geocodes[day]
        print(daily_locations)
        latitude_list = [coordinate[0] for coordinate in daily_locations]
        longitude_list = [coordinate[1] for coordinate in daily_locations]
        map_centre, max_diff = calculate_map_boundary(latitude_list, longitude_list)
        gmap = gmplot.GoogleMapPlotter(map_centre[0], map_centre[1], 9.5)
        gmap.apikey = self.MAPPLOTTING_KEY
        gmap.scatter(latitude_list, longitude_list, '6A5ACD',
                      size=1000, marker=False)
        # line tut
        # gmap.plot(latitude_list, longitude_list,
        #            'cornflowerblue', edge_width=2.5)
        print(max_diff)
        # plt.plot(longitude_list, latitude_list, 'r')
        path = 'maps/' + day + ".html"
        gmap.draw(path)
        # mplleaflet.show(path=path)


googlemaps = GoogleMaps()
googlemaps.plot_daily_trip('Day 14')
