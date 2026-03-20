#This will be the code for our mobile stations
import random

STATIONARY = 0
SLOW = 25
FAST = 50
VERY_FAST = 100

SPEEDS = [STATIONARY, SLOW, FAST, VERY_FAST]

class MobileStation:
    def __init__(self, id):
        self.id = id
        self.x = random.randint(0, 1000)
        self.y = random.randint(0, 1000)
        
        self.speed = random.choice(SPEEDS)