import math

class point():
    lat = 0.0
    lon = 0.0

    def __init__(self, latitude = 0.0, longitude = 0.0):
        self.lat = float(latitude)
        self.lon = float(longitude)

    def distance_to(self, point):

        start_long = math.radians(self.lon)
        start_latt = math.radians(self.lat)
        end_long = math.radians(point.lon)
        end_latt = math.radians(point.lat)


        d_latt = end_latt - start_latt
        d_long = end_long - start_long
        a = math.sin(d_latt/2)**2 + math.cos(start_latt) * math.cos(end_latt) * math.sin(d_long/2)**2
        c = 2 * math.atan2(math.sqrt(a),  math.sqrt(1-a))
        final = 6371 * c
        return final

if __name__ == '__main__':
    # Helsinki-Malmi airport
    efhf = point(60.254558, 24.042828)

    # Midgard airport
    fymg = point(-22.083332, 17.366667)

    distance = efhf.distance_to(fymg)
    print("Distance from Helsinki-Malmi to Midgard Airport is %s kilometers") % (int(distance))
