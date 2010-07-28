import point, adventurer, datetime, urllib, urllib2, simplejson
import _midgard as midgard

class adventure():
    mission = None
    destination = None
    name = ""
    adventurers = []

    def __init__(self, destination, name, mission = None):
        self.destination = destination
        self.name = name
        self.mission = mission

    def add_adventurer(self, adventurer):
        self.adventurers.append(adventurer)
        adventurer.mission_listener = adventurer.connect('location-changed', self.update_log)

    def remove_adventurer(self, adventurer):
        self.adventurers.remove(adventurer)
        adventurer.disconnect(adventurer.mission_listener)

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

    def adventure_to_qaiku(self, adventure, apikey):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'adventure_tablet/0.1')]
        try:
            data = urllib.urlencode({'status': unicode(adventure.text).encode('utf-8'), 'source': 'adventuretablet', 'channel': 'adventure', 'data': '%s,%s' % (adventure.destination.lat, adventure.destination.lon)})
            params = urllib.urlencode({'apikey': apikey})
            url = 'http://www.qaiku.com/api/statuses/update.json?%s' % params
            req = opener.open(url, data)
            response = req.read()
        except urllib2.HTTPError, e:
            print "Updating failed, HTTP %s" % (e.code)
        except urllib2.URLError, e:
            print "Connection failed, error %s" % (e.message)
        print response
