import adventure, hashlib, datetime, struct, urllib, re, point
import _midgard as midgard

class enid():
    adventures = []

    def __init__(self, location):
        self.refresh_adventures(location)

    def refresh_adventures(self, location):
        # Clear old list of adventures
        self.adventures = []

        # Fetch currently valid adventures from Midgard
        today = datetime.datetime.today()
        today.microsecond = 0
        qb = midgard.query_builder('ttoa_mission')
        qb.add_constraint('validDate', '>=', today.isoformat())
        geohash_found = False
        missions = qb.execute()
        for mission in missions:
            if mission.type is 1:
                geohash_found = True
            self.adventures.append(self.adventure_from_mission(mission))

        if geohash_found is False:
            # We didn't have a GeoHash for today yet, generate one
            self.adventures.append(self.adventure_from_geohash(location, today))

    def adventure_from_mission(self, mission):
        target = point.point(mission.latitude, mission.longitude)
        mission_adventure = adventure.adventure(target, mission.text, mission)
        return mission_adventure

    def adventure_from_geohash(self, location, date):
        destination = self.geohash(location, date)
        mission = midgard.mgdschema.ttoa_mission()
        mission.type = 1
        mission.text = "Today's Geohash"
        mission.pubDate = date.isoformat()
        mission.validDate = date.replace(hour=23, minute=59, second=59).isoformat()
        mission.latitude = destination.lat
        mission.longitude = destination.lon
        mission.create()
        return self.adventure_from_mission(mission)

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
