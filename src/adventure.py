import point, adventurer, datetime, urllib, urllib2, simplejson
import _midgard as midgard

class adventure():
    mission = None
    destination = None
    qaikuid = None
    name = ""
    adventurers = []

    def __init__(self, destination, name, mission = None):
        self.destination = destination
        self.name = name
        self.mission = mission
        if self.mission is not None:
            self.qaikuid = self.mission.get_parameter('adventuretablet', 'qaikuid')

    def add_adventurer(self, adventurer):
        self.adventurers.append(adventurer)
        adventurer.mission_listener = adventurer.connect('location-changed', self.update_log)

    def remove_adventurer(self, adventurer):
        self.adventurers.remove(adventurer)
        adventurer.disconnect(adventurer.mission_listener)

    def set_qaikuid(self, qaikuid):
        self.qaikuid = qaikuid
        if self.mission is not None:
            self.mission.set_parameter('adventuretablet', 'qaikuid', qaikuid)

    def update_log(self, adventurer, location, data = None, text = None):
        log = midgard.mgdschema.ttoa_log()
        log.author = adventurer.user.id
        log.mission = self.mission.id
        log.date = datetime.datetime.today()
        log.latitude = location.lat
        log.longitude = location.lon
        if text is not None:
            log.comment = text
        log.participating = True
        log.create()
        if adventurer.apikey is not None:
            self.log_to_qaiku(self, log, adventurer.apikey)

    def log_to_qaiku(self, adventure, log, apikey):
        if adventure.qaikuid is None:
            return

        if log.comment == '':
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
