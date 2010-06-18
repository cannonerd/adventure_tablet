import Geoclue, point

class adventurer():
    nick = ""
    location = 0.0
    color = ""
    adventure = None
    def __init__(self, nickname):
        self.nick = nickname

    def location(self):
        self.location = Geoclue.DiscoverLocation()
        self.location.init()
        self.location.set_position_provider("hostip")
        coordinates = self.location.get_location_info()
        
        try:
            return point.point(coordinates['latitude'], coordinates['longitude'])
        except KeyError, e:
            #TODO: Define exception for no location
            return point.point()

if __name__ == '__main__':
    suski = adventurer('suski')
    location = suski.location()
    fymg = point.point(-22.083332, 17.366667)
    distance = location.distance_to(fymg)
    print(' %s is in %s, %s %s km from Midgard') % (suski.nick, location.lat, location.lon, int(distance))
