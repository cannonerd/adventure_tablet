import adventure, adventurer, hashlib, datetime, struct, urllib, urllib2, simplejson, re, point, math
import _midgard as midgard

class enid():
    adventures = []
    last_updated = None

    def refresh_adventures(self, adventurer):
        # Clear old list of adventures
        self.adventures = []

        # Fetch currently valid adventures from Midgard
        location = adventurer.location
        today = datetime.datetime.today()
        today = today.replace(microsecond=0)
        qb = midgard.query_builder('ttoa_mission')
        qb.add_constraint('validDate', '>=', today.isoformat(' '))
        geohash_found = False
        missions = qb.execute()
        for mission in missions:
            if (mission.type is 1) and (int(math.floor(mission.latitude)) == int(math.floor(location.lat))) and (int(math.floor(mission.longitude)) == int(math.floor(location.lon))):
                # We have a geohash for today and current graticule
                geohash_found = True
            self.adventures.append(self.adventure_from_mission(mission, adventurer))

        if geohash_found is False:
            # We didn't have a GeoHash for today yet, generate one
            self.adventures.append(self.adventure_from_geohash(adventurer, today))

    def adventures_from_qaiku(self, apikey):
        timestamp = datetime.datetime.today()
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'adventure_tablet/0.1')]
        try:
            if self.last_updated is not None:
                since = self.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                params = urllib.urlencode({'apikey': apikey, 'since': since})
            else:
                params = urllib.urlencode({'apikey': apikey})
            url = 'http://www.qaiku.com/api/statuses/channel_timeline/adventure.json?%s' % (params)
            req = opener.open(url)
        except urllib2.HTTPError, e:
            print "adventures_from_qaiku: HTTP Error %s" % (e.code)
            return
        except urllib2.URLError, e:
            print "adventures_from_qaiku: Connection failed, error %s" % (e.message)
            return

        messages = simplejson.loads(req.read())
        for message in messages:
            if message['in_reply_to_status_id']:
                # This is a log entry or comment, we're only interested in adventures
                continue

            if message['data'] == '':
                # No QaikuData found, we need this for our adventure
                continue

            qb = midgard.query_builder('ttoa_mission')
            qb.add_constraint('parameter.value', '=', message['id'])
            if qb.count() != 0:
                # We already have this adventure
                continue

            mission = midgard.mgdschema.ttoa_mission()
            mission.type = 2
            mission.text = message['text']
            mission.pubDate = timestamp
            mission.validDate = timestamp.replace(hour=23, minute=59, second=59)
            qaikudata = message['data'].split(',')
            if len(qaikudata) != 2:
                # Invalid mission coordinates, skip
                continue
            mission.latitude = float(qaikudata[0])
            mission.longitude = float(qaikudata[1])
            mission.create()
            mission.set_parameter('adventuretablet', 'qaikuid', message['id'])

        self.last_updated = timestamp

    def adventure_from_mission(self, mission, player):
        target = point.point(mission.latitude, mission.longitude)
        mission_adventure = adventure.adventure(target, mission.text, mission)

        # Check for adventurers
        adventurers = []
        qb = midgard.query_builder('ttoa_log')
        qb.add_constraint('mission', '=', mission.id)
        logs = qb.execute()
        for log in logs:
            if log.author not in adventurers:
                adventurers.append(log.author)
        for participant in adventurers:
            user = midgard.mgdschema.ttoa_user()
            user.get_by_id(participant)
            if user.username == player.nick:
                # We don't add the current player to adventures, they do so manually
                continue
            else:
                mission_adventure.add_adventurer(adventurer.adventurer(user.username), True)

        return mission_adventure

    def adventure_from_geohash(self, adventurer, datetime):
        location = adventurer.location
        destination = self.geohash(location, datetime.date())
        mission = midgard.mgdschema.ttoa_mission()
        mission.type = 1
        mission.text = "Geohash for %s, %s" % (int(math.floor(destination.lat)), int(math.floor(destination.lon)))
        mission.pubDate = datetime
        mission.validDate = datetime.replace(hour=23, minute=59, second=59)
        mission.latitude = destination.lat
        mission.longitude = destination.lon
        mission.create()
        return self.adventure_from_mission(mission, adventurer)

    def geohash(self, location, date):
        args = []
        args.append(int(location.lat))
        args.append(int(location.lon))
        if args[1] < -30:
            td30 = 0
        else:
            td30 = 1
        if args[0] < 0:
            south = -1
        else:
            south = 1
        if args[1] < 0:
            west = -1
        else:
            west = 1
        djia = urllib.urlopen((date - datetime.timedelta(td30)).strftime("http://irc.peeron.com/xkcd/map/data/%Y/%m/%d")).read()
        if '404 Not Found' in djia:
            # FIXME: Throw an exception here instead
            print("Dow Jones not available yet.")
        sum = hashlib.md5("%s-%s" % (date, djia)).digest()
        n, w = [str(d*(abs(a)+f)) for d, f, a in zip((south, west),
            [x/2.**64 for x in struct.unpack_from(">QQ", sum)], args[0:])]
        geohash = point.point(n, w)
        return geohash

if __name__ == '__main__':
    import adventurer
    suski = adventurer.adventurer('suski')
    location = suski.location()
    blyton = enid()
    date = datetime.date.today()
    mission = blyton.adventure_from_geohash(location, date)
    print("%s, your mission, if you choose to accept it, is:") % (suski.nick)
    print("  %s is in %s (%s, %s), some %s km away from you") % (mission.name, mission.destination.describe(), mission.destination.lat, mission.destination.lon, int(location.distance_to(mission.destination)))
