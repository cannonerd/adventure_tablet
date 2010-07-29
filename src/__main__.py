#instansoin pelaaja enid map
import gameboard, enid, adventurer, datetime, gtk, adventure, point, getpass, hildon
import _midgard as midgard

# Display splash screen while the app initializes
splash = gtk.Window()
splash.set_title('the Tablet of Adventure')
# TODO: Display a picture of unicorns, kittens and ponies
splash.show()

hildon.hildon_gtk_window_set_progress_indicator(splash, 1)

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
    midgard.storage.create_class_storage('midgard_parameter')

#initialize player for current user and log into Midgard
username = getpass.getuser()
me = adventurer.adventurer(username, True)
#players location
me.get_location()
#initialize game controller
blyton = enid.enid()

if me.apikey is not None:
    # Fetch current adventures from Qaiku
    blyton.adventures_from_qaiku(me.apikey)

# Build adventure list
blyton.refresh_adventures(me)

# Remove the splash screen
hildon.hildon_gtk_window_set_progress_indicator(splash, 0)
splash.destroy()

#prepare and show UI
game = gameboard.UI(blyton, me)

game.show_all()
gtk.main()
