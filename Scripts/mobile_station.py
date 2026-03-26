#This will be the code for our mobile stations
import random

#Different speed categories for MSs
STATIONARY = 0
SLOW = 25
FAST = 50
VERY_FAST = 100
SPEEDS = [STATIONARY, SLOW, FAST, VERY_FAST]

class MobileStation:
    def __init__(self, id):
        #identifier for the mobile station
        self.id = id
        
        #initial random position and speed
        self.x = random.randint(0, 1000)
        self.y = random.randint(0, 1000)
        self.speed = random.choice(SPEEDS)
        
        #current BS, gets updated in sim.py when handoff logic is applied
        self.connected_bs = None
        
        #count the number of handoffs this MS has experienced
        self.handoff_count = 0     
        
        #determine if the current MS has experienced a call drop 
        self.call_dropped  = False
        
    def move(self):
        #Move the mobile station based on its speed
        if self.speed == STATIONARY:
            return
        elif self.speed == SLOW:
            self.x += random.randint(-1, 1)
            self.y += random.randint(-1, 1)
        elif self.speed == FAST:
            self.x += random.randint(-5, 5)
            self.y += random.randint(-5, 5)
        elif self.speed == VERY_FAST:
            self.x += random.randint(-10, 10)
            self.y += random.randint(-10, 10)
        
        #Keep the mobile station within the bounds of the area
        self.x = max(0, min(1000, self.x))
        self.y = max(0, min(1000, self.y))
        
        #MAY WANT TO ADD A DIRECTION COMPONENT TO MOVEMENT TO SIMULATE MORE REALISTIC MOVEMENT PATTERNS, BUT THIS IS GOOD ENOUGH FOR NOW
        #WE CAN ALSO CHANGE HOW THE MS MOVES IN GENERAL IF THERE IS A BETTER WAY
    
    #return what speed the MS is going as a string
    def get_speed_category(self):
        if self.speed == STATIONARY:
            return "stationary"
        elif self.speed == SLOW:
            return "slow"
        elif self.speed == FAST:
            return "fast"
        else:
            return "very_fast"
        
    #helper function that acts as print(ms) to show all the info regarding this MS (special modifiable python function)
    def __repr__(self):
        bs_id = self.connected_bs.id if self.connected_bs else "None"
        return (
            f"MobileStation(id={self.id}, pos=({self.x:.0f},{self.y:.0f}), "
            f"speed={self.speed} [{self.get_speed_category()}], "
            f"bs={bs_id}, handoffs={self.handoff_count})"
        )    