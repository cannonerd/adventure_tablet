import point, gobject
import _midgard as midgard

location = None
Geoclue = None
try:
    import Geoclue
except ImportError:
    try:
        import location
    except ImportError:
        print "No location service found"

class adventurer(gobject.GObject):
    nick = ""
    color = ""
    adventure = None
    location = None
    user = None

    __gsignals__ = {
        'location-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
    }

    def __init__(self, nickname, login = False):
        gobject.GObject.__init__(self)

        if login is True:
            self.init_midgard_session(nickname)

        # Every adventurer has a ttoa_user record, check if it already exists
        qb = midgard.query_builder('ttoa_user')
        qb.add_constraint('username', '=', nickname)
        if qb.count() is 0:
            # No user yet in database, create it
            self.user = midgard.mgdschema.ttoa_user()
            self.user.username = nickname
            self.user.create()
        else:
            users = qb.execute()
            for user in users:
                self.user = user

        self.nick = nickname

    def init_midgard_session(self, nickname):
        # Ensure we have a corresponding Midgard user record
        try:
            self.mgduser = midgard.db.user({'login': nickname, 'authtype': 'APIkey'})
        except:
            self.mgduser = midgard.db.user()
            self.mgduser.login = nickname
            self.mgduser.authtype = 'APIkey'
            self.mgduser.active = True
            self.mgduser.create()
        # Initialize a Midgard session for the user
        self.mgduser.log_in()

    def get_location(self):
        if Geoclue:
            self.get_location_geoclue()
        elif location:
           self.get_location_liblocation()
        else:
           self.location = point.point()

    def get_location_liblocation(self):
        self.control = location.GPSDControl.get_default()
        self.device = location.GPSDevice()
        self.control.set_properties(preferred_method=location.METHOD_USER_SELECTED,
            preferred_interval=location.INTERVAL_10S)

        # We don't have a location yet, return blank point
        self.location = point.point()

        self.control.connect("error-verbose", self.location_error_liblocation, None)
        self.device.connect("changed", self.location_changed_liblocation, self.control)
        self.control.start()
        if self.device.fix:
            if self.device.fix[1] & location.GPS_DEVICE_LATLONG_SET:
                # We have a "hot" fix
                self.location = point.point(self.device.fix[4], self.device.fix[5])
                self.log_location_change()

    def location_error_liblocation(self, control, error):
        print "location error: %d" % error
        self.control.quit()

    def location_changed_liblocation(self, device, control):
        if not self.device:
            return
        if self.device.fix:
            if self.device.fix[1] & location.GPS_DEVICE_LATLONG_SET:
                self.location = point.point(self.device.fix[4], self.device.fix[5])
            self.log_location_change()
            self.emit('location-changed', self.location)

    def get_location_geoclue(self):
        self.geoclue = Geoclue.DiscoverLocation()
        self.geoclue.init()
        self.geoclue.set_position_provider("hostip")
        coordinates = self.geoclue.get_location_info()
        self.geoclue.position.connect_to_signal("PositionChanged", self.location_changed_geoclue)

        try:
            self.location = point.point(coordinates['latitude'], coordinates['longitude'])
            self.log_location_change()
        except KeyError, e:
            #TODO: Define exception for no location
            self.location = point.point()

    def location_changed_geoclue(self, fields, timestamp, latitude, longitude, altitude, accuracy):
        self.location = point.point(latitude, longitude)
        self.log_location_change()
        self.emit('location-changed', self.location)

    def log_location_change(self):
        # Update user record
        self.user.latitude = self.location.lat
        self.user.longitude = self.location.lon
        self.user.update()
        # TODO: Create a log entry if we're in an adventure?

if __name__ == '__main__':
    suski = adventurer('suski')
    suski.get_location()
    if (suski.location):
        fymg = point.point(-22.083332, 17.366667)
        distance = suski.location.distance_to(fymg)
        print(' %s is in %s, %s %s km from Midgard') % (suski.nick, suski.location.lat, suski.location.lon, int(distance))
    else:
        print('We did not get location yet')
