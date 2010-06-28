import point, gobject

class adventurer(gobject.GObject):
    nick = ""
    color = ""
    adventure = None
    location = None

    __gsignals__ = {
        'location-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
    }

    def __init__(self, nickname):
        gobject.GObject.__init__(self)
        self.nick = nickname

    def get_location(self):
        try:
            import Geoclue
            self.get_location_geoclue()

        except ImportError:
            try:
                # We are probably on Maemo 5, try using liblocation
                import location
                self.get_location_liblocation()
            except ImportError:
                self.location = point.point()

    def get_location_liblocation(self):
        import location
        control = location.GPSDControl.get_default()
        device = location.GPSDevice()
        control.set_properties(preferred_method=location.METHOD_USER_SELECTED,
            preferred_interval=location.INTERVAL_DEFAULT)

        device.connect("changed", self.location_changed_liblocation, control)
        # We don't have a location yet, return blank point
        self.location = point.point()

    def location_changed_liblocation(self, device, data):
        if not device:
            return
        if device.fix:
            if device.fix[1] & location.GPS_DEVICE_LATLONG_SET:
                self.location = point.point(device.fix[4], device.fix[6])
                data.stop()
            self.emit('location-changed', self.location)

    def get_location_geoclue(self):
        import Geoclue
        self.geoclue = Geoclue.DiscoverLocation()
        self.geoclue.init()
        self.geoclue.set_position_provider("hostip")
        coordinates = self.geoclue.get_location_info()
        self.geoclue.position.connect_to_signal("PositionChanged", self.location_changed_geoclue)

        try:
            self.location = point.point(coordinates['latitude'], coordinates['longitude'])
        except KeyError, e:
            #TODO: Define exception for no location
            self.location = point.point()

    def location_changed_geoclue(self, fields, timestamp, latitude, longitude, altitude, accuracy):
        self.location = point.point(latitude, longitude)
        self.emit('location-changed', self.location)

if __name__ == '__main__':
    suski = adventurer('suski')
    suski.get_location()
    if (suski.location):
        fymg = point.point(-22.083332, 17.366667)
        distance = suski.location.distance_to(fymg)
        print(' %s is in %s, %s %s km from Midgard') % (suski.nick, suski.location.lat, suski.location.lon, int(distance))
    else:
        print('We did not get location yet')
