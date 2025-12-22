class Room:
    def __init__(self, humidity, temperature):
        self.humidity = humidity
        self.temperature = temperature

class Electronics:
    def __init__(self):
        pass
    def use(self, room, hour):
        pass

class Humidifier(Electronics):
    def __init__(self):
        super().__init__()
        self.humidity = 3
    def use(self, room, hour):
        room.humidity += hour * self.humidity

class Heater(Electronics):
    def __init__(self):
        super().__init__()
        self.humidity = 5
        self.temperature = 2
    def use(self, room, hour):
        room.humidity -= hour * self.humidity
        room.temperature += hour * self.temperature

def solution(humidity, temperature, hour):
    room = Room(humidity, temperature)
    humidifier = Humidifier()
    heater = Heater()
    humidifier.use(room, hour)
    heater.use(room, hour)
    return [room.humidity, room.temperature]
