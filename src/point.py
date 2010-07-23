# -*- coding: utf-8 -*-
import math

class point():
    lat = 0.0
    lon = 0.0
    description = None
    cloudmade_key = 'f4f1cc62bbca426a84fe69fcd27b0498'

    def __init__(self, latitude = 0.0, longitude = 0.0):
        self.lat = float(latitude)
        self.lon = float(longitude)

    def distance_to(self, point, unit = 'K'):

        start_long = math.radians(self.lon)
        start_latt = math.radians(self.lat)
        end_long = math.radians(point.lon)
        end_latt = math.radians(point.lat)


        d_latt = end_latt - start_latt
        d_long = end_long - start_long
        a = math.sin(d_latt/2)**2 + math.cos(start_latt) * math.cos(end_latt) * math.sin(d_long/2)**2
        c = 2 * math.atan2(math.sqrt(a),  math.sqrt(1-a))
        final = 6371 * c

        # Convert to nautical miles
        if unit is 'N':
            final = final * 0.539956803

        return final

    def bearing_to(self, point):
        distance = self.distance_to(point, 'N')
        if distance is 0:
            return None
        arad = math.acos((math.sin(math.radians(point.lat)) - math.sin(math.radians(self.lat)) * math.cos(math.radians(distance / 60))) / (math.sin(math.radians(distance / 60)) * math.cos(math.radians(self.lat))))
        bearing = arad * 180 / math.pi
        if (math.sin(math.radians(point.lon - self.lon)) < 0):
            bearing = 360 - bearing
        return int(bearing)

    def pretty_print(self):
        lat_degrees = math.floor(abs(self.lat))
        lat_minutes = (abs(self.lat) % abs(lat_degrees)) * 60
        lat_seconds = (lat_minutes % int(lat_minutes)) * 60
        lon_degrees = int(self.lon)
        lon_minutes = (abs(self.lon) % abs(lon_degrees)) * 60
        lon_seconds = (lon_minutes % int(lon_minutes)) * 60

        lat = u"%s°%s′%s″" % (int(lat_degrees), int(lat_minutes), int(lat_seconds))
        lon = u"%s°%s′%s″" % (int(lon_degrees), int(lon_minutes), int(lon_seconds))

        if self.lat > 0:
            lat = lat + 'N'
        else:
            lat = lat + 'S'

        if self.lon > 0:
            lon = lon + 'E'
        else:
            lon = lon + 'W'

        return u"%s %s" % (lat, lon)

    def describe(self):
        if self.description != None:
            return self.description
        import urllib, urllib2
        import simplejson as json
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'adventure_tablet/0.1')]
        try:
            params = urllib.urlencode({'object_type': 'city', 'distance': 'closest', 'around': '%s,%s' % (self.lat, self.lon)})
            url = 'http://geocoding.cloudmade.com/%s/geocoding/v2/find.js?%s' % (self.cloudmade_key, params)
            req = opener.open(url)
            features = req.read()
        except urllib2.HTTPError, e:
            print('Sorry, authorization failed.')
            return self.pretty_print()
        except urllib2.URLError, e:
            print("Connection failed, error %s. Try again later" % (e.message))
            return self.pretty_print()

        try:
            features = json.loads(features)
        except ValueError, e:
            print('Parse error')
            return self.pretty_print()

        if 'features' not in features:
            return self.pretty_print()

        for feature in features['features']:
            self.description = feature['properties']['name']
            return self.description
        return self.pretty_print()

if __name__ == '__main__':
    # Helsinki-Malmi airport
    efhf = point(60.254558, 25.042828)
    print efhf.lat, efhf.lon
    # Midgard airport
    fymg = point(-22.083332, 17.366667)

    distance = efhf.distance_to(fymg)
    distance_n = efhf.distance_to(fymg, 'N')
    bearing = efhf.bearing_to(fymg)
    print("Distance from Helsinki-Malmi (%s) to Midgard Airport (%s) is %s kilometers (%s Nautical miles) %s degrees") % (efhf.describe(), fymg.describe(), int(distance), int(distance_n), bearing)
