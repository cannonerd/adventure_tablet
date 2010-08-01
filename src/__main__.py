import gameboard, enid, adventurer, datetime, gobject, gtk, adventure, point, getpass, hildon, socket, os
import _midgard as midgard

class adventuretablet(gobject.GObject):

    __gsignals__ = {
        'storage-ready': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))
    }

    def __init__(self):
        gobject.GObject.__init__(self)

        # Display splash screen while the app initializes
        self.splash = gtk.Window()
        self.splash.set_title('the Tablet of Adventure')
        # TODO: Display a picture of unicorns, kittens and ponies
        vbox = gtk.VBox(False, 0)
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.abspath(os.path.dirname(__file__)) + "/blue.png", 200,200)
        image = gtk.Image()
        image.set_from_pixbuf(pixbuf)
        image.show()
        self.status = gtk.Label()
        self.status.set_text("Initializing...")
        self.status.show()
        vbox.pack_start(image)
        vbox.pack_start(self.status)
        self.splash.add(vbox)
        vbox.show()
        self.splash.show()

        # Set a default timeout for our HTTP requests so they don't hang when cell connection is bad
        socket.setdefaulttimeout(10)

        # Tell GLib to prepare Midgard and show game when ready
        self.connect('storage-ready', self.show_game)
        gobject.timeout_add(50, self.prepare_midgard)

        gtk.main()

    def prepare_midgard(self):
        hildon.hildon_gtk_window_set_progress_indicator(self.splash, 1)

        #self.status.set_text("Initializing Midgard connection...")

        # Preparing configuration for using Midgard
        # the SQLite database file will be placed into ~/.midgard2/data/adventuretablet.db
        configuration = midgard.config()
        configuration.dbtype = 'SQLite'
        configuration.database = 'adventuretablet'

        # Open a Midgard repository connection with our config
        connection = midgard.connection()
        if (connection.open_config(configuration) is False):
            print "failed to open midgard connection"
            self.emit('storage-ready', False)
        if (midgard.storage.class_storage_exists('ttoa_user') is False):
            # We only need to do these on the first run: prepare database tables
            #self.status.set_text("Building Midgard database tables on this first run")
            midgard.storage.create_base_storage()
            midgard.storage.create_class_storage('ttoa_user')
            midgard.storage.create_class_storage('ttoa_log')
            midgard.storage.create_class_storage('ttoa_mission')
            midgard.storage.create_class_storage('midgard_parameter')

        self.emit('storage-ready', True)
        # Return false so the timeout is removed
        return False

    def show_game(self, ttoa, storage_ready):
        if not storage_ready:
            exit()

        #initialize player for current user and log into Midgard
        username = getpass.getuser()
        me = adventurer.adventurer(username, True)
        #players location
        me.get_location()
        #initialize game controller
        blyton = enid.enid()

        if me.apikey is not None:
            # Fetch current adventures from Qaiku
            #self.status.set_text("Fetching adventures from Qaiku...")
            blyton.adventures_from_qaiku(me.apikey)

        # Build adventure list
        #self.status.set_text("Starting the game...")
        blyton.refresh_adventures(me)

        #prepare and show UI
        game = gameboard.UI(blyton, me)
        game.show_all()

        # Remove the splash screen
        hildon.hildon_gtk_window_set_progress_indicator(self.splash, 0)
        self.splash.destroy()

ttoa = adventuretablet()
