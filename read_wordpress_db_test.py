from collections import namedtuple, defaultdict


StationContact = namedtuple('StationContact', 'name, email')

tom = StationContact('Tom Kooij', 'tkooij@nikhef.nl')
kasper = StationContact('Kasper van Dam', 'kaspervd@nikhef.nl')

contacts = {501: [kasper, tom], 599: [tom], 7: [tom]}

def get_station_contacts():
    return contacts


if __name__ == '__main__':
    print(get_station_contacts())
