#!/usr/bin/python

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
import math
import gtk.gdk
import gobject
import adventurer, enid

gobject.threads_init()
gtk.gdk.threads_init()

import osmgpsmap

class UI(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

        self.set_default_size(500, 500)
        self.connect('destroy', lambda x: gtk.main_quit())
        self.set_title('the Tablet of Adventure')
        self.vbox = gtk.VBox(False, 0)
        self.add(self.vbox)

        self.osm = osmgpsmap.GpsMap()
        self.osm.connect('button_release_event', self.map_clicked)

        #connect keyboard shortcuts
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_FULLSCREEN, gtk.gdk.keyval_from_name("F11"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_UP, gtk.gdk.keyval_from_name("Up"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_DOWN, gtk.gdk.keyval_from_name("Down"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_LEFT, gtk.gdk.keyval_from_name("Left"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_RIGHT, gtk.gdk.keyval_from_name("Right"))

        self.latlon_entry = gtk.Entry()

        zoom_in_button = gtk.Button(stock=gtk.STOCK_ZOOM_IN)
        zoom_in_button.connect('clicked', self.zoom_in_clicked)
        zoom_out_button = gtk.Button(stock=gtk.STOCK_ZOOM_OUT)
        zoom_out_button.connect('clicked', self.zoom_out_clicked)
        home_button = gtk.Button(stock=gtk.STOCK_HOME)
        home_button.connect('clicked', self.home_clicked)
        destination_button = gtk.Button("Destination")
        destination_button.connect ('clicked', self.destination_clicked)


        self.vbox.pack_start(self.osm)
        hbox = gtk.HBox(False, 0)
        hbox.pack_start(zoom_in_button)
        hbox.pack_start(zoom_out_button)
        hbox.pack_start(home_button)
        hbox.pack_start(destination_button)

        self.vbox.pack_end(hbox, False)

    def zoom_in_clicked(self, button):
        self.osm.set_zoom(self.osm.props.zoom + 1)
 
    def zoom_out_clicked(self, button):
        self.osm.set_zoom(self.osm.props.zoom - 1)

    def home_clicked(self, button):

        self.adventurer = adventurer.adventurer('suski')
        self.location = self.adventurer.location()

        lati = self.location.lat
        longi = self.location.lon

        self.osm.set_mapcenter(lati, longi, 12)

    def destination_clicked(self, button):

        self.adventurer = adventurer.adventurer('suski')
        self.location = self.adventurer.location()

        self.enid = enid.enid()
        mission = self.enid.adventure_from_geohash(self.location)
        lat = mission.destination.lat
        lon = mission.destination.lon

        self.osm.set_mapcenter(lat, lon, 12)


    def map_clicked(self, osm, event):
        if event.button == 1:
            self.latlon_entry.set_text(
                'Map Centre: latitude %s longitude %s' % (
                    self.osm.props.latitude,
                    self.osm.props.longitude
                )
            )
        elif event.button == 2:
            rlat, rlon = self.osm.get_co_ordinates(event.x, event.y)
            self.osm.draw_gps(
                    math.degrees(rlat),
                    math.degrees(rlon),
                    osmgpsmap.INVALID);
 

if __name__ == "__main__":
    u = UI()
    u.show_all()
    gtk.main()
