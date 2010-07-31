#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 Copyright (C) Susanna Huhtanen 2010 <ihmis.suski@gmail.com>
 Based on map viewer by:
 Copyright (C) Hadley Rich 2008 <hads@nice.net.nz>
 based on main.c - with thanks to John Stowers

 osm-gps.py is free software: you can redistribute it and/or modify it
 under the terms of the GNU General Public License as published by the
 Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 osm-gps.py is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 See the GNU General Public License for more details.

 You should have received a copy of the GNU General Public License along
 with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import gtk.gdk
import gobject
import adventurer, enid, point, adventure
import os
import sys
import gtk
import hildon
import datetime
import midgard
gobject.threads_init()
gtk.gdk.threads_init()

import osmgpsmap

class UI(hildon.StackableWindow):
    track_location = False
    player = None
    player_colours = ['grey', 'blue', 'red', 'yellow', 'green', 'purple']
    blyton = None
    current_adventure = None
    create_destination = None

    def __init__(self, enid, player):
        win = hildon.StackableWindow.__init__(self)

        self.set_default_size(500, 500)
        self.connect('destroy', gtk.main_quit, None)
        self.set_title('the Tablet of Adventure')

        self.blyton = enid
        self.player = player

        self.build_ui()

        # For now we autoselect the first adventure
        self.select_adventure(self.blyton.adventures[0])

        men = self.create_menu()
        self.set_app_menu(men)
        self.show_all()

        self.destination_clicked(self.destination_button)

    def add_player_to_map(self, adventure, player):
        print "Adding " + player.nick + " to map of " + adventure.name + " to " + player.location.describe()
        banner = hildon.hildon_banner_show_information(self, "", "%s has joined adventure %s" % (player.nick, adventure.name))
        if player.piece is not None:
            # This player is already on the map
            print "  skipping add because player is already on map"
            return
        player.piece = gtk.gdk.pixbuf_new_from_file_at_size (os.path.dirname(__file__) + "/" + player.colour + ".png", 35,35)
        self.osm.add_image(player.location.lat, player.location.lon, player.piece)
        player.gameboard_listener = player.connect('location-changed', self.location_changed)
        print "Subscribed to location updates from %s to adventure %s" % (player.nick, adventure.name)

    def add_players(self):
        for player in self.current_adventure.adventurers:
            self.add_player_to_map(self.current_adventure, player)

    def remove_players(self):
        for player in self.current_adventure.adventurers:
            if player.piece is not None:
                self.osm.remove_image(player.piece)
            player.piece = None
            player.disconnect(player.gameboard_listener)

    def build_ui(self):
        self.hbox = gtk.HBox(False, 0)
        self.add(self.hbox)

        self.osm = osmgpsmap.GpsMap()

        #connect keyboard shortcuts
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_FULLSCREEN, gtk.gdk.keyval_from_name("F11"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_UP, gtk.gdk.keyval_from_name("Up"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_DOWN, gtk.gdk.keyval_from_name("Down"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_LEFT, gtk.gdk.keyval_from_name("Left"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_RIGHT, gtk.gdk.keyval_from_name("Right"))

        self.adventure_selector = gtk.combo_box_new_text()
        self.adventure_selector.append_text('Select adventure:')
        self.adventure_selector_position = 0
        for adventure in self.blyton.adventures:
            self.add_adventure_to_selector(adventure)
        self.adventure_selector.connect('changed', self.changed_adventure)
        self.adventure_selector.set_active(0)


        self.latlon_entry = gtk.Entry()

        self.destination_info = gtk.Label()
        self.destination_info.set_line_wrap(True)
        self.destination_info.set_width_chars(20)

        zoom_in_button = gtk.Button( " + ")
        zoom_in_button.connect('clicked', self.zoom_in_clicked)

        zoom_out_button = gtk.Button(" - ")
        zoom_out_button.connect('clicked', self.zoom_out_clicked)

        start_button = gtk.Button("start")
        start_button.connect('clicked', self.startstop)

        home_image = gtk.Image()
        home_image.set_from_stock(gtk.STOCK_HOME, gtk.ICON_SIZE_BUTTON)
        home_button = gtk.Button()
        home_button.add(home_image)
        home_button.connect('clicked', self.home_clicked)

        destination_image = gtk.Image()
        destination_image.set_from_stock(gtk.STOCK_JUMP_TO, gtk.ICON_SIZE_BUTTON)
        self.destination_button = gtk.Button()
        self.destination_button.add(destination_image)
        self.destination_button.connect ('clicked', self.destination_clicked)

        vbox = gtk.VBox(False, 2)
        vbox.pack_start(self.adventure_selector, expand = False, fill = False)
        vbox.pack_start(start_button, expand = False, fill = False)

        locationbox = gtk.HBox(True, 2)
        zoombox = gtk.HBox(True, 2)
        zoombox.pack_start(zoom_in_button)
        zoombox.pack_start(zoom_out_button)
        locationbox.pack_start(home_button)
        locationbox.pack_start(self.destination_button)
        vbox.pack_start(self.destination_info, padding = 10, fill = False)
        vbox.pack_end(zoombox, expand = False)
        vbox.pack_end(locationbox, expand = False)



        self.hbox.pack_start(vbox, False)
        self.hbox.pack_end(self.osm)

    def startstop(self, button):
        if button.get_label() == "start":
            self.current_adventure.add_adventurer(self.player, True)
            button.set_label("stop")
        else:
            self.player.participating = False
            self.current_adventure.remove_adventurer(self.player)
            button.set_label("start")

    def add_adventure_to_selector(self, adventure):
        self.adventure_selector_position = self.adventure_selector_position + 1
        self.adventure_selector.append_text(adventure.name)
        adventure.combo_index = self.adventure_selector_position

    def select_adventure(self, adventure):
        if self.current_adventure is None:
            # First run, we have to load the target image
            self.target_image = gtk.gdk.pixbuf_new_from_file_at_size (os.path.dirname(__file__) + "/target.png", 24,24)
        else:
            # On later runs we first have to remove old target from map
            self.osm.remove_image(self.target_image)

            # Remove players of previous adventure
            self.current_adventure.disconnect(self.current_adventure.gameboard_listener)
            self.remove_players()

            # Stop polling the old Qaiku feed
            if self.current_adventure.polling_timeout is not None:
                gobject.source_remove(self.current_adventure.polling_timeout)

        self.current_adventure = adventure
        self.osm.add_image(self.current_adventure.destination.lat, self.current_adventure.destination.lon, self.target_image)

        # Add the players of the adventure
        self.add_players()
        self.current_adventure.gameboard_listener = self.current_adventure.connect('adventurer-added', self.add_player_to_map)

        if self.player.apikey is not None:
            # Start polling Qaiku
            self.current_adventure.polling_timeout = gobject.timeout_add(30000, self.current_adventure.logs_from_qaiku, self.player)

    def changed_adventure(self, combobox):
        model = combobox.get_model()
        index = combobox.get_active()
        if index is 0:
            # "Select adventure" selected
            return
        # Check which adventure user selected
        for adventure in self.blyton.adventures:
            if index is adventure.combo_index:
                self.select_adventure(adventure)
                self.destination_clicked(self.destination_button)
                return

    def location_changed(self, adventurer, location, text, qaikuid):
        # FIXME: In newer OsmGpsMap versions we can just move the image
        if text == '':
            text = "New location %s, distance to destination %s" % (location.pretty_print(), location.distance_to(self.current_adventure.destination))
        print text
        if adventurer.piece is not None:
            self.osm.remove_image(adventurer.piece)
        self.osm.add_image(adventurer.location.lat, adventurer.location.lon, adventurer.piece)

        if adventurer.nick == self.player.nick:
            if (self.track_location):
                self.osm.set_mapcenter(location.lat, location.lon, self.osm.props.zoom)
                self.update_description('home')
            else:
                self.update_description('destination')
        else:
            banner= hildon.hildon_banner_show_information(self, "", "%s: %s" %(adventurer.nick, text))
            #TODO: Send an infobubble saying the text of the new location
            pass

    def zoom_in_clicked(self, button):
        self.osm.set_zoom(self.osm.props.zoom + 1)
 
    def zoom_out_clicked(self, button):
        self.osm.set_zoom(self.osm.props.zoom - 1)

    def update_description(self, mode):
        if self.player.location.distance_to(self.current_adventure.destination) <= 0.05:
            description = "Congratulations! you have arrived to your destination."
            self.osm.remove_image(self.target_image)
            self.fin_image = gtk.gdk.pixbuf_new_from_file_at_size (os.path.dirname(__file__) + "/lippu.png", 45,45)
            self.osm.add_image(self.current_adventure.destination.lat, self.current_adventure.destination.lon, self.fin_image)

        elif mode is 'home':
            if int(self.player.location.distance_to(self.current_adventure.destination)) <= 2:
                description = u"You are in %s. Destination is %s km from you, at %s°" %(self.player.location.describe(), round( self.player.location.distance_to(self.current_adventure.destination), 2), self.player.location.bearing_to(self.current_adventure.destination))
            else:
                description = u"You are in %s. Destination is %s km from you, at %s°" %(self.player.location.describe(), int(self.player.location.distance_to(self.current_adventure.destination)), self.player.location.bearing_to(self.current_adventure.destination))
        else:
            if int(self.player.location.distance_to(self.current_adventure.destination)) <= 2:
                description = u"You are in %s. Destination is %s km from you, at %s°" %(self.player.location.describe(), round( self.player.location.distance_to(self.current_adventure.destination), 2), self.player.location.bearing_to(self.current_adventure.destination))
            else:
                description = u"%s is in %s, some %s km from you, at %s°" % (self.current_adventure.name, self.current_adventure.destination.describe(), int(self.player.location.distance_to(self.current_adventure.destination)), self.player.location.bearing_to(self.current_adventure.destination))

        self.destination_info.set_text(description)

    def home_clicked(self, button):
        self.update_description('home')
        self.osm.set_mapcenter(self.player.location.lat, self.player.location.lon, 12)

        self.track_location = True

    def destination_clicked(self, button):
        self.update_description('destination')
        self.track_location = False


        self.osm.set_mapcenter(self.current_adventure.destination.lat, self.current_adventure.destination.lon, 12)

    def create_adventure(self, button):
        wind = hildon.StackableWindow()
        wind.set_title("Plan your adventure")
        label = gtk.Label("Name your adventure")
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(label, expand = False)
        wind.add(vbox)
        self.create_adventure = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        self.create_adventure.set_placeholder("We're Going to...")
#Choose your destination

        self.osms = osmgpsmap.GpsMap()
        self.osms.connect('button_release_event', self.map_info)
        self.osms.add_image(self.osms.props.latitude, self.osms.props.longitude, self.target_image)

        zoom_in_button_choose = gtk.Button( " + ")
        zoom_in_button_choose.connect('clicked', self.zoom_in_clicked_choose)

        zoom_out_button_choose = gtk.Button(" - ")
        zoom_out_button_choose.connect('clicked', self.zoom_out_clicked_choose)


        add = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
        add.set_label("Add")
        add.connect("clicked", self.added)
        vbox.pack_start(self.create_adventure, expand = False)
        vbox.pack_start(self.osms)
        hbox = gtk.HBox(False, 0)
        hbox.pack_start(zoom_in_button_choose, expand = False)
        hbox.pack_start(zoom_out_button_choose, expand = False)
        hbox.pack_end(add, expand = False)
        vbox.pack_end(hbox, expand = False)
        wind.show_all()

    def zoom_in_clicked_choose(self, button):
        self.osms.set_zoom(self.osms.props.zoom + 1)
 
    def zoom_out_clicked_choose(self, button):
        self.osms.set_zoom(self.osms.props.zoom - 1)

    def added(self, button):
        if self.create_destination is None:
            banner= hildon.hildon_banner_show_information(button, "", "You have to choose a destination")
        date = datetime.datetime.today()
        mission = midgard.mgdschema.ttoa_mission()
        mission.type = 2
        mission.text = self.create_adventure.get_text()
        mission.pubDate = date
        mission.validDate = date.replace(hour=23, minute=59, second=59)
        mission.latitude = self.create_destination.lat
        mission.longitude = self.create_destination.lon
        mission.author = self.player.user.id
        mission.create()
        adventure = self.blyton.adventure_from_mission(mission, self.player)
        self.blyton.adventures.append(adventure)
        self.add_adventure_to_selector(adventure)

        if self.player.apikey is not None:
            adventure.adventure_to_qaiku(adventure, self.player.apikey)
        
        # Close the "add" window
        stack = self.get_stack()
        stack.pop(1)

    def map_info(self, osm, event):
        self.create_destination = point.point(osm.props.latitude, osm.props.longitude)
        self.osms.remove_image(self.target_image)
        self.osms.add_image(self.create_destination.lat, self.create_destination.lon, self.target_image)

    def settings(self, button):
        window = hildon.StackableWindow()
        vbox = gtk.VBox(False, 0)
        window.add(vbox)
        window.set_title("Settings")
        label = gtk.Label("Give your Qaiku-api key")
        self.qapikey = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        self.qapikey.set_placeholder("Your Qaiku Apikey is..")


        label1 = gtk.Label("choose colour of your button")

        hbox= gtk.HBox(False, 0)
        
        radioGroup = None
        for colour in self.player_colours:
            colour_pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (os.path.dirname(__file__) + "/"+colour+".png", 80,80)
            colour_image = gtk.Image()
            colour_image.set_from_pixbuf(colour_pixbuf)
            colour_button = gtk.RadioButton(radioGroup)
            if self.player.colour == colour:
                colour_button.set_active(True)
            # Make the selectors look like buttons (Maemo 5 style compatibility, see bug 4578)
            colour_button.set_mode(False)
            if radioGroup is None:
                radioGroup = colour_button
            colour_button.add(colour_image)
            colour_button.connect('toggled', self.change_colour, colour)
            hbox.pack_start(colour_button, expand = False)

        save_button = gtk.Button(" save ")
        save_button.connect('clicked', self.save)

        vbox.pack_start(label, expand = False)
        vbox.pack_start(self.qapikey, expand = False)
        vbox.pack_start (save_button, expand = False)
        vbox.pack_start(label1, expand = False)
        vbox.pack_start (hbox, expand = False)
        window.show_all()

    def save(self, button):

        apikey = self.qapikey.get_text()
        if self.player.check_password(apikey):
            banneri= hildon.hildon_banner_show_information(button, "", "Qaiku api-key saved")
            stack = self.get_stack()
            stack.pop(1)
        else:
            banner= hildon.hildon_banner_show_information(button, "", "Incorrect qaiku api-key")

    def change_colour(self, button, colour):
        if button.get_active() is False:
            return
        self.player.set_colour(colour)
        if self.player.piece is not None:
            self.osm.remove_image(self.player.piece)
        self.player.piece = gtk.gdk.pixbuf_new_from_file_at_size (os.path.dirname(__file__) + "/" +  self.player.colour + ".png", 35,35)
        self.osm.add_image(self.player.location.lat, self.player.location.lon, self.player.piece)

    def log(self, button):
        print "log"
        wido= hildon.StackableWindow()
        vbox= gtk.VBox(False, 0)
        wido.add(vbox)
        wido.set_title("the Log")
        comment = "here be comments"#hae qaikusta

#        qb = midgard.query_builder('ttoa_log')
#        qb.add_constraint('mission', '=', self.current_adventure.mission.id)
#        logs = qb.execute()
#        for log in logs:


        self.qaiku_message = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        self.qaiku_message.set_placeholder("I'finding myself in deep trouble..")
        log_b = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
        log_b.set_label("post to Qaiku")
        log_b.connect("clicked", self.log_button)
        label = gtk.Label (comment)
        vbox.pack_start(label, expand = False)
        vbox.pack_end(log_b, expand = False)
        vbox.pack_end(self.qaiku_message, expand = False)
        wido.show_all()

    def log_button(self, button):

        self.current_adventure.log(self.player, self.player.location, self.qaiku_message.get_text(), '', True
)

        banneri= hildon.hildon_banner_show_information(button, "", "Log has been sent")
        stack = self.get_stack()
        stack.pop(1)


    def about(self, button):
        about_tablet = gtk.AboutDialog()
        about_tablet.set_name("the Tablet of Adventure")
        about_tablet.set_version("version 0.4")
        about_tablet.set_copyright("Map (c) OpenStreetMap and contributors, CC-BY-SA")
        about_tablet.set_website("http://cannonerd.wordpress.com/")

        about_tablet.show_all()

    def create_menu(self):
        self.menu = hildon.AppMenu()

        # Create menu entries
        button = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
        button.set_label("settings")
        button.connect("clicked", self.settings)

        button1 = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
        button1.set_label("create an adventure")
        button1.connect("clicked", self.create_adventure)

        button2 = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
        button2.set_label("log")
        button2.connect("clicked", self.log)

        button3 = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
        button3.set_label("about")
        button3.connect("clicked", self.about)

        # Add entry to the view menu
        self.menu.append(button)
        self.menu.append(button1)
        self.menu.append(button2)
        self.menu.append(button3)

        self.menu.show_all()

        return self.menu

if __name__ == "__main__":
    u = UI()
    u.show_all()
    gtk.main()
