#This will be the code for our mobile stations
import random
import math

#Different speed categories for MSs
STATIONARY = 5
SLOW = 15
FAST = 55
VERY_FAST = 90
SPEEDS = [STATIONARY, SLOW, FAST, VERY_FAST]

# time steps before changing direction
DIRECTION_CHANGE_INTERVAL = 25 

class MobileStation:
    def __init__(self, id, bounds=(235, 765, 235, 765)):
        #identifier for the mobile station
        self.id = id
        self.bounds = bounds

        #initial random position and speed
        #make sure the MS start in the range of the BSs
        self.x = random.randint(bounds[0], bounds[1]) 
        self.y = random.randint(bounds[2], bounds[3])
        self.speed = random.choices(
            SPEEDS,
            weights=[0.05, 0.2, 0.4, 0.35]
        )[0]
        
        
        #determine the direction of the MS (radians)
        self.direction = random.uniform(0, 2 * math.pi)  
        # Internal timer for direction changes
        self._steps_since_direction_change = 0
        
        #current BS, gets updated in sim.py when handoff logic is applied
        self.connected_bs = None
        
        #count the number of handoffs this MS has experienced
        self.handoff_count = 0     
        
        #determine if the current MS has experienced a call drop 
        self.call_dropped  = False
        
        #call drop counter
        self.drop_count   = 0

        # countdown timer for purple flash
        self.handoff_flash = 0
        
        self.prev_x = self.x    # position at start of last sim step
        self.prev_y = self.y    # position at start of last sim step
        self.next_x = self.x    # position at end of last sim step  
        self.next_y = self.y    # position at end of last sim step
        
    #advance MS by a certain amount each time step, in the same direction for a while
    #Boundary radius is the circle that the MSs bounce off
    #MSs refelct either off the walls, or the circle boundary
    def move(self, dt=1, cx=500, cy=500, boundary_radius=415):
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

        # Reflect off vertical walls
        if new_y < y_min or new_y > y_max:
            self.direction = -self.direction
            new_y = max(y_min, min(new_y, y_max))

        
        # If on circle boundary, bounce back within the cell cluster
        dist_from_center = math.sqrt((new_x - cx)**2 + (new_y - cy)**2)
        if dist_from_center > boundary_radius:
            angle_to_center = math.atan2(cy - self.y, cx - self.x)
            self.direction  = angle_to_center + random.uniform(-math.pi / 4, math.pi / 4)
            # Don't move this step, just redirect
            new_x = self.x
            new_y = self.y

        self.x = new_x
        self.y = new_y

        self.next_x = self.x
        self.next_y = self.y

        self._steps_since_direction_change += 1
        if self._steps_since_direction_change >= DIRECTION_CHANGE_INTERVAL:
            self.change_direction()
 
    #choose a new random direction and reset the step counter
    def change_direction(self):
        self.direction = random.uniform(0, 2 * math.pi)
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