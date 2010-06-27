import math

class point():
    lat = 0.0
    lon = 0.0
    cloudmade_key = 'f4f1cc62bbca426a84fe69fcd27b0498'

    def __init__(self, latitude = 0.0, longitude = 0.0):
        self.lat = float(latitude)
        self.lon = float(longitude)

    def distance_to(self, point):

        start_long = math.radians(self.lon)
        start_latt = math.radians(self.lat)
        end_long = math.radians(point.lon)
        end_latt = math.radians(point.lat)


        d_latt = end_latt - start_latt
        d_long = end_long - start_long
        a = math.sin(d_latt/2)**2 + math.cos(start_latt) * math.cos(end_latt) * math.sin(d_long/2)**2
        c = 2 * math.atan2(math.sqrt(a),  math.sqrt(1-a))
        final = 6371 * c
        return final

    def describe(self):
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
            return ''
        except urllib2.URLError, e:
            print("Connection failed, error %s. Try again later" % (e.message))
            return ''

        try:
            features = json.loads(features)
        except ValueError, e:
            print('Parse error')
            return ''

        if 'features' not in features:
            return ''

        for feature in features['features']:
            return feature['properties']['name']
        return False

if __name__ == '__main__':
    # Helsinki-Malmi airport
    efhf = point(60.254558, 25.042828)

    # Midgard airport
    fymg = point(-22.083332, 17.366667)

    distance = efhf.distance_to(fymg)
    print("Distance from Helsinki-Malmi to Midgard Airport is %s kilometers") % (int(distance))
