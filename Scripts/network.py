#any network generation and logic seperate from the simulation
import math
import random

from base_station import BaseStation
from mobile_station import MobileStation

class Network:
    
    def __init__(self, bounds=(0, 1000, 0, 1000)):
        #bounds = (x_min, x_max, y_min, y_max)
        self.bounds          = bounds
        
        #contains all the BSs and MSs in the network
        self.base_stations   = []
        self.mobile_stations = []
    
    #build the base station objects of the network
    #returns a list of the BSs
    def generate_base_stations(self, center_x=500, center_y=500, cell_radius=130, rings=1):
        
        centers = self.generate_hex_centers(center_x, center_y, cell_radius, rings)
        self.base_stations = []
 
        # Predefined base station configurations
        configs = [
            {"power": 25, "noise": 2.2, "congestion": 0.5},
            {"power": 27, "noise": 1.8, "congestion": 0.5},
            {"power": 22, "noise": 2.5, "congestion": 0.6},
            {"power": 25, "noise": 1.5, "congestion": 0.7},
            {"power": 20, "noise": 4.0, "congestion": 0.4},
            {"power": 23, "noise": 3.0, "congestion": 0.5},
            {"power": 19, "noise": 2.7, "congestion": 0.3},
        ]

        for i, (x, y) in enumerate(centers):
            config = configs[i]

            bs = BaseStation(
                id=i,
                x=x,
                y=y,
                power=config["power"],
                noise=config["noise"],
                congestion=config["congestion"],
                coverage_radius=250
            )

            self.base_stations.append(bs)
 
        return self.base_stations

    #build each MS object in the Network
    #returns a list of the MSs
    def generate_mobile_stations(self, num):
        self.mobile_stations = []
        
        for i in range(num):
            ms = MobileStation(id=i)
            self.mobile_stations.append(ms)
        
        return self.mobile_stations
    
    
    #places the BSs on a hexogonal grid
    #rings is pretty much how many "layers" of BSs there are (rings = 1 means 7 BSs)
    #We'll keep it hardcoded at 7 for now, but we can easily change it to generate more if needed
    def generate_hex_centers(self, center_x, center_y, cell_radius, rings=1):
        centers = [(center_x, center_y)]  # center of the BSs
        
        if rings >= 1:
            horiz = math.sqrt(3) * cell_radius

            directions = [
                (0,       cell_radius * 2),
                (horiz,   cell_radius),
                (horiz,  -cell_radius),
                (0,      -cell_radius * 2),
                (-horiz, -cell_radius),
                (-horiz,  cell_radius),
            ]
                        
            for dx, dy in directions:
                centers.append((center_x + dx, center_y + dy))
        
        return centers
        
        #If we want to add more rings:
        #if R == 2:
    
    
    #finds the BS with the strongest signal at the MSs location
    def find_strongest_bs(self, ms):
        best_bs  = None
        best_rss = float('-inf')  # start at negative infinity so any real RSS beats it

        for bs in self.base_stations:
            if bs.calculate_distance(ms) > bs.coverage_radius:
                continue
                
            rss = bs.calculate_rss(ms)
            if rss > best_rss:
                best_rss = rss
                best_bs  = bs

        return best_bs
    
    
    #returns a list of all the neighboring BSs to a given BS
    def get_neighbor_stations(self, bs, ms=None):
        neighbors = []
        for b in self.base_stations:
            if b.id == bs.id:
                continue
            if ms and b.calculate_distance(ms) > b.coverage_radius:
                continue  # skip BSs out of range
            neighbors.append(b)
        return neighbors
    
    
    
    #Determine initial connections for all MSs at the start of the simulation
    def initial_connections(self):
        for ms in self.mobile_stations:
            best_bs = self.find_strongest_bs(ms)
            
            #See if we can add the MS to the BS with the strongest signal
            if best_bs and best_bs.add_call(ms):
                ms.connected_bs = best_bs
            else:
                #BS is full, gotta try the next one
                candidate_BSs = sorted(
                    [bs for bs in self.base_stations 
                    if math.sqrt((bs.x - ms.x)**2 + (bs.y - ms.y)**2) <= bs.coverage_radius],
                    key=lambda b: b.calculate_rss(ms),
                    reverse=True
                )
        #If no BS is avaliable, the MS stays unconnected (nothing changes from their default value)
        
        
    
    
    #Print functions 
    #Network topology summary:
    def print_summary(self):
        print(f"\n{'='*50}")
        print(f"Network Summary")
        print(f"  Grid bounds  : {self.bounds}")
        print(f"  Base stations: {len(self.base_stations)}")
        print(f"  Mobile units : {len(self.mobile_stations)}")
        print(f"{'-'*50}")
        for bs in self.base_stations:
            print(f"  {bs}")
        print(f"{'='*50}\n")
    
    #print out the details of the Network on the fly   
    def __repr__(self):
        return (
            f"Network(bs={len(self.base_stations)}, "
            f"ms={len(self.mobile_stations)}, bounds={self.bounds})"
        )