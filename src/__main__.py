#instansoin pelaaja enid map
import gameboard, enid, adventurer, datetime, gtk, adventure, point, getpass, hildon
import _midgard as midgard

# Display splash screen while the app initializes
splash = gtk.Window()
splash.set_title('the Tablet of Adventure')
splash_box = gtk.VBox(False, 0)
splash.add(splash_box)
splash_text = gtk.Label("Don't Panic. Here be dragons")
splash_box.pack_start(splash_text, True)
status_text = gtk.Label("Loading...")
splash_box.pack_end(status_text)

# TODO: Display a picture of unicorns, kittens and ponies
hildon.hildon_gtk_window_set_progress_indicator(splash, 1)
splash.show_all()

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
    status_text.set_text("Initializing Midgard database...")
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
    status_text.set_text("Fetching adventures from Qaiku...")
    blyton.adventures_from_qaiku(me.apikey)

# Build adventure list
status_text.set_text("Building list of adventures...")
blyton.refresh_adventures(me)

#prepare and show UI
game = gameboard.UI(blyton, me)
game.show_all()

# Remove the splash screen
hildon.hildon_gtk_window_set_progress_indicator(splash, 0)
splash.destroy()

gtk.main()
