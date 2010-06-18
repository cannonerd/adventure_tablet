import adventure, hashlib, datetime, struct, urllib, re, point

class enid():
    adventures = []

    def adventure_from_geohash(self, location):
        date = datetime.date.today()
        destination = self.geohash(location, date)
        mission = adventure.adventure(destination, "Today's Geohash")
        return mission

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
    mission = blyton.adventure_from_geohash(location)
    print("%s, your mission, if you choose to accept it, is:") % (suski.nick)
    print("  %s is in %s (%s, %s), some %s km away from you") % (mission.name, mission.destination.describe(), mission.destination.lat, mission.destination.lon, int(location.distance_to(mission.destination)))
