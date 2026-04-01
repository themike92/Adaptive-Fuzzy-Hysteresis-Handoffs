#Group 6
#Adam Tremblay - 101264116
#Michael Roy - 101260953
#Network generation and management

import math
import random

from base_station import BaseStation
from mobile_station import MobileStation

BS_SEED = 12345

class Network:
    #Initialize the network with empty lists of BSs and MSs, and set the grid bounds
    def __init__(self, bounds=(0, 1000, 0, 1000)):
        
        #bounds = (x_min, x_max, y_min, y_max)
        self.bounds          = bounds
        
        #contains all the BSs and MSs in the network
        self.base_stations   = []
        self.mobile_stations = []
    
    #create the base station objects of the network
    #returns a list of the BSs
    def generate_base_stations(self, center_x=500, center_y=500, cell_radius=80, rings=2):
        
        centers = self.generate_hex_centers(center_x, center_y, cell_radius, rings)
        self.base_stations = []

        # fixed seed so BSs are deterministic
        rng = random.Random(BS_SEED)  

        for i, (x, y) in enumerate(centers):
            bs = BaseStation(
                id=i,
                x=x,
                y=y,
                power=rng.uniform(19, 27),
                noise=rng.uniform(1.5, 4.0),
                congestion=rng.uniform(0.3, 0.7),
                coverage_radius=170
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
    #rings is pretty much how many "layers" of BSs there are. We use 2 rings, so in total there are 19 BSs
    def generate_hex_centers(self, center_x, center_y, cell_radius, rings):
        centers = [(center_x, center_y)]
        horiz = math.sqrt(3) * cell_radius

        # The 6 unit-step directions for walking around a ring 
        step_directions = [
            ( horiz,  -cell_radius),   # SE
            ( 0,      -cell_radius*2), # S
            (-horiz,  -cell_radius),   # SW
            (-horiz,   cell_radius),   # NW
            ( 0,       cell_radius*2), # N
            ( horiz,   cell_radius),   # NE
        ]

        for r in range(1, rings + 1):
            # Start position: move r steps north from center
            x = center_x
            y = center_y + r * cell_radius * 2

            # Walk the 6 sides of the ring, r steps per side
            for side, (dx, dy) in enumerate(step_directions):
                for _ in range(r):
                    centers.append((x, y))
                    x += dx
                    y += dy

        return centers
    
    
    #finds the BS with the strongest signal at the MSs location
    def find_strongest_bs(self, ms):
        best_bs  = None
        
        #Start at negative infinity so any real RSS will be better than it
        best_rss = float('-inf')  

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
            candidate_BSs = sorted(
                [bs for bs in self.base_stations 
                if bs.calculate_distance(ms) <= bs.coverage_radius],
                key=lambda b: b.calculate_rss(ms),
                reverse=True
            )
            for bs in candidate_BSs:
                if bs.add_call(ms):
                    ms.connected_bs = bs
                    break
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