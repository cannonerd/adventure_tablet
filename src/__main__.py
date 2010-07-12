#instansoin pelaaja enid map
import gameboard, enid, adventurer, datetime, gtk.gdk, adventure, point
#initialize palyer
me = adventurer.adventurer('me')
#players location
me.get_location()
#initialize game controller
blyton = enid.enid()
#generate an adventure
date = datetime.date.today()
mission = blyton.adventure_from_geohash(me.location, date)
#test mission

efhf = point.point(60.249418, 25.045655)
malmi = adventure.adventure(efhf, "Go to Malmi!")
blyton.adventures.append(malmi)

#add plauer to adventure
mission.adventurers.append(me)
#prepare and show UI
game = gameboard.UI(blyton, me)
game.show_all()
gtk.main()
