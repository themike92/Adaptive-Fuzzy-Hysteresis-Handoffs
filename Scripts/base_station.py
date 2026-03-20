#This will be the code for our base stations
import random
import math

class BaseStation:
    def __init__(self, id, x, y, power, noise, congestion, max_capacity):
        self.id = id

        #Base station location
        self.x = x
        self.y = y

        self.power = power
        self.noise = noise
        self.congestion = congestion
        self.max_capacity = max_capacity

        #List of mobile stations currently connected to this base station
        self.active_calls = []



    def add_call(self, ms):
        if len(self.active_calls) < self.max_capacity:
            self.active_calls.append(ms)
            return True
        return False

    def remove_call(self, ms):
        if ms in self.active_calls:
            self.active_calls.remove(ms)
            return True
        return False

    def calculate_distance(self, ms):
        return math.sqrt((self.x - ms.x)**2 + (self.y - ms.y)**2)

    def calculate_rss(self, ms):
        distance = self.calculate_distance(ms)
        
        if distance == 0:
            distance = 0.1
        
        path_loss = 10 * 2 * math.log10(distance)
        noise = random.gauss(0, self.noise)
        congestion_penalty = len(self.active_calls) * self.congestion
        
        rss = self.power - path_loss - congestion_penalty + noise
        return rss