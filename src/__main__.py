#instansoin pelaaja enid map
import gameboard, enid, adventurer, datetime, gtk.gdk, adventure, point, getpass
import _midgard as midgard

# TODO: We should display the TToA splash screen now

# Preparing configuration for using Midgard
# the SQLite database file will be placed into ~/.midgard2/data/adventuretablet.db
configuration = midgard.config()
configuration.dbtype = 'SQLite'
configuration.database = 'adventuretablet'

# Open a Midgard repository connection with our config
connection = midgard.connection()
if (connection.open_config(configuration) is False):
    print "failed to open midgard connection"
    exit()
if (midgard.storage.class_storage_exists('ttoa_user') is False):
    # We only need to do these on the first run: prepare database tables
    midgard.storage.create_base_storage()
    midgard.storage.create_class_storage('ttoa_user')
    midgard.storage.create_class_storage('ttoa_log')
    midgard.storage.create_class_storage('ttoa_mission')

#initialize player for current user and log into Midgard
username = getpass.getuser()
me = adventurer.adventurer(username, True)
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

# TODO: We should hide the TToA splash screen

game.show_all()
gtk.main()
