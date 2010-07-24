import point

class adventure():
    mission = None
    destination = None
    name = ""
    adventurers = []

    def __init__(self, destination, name, mission = None):
        self.destination = destination
        self.name = name
        self.mission = mission


