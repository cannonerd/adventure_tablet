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
import adventurer, enid

gobject.threads_init()
gtk.gdk.threads_init()

import osmgpsmap

class UI(gtk.Window):
    track_location = False
    player = None
    blyton = None
    current_adventure = None

    def __init__(self, enid, player):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

        self.set_default_size(500, 500)
        self.connect('destroy', lambda x: gtk.main_quit())
        self.set_title('the Tablet of Adventure')



        self.blyton = enid
        self.player = player
        self.current_adventure = self.blyton.adventures[0]#ei valintaa otetaan ensimmainen
        self.build_ui()
        self.add_players()

        self.destination_clicked(self.destination_button)

    def add_players(self):
        for player in self.current_adventure.adventurers:
            player.connect('location-changed', self.location_changed)

            player.piece = gtk.gdk.pixbuf_new_from_file_at_size ("you.png", 35,35)
            self.osm.add_image(player.location.lat, player.location.lon, player.piece)

        self.target_image = gtk.gdk.pixbuf_new_from_file_at_size ("target.png", 24,24)
        self.osm.add_image(self.current_adventure.destination.lat, self.current_adventure.destination.lon, self.target_image)

    def build_ui(self):
        self.hbox = gtk.HBox(False, 0)
        self.add(self.hbox)

        self.osm = osmgpsmap.GpsMap()
        self.osm.connect('button_release_event', self.map_clicked)

        #connect keyboard shortcuts
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_FULLSCREEN, gtk.gdk.keyval_from_name("F11"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_UP, gtk.gdk.keyval_from_name("Up"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_DOWN, gtk.gdk.keyval_from_name("Down"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_LEFT, gtk.gdk.keyval_from_name("Left"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_RIGHT, gtk.gdk.keyval_from_name("Right"))

        combobox = gtk.combo_box_new_text()
        combobox.append_text('Select adventure:')
        i = 0
        for adventure in self.blyton.adventures:
            i = i + 1
            combobox.append_text(adventure.name)
            adventure.combo_index = i
        combobox.connect('changed', self.changed_adventure)
        combobox.set_active(0)



        self.latlon_entry = gtk.Entry()

        self.destination_info = gtk.Label()
        self.destination_info.set_line_wrap(True)
        self.destination_info.set_width_chars(20)

        zoom_in_button = gtk.Button( " + ")
        zoom_in_button.connect('clicked', self.zoom_in_clicked)

        zoom_out_button = gtk.Button(" - ")
        zoom_out_button.connect('clicked', self.zoom_out_clicked)

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
        vbox.pack_start(combobox, expand = False, fill = False)
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



    def changed_adventure(self, combobox):
        model = combobox.get_model()
        index = combobox.get_active()
        if index is 0:
            # "Select adventure" selected
            return
        # Check which adventure user selected
        for adventure in self.blyton.adventures:
            if index is adventure.combo_index:
                self.current_adventure = adventure
                self.osm.remove_image(self.target_image)
                self.osm.add_image(adventure.destination.lat, adventure.destination.lon, self.target_image)
                self.destination_clicked(self.destination_button)
                return

    def location_changed(self, adventurer, location, data=None):

        # FIXME: In newer OsmGpsMap versions we can just move the image
        self.osm.remove_image(adventurer.piece)
        self.osm.add_image(adventurer.location.lat, adventurer.location.lon, adventurer.piece)

        if (self.track_location):
            self.osm.set_mapcenter(location.lat, location.lon, self.osm.props.zoom)
            self.update_description('home')
        else:
            self.update_description('destination')

    def zoom_in_clicked(self, button):
        self.osm.set_zoom(self.osm.props.zoom + 1)
 
    def zoom_out_clicked(self, button):
        self.osm.set_zoom(self.osm.props.zoom - 1)

    def update_description(self, mode):
        if self.player.location.distance_to(self.current_adventure.destination) <= 0.05:
            description = "Congratulations! you have arrived to your destination."
            self.osm.remove_image(self.target_image)
            self.fin_image = gtk.gdk.pixbuf_new_from_file_at_size ("lippu.png", 45,45)
            self.osm.add_image(self.current_adventure.destination.lat, self.current_adventure.destination.lon, self.fin_image)

        elif mode is 'home':
            description = u"You are in %s. Destination is %s km from you, in %s°" %(self.player.location.describe(), int(self.player.location.distance_to(self.current_adventure.destination)), self.player.location.bearing_to(self.current_adventure.destination))
        else:
            description = u"%s is in %s, some %s km from you, in %s°" % (self.current_adventure.name, self.current_adventure.destination.describe(), int(self.player.location.distance_to(self.current_adventure.destination)), self.player.location.bearing_to(self.current_adventure.destination))

        self.destination_info.set_text(description)

    def home_clicked(self, button):
        self.update_description('home')
        self.osm.set_mapcenter(self.player.location.lat, self.player.location.lon, 12)

        self.track_location = True

    def destination_clicked(self, button):
        self.update_description('destination')
        self.track_location = False


        self.osm.set_mapcenter(self.current_adventure.destination.lat, self.current_adventure.destination.lon, 12)

    def map_clicked(self, osm, event):
        if event.button == 1:
            self.latlon_entry.set_text(
                'Map Centre: latitude %s longitude %s' % (
                    self.osm.props.latitude,
                    self.osm.props.longitude
                )
            )



if __name__ == "__main__":
    u = UI()
    u.show_all()
    gtk.main()
