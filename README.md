The Tablet of Adventure
=======================

The Tablet of Adventure includes both Geohashed and hand-picked location-based adventures. The Geohashing mode calculates and shows on map the day's Geohashing goal in your area using xkcd's random adventure generating algorithm. You can request the application to show the easiest route to the chosen goal. When you reach your destination you can save a picture from the place and a few thoughts to your adventure log.

You can set the application to alert you if today's Geohashing goal is within your set limitations or when your friends share an adventure.

You can also challenge your friends to take part in an adventure. The inviter sets a goal, and invites friends to join the race. Or one could invite friends to race current day's Geohashing goal. The competitors' location updates would show in your map.

The program is written in Python and developed out in the open using GitHub.

Dependencies
------------

* Python
* PyGTK
* python-osmgpsmap
* python-geoclue (and geoclue-hostip) _or_ python-location
* python-midgard2
* libgda4-sqlite
* python-simplejson

Running Tablet of Adventure
---------------------------

    python src/__main__.py

Building Tablet of Adventure for Maemo
--------------------------------------

* Update the `debian/changelog` file
* Create source package with `$ dpkg-buildpackage -rfakeroot -S -us -uc`
* Upload to <https://garage.maemo.org/extras-assistant/index.php>
* Monitor the build happening on <https://garage.maemo.org/pipermail/extras-cauldron-builds/>
* Check that everything looks correct on <http://maemo.org/packages/view/adventure-tablet/>
