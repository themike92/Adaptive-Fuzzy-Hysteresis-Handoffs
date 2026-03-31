#mobile_station.py
#Adam Tremblay - 101264116
#Michael Roy - 

#Represents a mobile station object in the network. Includes spped and connection attributes, as well as movement logic.

import random
import math

#Different speed categories for MSs
STATIONARY = 0
SLOW = 15
FAST = 45
VERY_FAST = 70
SPEEDS = [STATIONARY, SLOW, FAST, VERY_FAST]

# time steps before changing direction
DIRECTION_CHANGE_INTERVAL = 25 

class MobileStation:
    #Initialize a mobile station object 
    #All positions and movement are generate with RNG. This is keep the movement consistent across the different algorithms for fair comparison.
    def __init__(self, id, bounds=(150, 850, 150, 850)):
        
        self.id = id
        self.bounds = bounds
        self.move_rng = random.Random(id)
        
        self.x = self.move_rng.randint(bounds[0], bounds[1]) 
        self.y = self.move_rng.randint(bounds[2], bounds[3])
        
        #probability distribution for speed categories: 5% stationary, 15% slow, 35% fast, 45% very fast
        self.speed = self.move_rng.choices(
            SPEEDS,
            weights=[0.05, 0.15, 0.35, 0.45]
        )[0]
        
        # cache for RSS values to avoid recalculating for the same BS repeatedly, key is BS id, value is RSS
        self.rss_cache = {}  
        
        #determine the direction of the MS (radians)
        self.direction = self.move_rng.uniform(0, 2 * math.pi)
        
        # Internal timer for direction changes
        self._steps_since_direction_change = 0
        
        #current BS, gets updated in sim.py when handoff logic is applied
        self.connected_bs = None
        
        #count the number of handoffs this MS has experienced
        self.handoff_count = 0     
        
        #determine if the current MS has experienced a call drop 
        self.call_dropped  = False
        
        #cooldown timer to prevent excessive handoffs in succession
        self.handoff_cooldown = 0
        
        #call drop counter
        self.drop_count   = 0

        # countdown timer for purple flash
        self.handoff_flash = 0
        
        #countdown timer for red flash
        self.drop_flash = 0
        self._drop_flash_set = False
        
        # position at start of last sim step
        self.prev_x = self.x    
        self.prev_y = self.y  
        
        # position at end of last sim step 
        self.next_x = self.x     
        self.next_y = self.y    
        
    #advance MS by a certain amount each time step, in the same direction for a while
    #Boundary radius is the circle that the MSs bounce off
    def move(self, dt=1, cx=500, cy=500, boundary_radius=450):
        if self.speed == STATIONARY:
            return

        self.prev_x = self.x
        self.prev_y = self.y

        dx = self.speed * math.cos(self.direction) * dt
        dy = self.speed * math.sin(self.direction) * dt

        new_x = self.x + dx
        new_y = self.y + dy

        x_min, x_max, y_min, y_max = 0, 1000, 0, 1000

        # Reflect off horizontal walls
        if new_x < x_min or new_x > x_max:
            self.direction = math.pi - self.direction
            new_x = max(x_min, min(new_x, x_max))

        
        # If on circle boundary, bounce back within the cell cluster
        dist_from_center = math.sqrt((new_x - cx)**2 + (new_y - cy)**2)
        if dist_from_center > boundary_radius:
            angle_to_center = math.atan2(cy - self.y, cx - self.x)
            self.direction = angle_to_center + self.move_rng.uniform(-math.pi / 4, math.pi / 4)

            # take a step in the new direction instead of stopping
            new_x = self.x + self.speed * math.cos(self.direction) * dt
            new_y = self.y + self.speed * math.sin(self.direction) * dt
            # clamp just in case
            new_x = max(0, min(1000, new_x))
            new_y = max(0, min(1000, new_y))

        self.x = new_x
        self.y = new_y

        self.next_x = self.x
        self.next_y = self.y

        #increase the direction change timer and change direction if needed
        self._steps_since_direction_change += 1
        if self._steps_since_direction_change >= DIRECTION_CHANGE_INTERVAL:
            self.change_direction()
            
            
 
    #choose a new random direction and reset the step counter
    def change_direction(self):
        self.direction = self.move_rng.uniform(0, 2 * math.pi)
        self._steps_since_direction_change = 0
    
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
            f"bs={bs_id}, handoffs={self.handoff_count}, flash={self.handoff_flash})"
        )    