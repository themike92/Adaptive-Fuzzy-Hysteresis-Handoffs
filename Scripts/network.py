#any network generation and logic seperate from the simulation
import math

from base_station import BaseStation
from mobile_station import MobileStation

def generate_base_stations(num_cells):
    MAX_CAPACITY = 20
    base_stations = []
    for i in range(num_cells):
        bs = BaseStation(id=i, x=0, y=0, power=100, noise=2, congestion=1, max_capacity=MAX_CAPACITY)
        base_stations.append(bs)
    return base_stations

def generate_mobile_stations(num):
    mobile_stations = []
    for i in range(num):
        ms = MobileStation(id=i)
        mobile_stations.append(ms)
    return mobile_stations

def generate_hex_centers(center_x, center_y, R):
    centers = [(center_x, center_y)]  # center BS
    
    for i in range(6):
        angle = math.radians(60 * i)  # 6 directions, 60 degrees apart
        x = center_x + R * math.cos(angle)
        y = center_y + R * math.sin(angle)
        centers.append((x, y))   
    return centers