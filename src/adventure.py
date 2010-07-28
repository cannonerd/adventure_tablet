import point, adventurer, datetime
import _midgard as midgard

class adventure():
    mission = None
    destination = None
    name = ""
    adventurers = []

    def __init__(self, destination, name, mission = None):
        self.destination = destination
        self.name = name
        self.mission = mission

    def add_adventurer(self, adventurer):
        self.adventurers.append(adventurer)
        adventurer.mission_listener = adventurer.connect('location-changed', self.update_log)

    def remove_adventurer(self, adventurer):
        self.adventurers.remove(adventurer)
        adventurer.disconnect(adventurer.mission_listener)

    def update_log(self, adventurer, location, data = None, text = None):
        log = midgard.mgdschema.ttoa_log()
        log.author = adventurer.user.id
        log.mission = self.mission.id
        log.date = datetime.datetime.today()
        log.latitude = location.lat
        log.longitude = location.lon
        if text is not None:
            log.comment = text
        log.participating = True
        log.create()
