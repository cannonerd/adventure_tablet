#instansoin pelaaja enid map
import gameboard, enid, adventurer, datetime, gtk.gdk
#initialize palyer
me = adventurer.adventurer('me')
#players location
me.get_location()
#initialize game controller
blyton = enid.enid()
#generate an adventure
date = datetime.date.today()
mission = blyton.adventure_from_geohash(me.location, date)
#add plauer to adventure
mission.adventurers.append(me)
#prepare and show UI
game = gameboard.UI(blyton, me)
game.show_all()
gtk.main()
