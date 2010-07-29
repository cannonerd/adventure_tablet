import point, gobject, adventurer, datetime, urllib, urllib2, simplejson
import _midgard as midgard

class adventure(gobject.GObject):
    mission = None
    destination = None
    qaikuid = None
    name = ""
    adventurers = []
    logs_last_updated = None
    last_log_position = {}
    polling_timeout = None

    __gsignals__ = {
        'adventurer-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
    }

    def __init__(self, destination, name, mission = None):
        gobject.GObject.__init__(self)
        self.destination = destination
        self.name = name
        self.mission = mission
        if self.mission is not None:
            self.qaikuid = self.mission.get_parameter('adventuretablet', 'qaikuid')

    def add_adventurer(self, adventurer, participating = False):
        adventurer.participating = participating
        self.adventurers.append(adventurer)
        adventurer.mission_listener = adventurer.connect('location-changed', self.log)
        self.emit('adventurer-added', adventurer)

    def remove_adventurer(self, adventurer):
        self.adventurers.remove(adventurer)
        adventurer.disconnect(adventurer.mission_listener)

    def set_qaikuid(self, qaikuid):
        self.qaikuid = qaikuid
        if self.mission is not None:
            self.mission.set_parameter('adventuretablet', 'qaikuid', qaikuid)

    def log(self, adventurer, location, text, qaikuid):
        if adventurer.participating is False:
            return

        if adventurer.nick in self.last_log_position:
            # Only log if sufficient distance has been covered
            distance_to_destination = self.destination.distance_to(location)
            distance_from_last = self.last_log_position[adventurer.nick].distance_to(location)
            if (distance_to_destination > 2):
                if distance_from_last < 0.5:
                    return
            else:
                if distance_from_last < 0.2:
                    return
        self.last_log_position[adventurer.nick] = location

        if qaikuid != '':
            qb = midgard.query_builder('ttoa_log')
            qb.add_constraint('mission', '=', self.mission.id)
            qb.add_constraint('parameter.value', '=', qaikuid)
            if qb.count() != 0:
                # We already have this log entry
                return

        log = midgard.mgdschema.ttoa_log()
        log.author = adventurer.user.id
        log.mission = self.mission.id
        log.date = datetime.datetime.today()
        log.latitude = location.lat
        log.longitude = location.lon
        if text != '':
            log.comment = text
        log.participating = True
        log.create()
        if qaikuid != '':
            # This message is coming from Qaiku
            log.set_parameter('adventuretablet', 'qaikuid', qaikuid)
        elif adventurer.apikey is not None:
            # This message needs to be sent to Qaiku
            self.log_to_qaiku(self, log, adventurer)

    def logs_from_qaiku(self, player):
        if self.qaikuid is None:
            return

        if self.mission is None:
            return

        timestamp = datetime.datetime.today()
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'adventure_tablet/0.1')]
        try:
            if self.logs_last_updated is not None:
                since = self.logs_last_updated.strftime('%Y-%m-%d %H:%M:%S')
                params = urllib.urlencode({'apikey': player.apikey, 'since': since})
            else:
                params = urllib.urlencode({'apikey': player.apikey})
            url = 'http://www.qaiku.com/api/statuses/replies/%s.json?%s' % (self.qaikuid, params)
            req = opener.open(url)
        except urllib2.HTTPError, e:
            print "logs_from_qaiku: HTTP Error %s" % (e.code)
            return
        except urllib2.URLError, e:
            print "logs_from_qaiku: Connection failed, error %s" % (e.message)
            return

        messages = simplejson.loads(req.read())
        for message in messages:
            if isinstance(message['geo'], dict) is False:
                # Log without a location, skip
                return

            # Parse QaikuData
            colour = None
            if message['data'] != '':
                qaikudata = message['data'].split(',')
                if len(qaikudata) == 3:
                    message['geo']['coordinates'][1] = float(qaikudata[0])
                    message['geo']['coordinates'][0] = float(qaikudata[1])
                    colour = qaikudata[2]

            # Check if the adventure already has this player
            nick = message['user']['screen_name']
            message_adventurer = None
            for player in self.adventurers:
                if player.nick == nick:
                    message_adventurer = player
                    break
            if message_adventurer is None:
                message_adventurer = adventurer.adventurer(nick)
                if colour is not None:
                    if message_adventurer.colour != colour:
                        message_adventurer.set_colour(colour)
                message.adventurer.location = point.point(message['geo']['coordinates'][1], message['geo']['coordinates'][0])
                self.add_adventurer(message_adventurer, True)

            message_adventurer.location_changed_qaiku(message)

        self.logs_last_updated = timestamp

    def log_to_qaiku(self, adventure, log, adventurer):
        if adventure.qaikuid is None:
            print "  No QaikuID for adventure"
            return
        self.current_adventure = adventure
        if log.comment is None:
            apikey = adventurer.apikey
            log.comment = 'Adventuring to %s, distance to destination %s km' %(adventure.destination.describe(), int(adventurer.location.distance_to(adventure.destination)))

        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'adventure_tablet/0.1')]
        try:
            data = urllib.urlencode({
                'status': unicode(log.comment).encode('utf-8'),
                'source': 'adventuretablet',
                'lat': log.latitude,
                'long': log.longitude,
                'in_reply_to_status_id': adventure.qaikuid,
                'data': '%s,%s,%s' % (log.latitude, log.longitude, adventurer.colour)
            })
            params = urllib.urlencode({'apikey': apikey})
            url = 'http://www.qaiku.com/api/statuses/update.json?%s' % params
            req = opener.open(url, data)
            response = req.read()
        except urllib2.HTTPError, e:
            print "log_to_qaiku: Updating failed, HTTP %s" % (e.code)
            return
        except urllib2.URLError, e:
            print "log_to_qaiku: Connection failed, error %s" % (e.message)
            return

        qaiku = simplejson.loads(response)
        if qaiku['id']:
            log.set_parameter('adventuretablet', 'qaikuid', qaiku['id'])

    def adventure_to_qaiku(self, adventure, apikey):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'adventure_tablet/0.1')]
        try:
            data = urllib.urlencode({
                'status': unicode(adventure.name).encode('utf-8'),
                'source': 'adventuretablet',
                'channel': 'adventure',
                'data': '%s,%s' % (adventure.destination.lat, adventure.destination.lon)
            })
            params = urllib.urlencode({'apikey': apikey})
            url = 'http://www.qaiku.com/api/statuses/update.json?%s' % params
            req = opener.open(url, data)
            response = req.read()
        except urllib2.HTTPError, e:
            print "adventure_to_qaiku: Updating failed, HTTP %s" % (e.code)
            return
        except urllib2.URLError, e:
            print "adventure_to_qaiku: Connection failed, error %s" % (e.message)
            return

        qaiku = simplejson.loads(response)
        adventure.set_qaikuid(qaiku['id'])
