import point, gobject, adventurer, datetime, urllib, urllib2, simplejson
import _midgard as midgard

class adventure(gobject.GObject):
    mission = None
    destination = None
    qaikuid = None
    name = ""
    adventurers = []
    logs_last_updated = None

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

    def add_adventurer(self, adventurer):
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
            self.log_to_qaiku(self, log, adventurer.apikey)

    def logs_from_qaiku(self, apikey):
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
                params = urllib.urlencode({'apikey': apikey, 'since': since})
            else:
                params = urllib.urlencode({'apikey': apikey})
            url = 'http://www.qaiku.com/api/statuses/replies/%s.json?%s' % (self.qaikuid, params)
            req = opener.open(url)
        except urllib2.HTTPError, e:
            print "HTTP Error %s" % (e.code)
            return
        except urllib2.URLError, e:
            print "Connection failed, error %s" % (e.message)
            return

        messages = simplejson.loads(req.read())
        for message in messages:
            # Check if the adventure already has this player
            print "New log entry from Qaiku for " + self.name
            nick = message['user']['screen_name']
            message_adventurer = None
            for player in self.adventurers:
                if player.nick is nick:
                    message_adventurer = player
                    break
            if message_adventurer is None:
                message_adventurer = adventurer.adventurer(nick)
                self.add_adventurer(message_adventurer)

            message_adventurer.location_changed_qaiku(message)

        self.logs_last_updated = timestamp

    def log_to_qaiku(self, adventure, log, apikey):
        if adventure.qaikuid is None:
            return

        if log.comment is None:
            log.comment = 'Adventuring'

        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'adventure_tablet/0.1')]
        try:
            data = urllib.urlencode({'status': unicode(log.comment).encode('utf-8'), 'source': 'adventuretablet', 'channel': 'adventure', 'latitude': log.latitude, 'longitude': log.longitude, 'in_reply_to_status_id': adventure.qaikuid})
            params = urllib.urlencode({'apikey': apikey})
            url = 'http://www.qaiku.com/api/statuses/update.json?%s' % params
            req = opener.open(url, data)
            response = req.read()
        except urllib2.HTTPError, e:
            print "Updating failed, HTTP %s" % (e.code)
            return
        except urllib2.URLError, e:
            print "Connection failed, error %s" % (e.message)
            return

        qaiku = simplejson.loads(response)
        if qaiku['id']:
            log.set_parameter('adventuretablet', 'qaikuid', qaiku['id'])

    def adventure_to_qaiku(self, adventure, apikey):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'adventure_tablet/0.1')]
        try:
            data = urllib.urlencode({'status': unicode(adventure.name).encode('utf-8'), 'source': 'adventuretablet', 'channel': 'adventure', 'data': '%s,%s' % (adventure.destination.lat, adventure.destination.lon)})
            params = urllib.urlencode({'apikey': apikey})
            url = 'http://www.qaiku.com/api/statuses/update.json?%s' % params
            req = opener.open(url, data)
            response = req.read()
        except urllib2.HTTPError, e:
            print "Updating failed, HTTP %s" % (e.code)
            return
        except urllib2.URLError, e:
            print "Connection failed, error %s" % (e.message)
            return

        qaiku = simplejson.loads(response)
        adventure.set_qaikuid(qaiku['id'])
