#This will be the code for our base stations
import random
import math

# Fuzzy scoring thresholds
RSS_THRESHOLDS  = {"low": -90, "high": -70}   # dBm
SNR_THRESHOLDS  = {"low": 5,   "high": 15}    # dB
LOAD_THRESHOLDS = {"low": 40,  "high": 70}    # % (lower load = better score)
 
# FFDS weights 
FFDS_WEIGHTS = {"rss": 0.4, "snr": 0.35, "load": 0.25}
#These thresholds and weights can be adjusted if needed


#Returns a fuzzy score (0.0 to 1.0) for a given metric value based on defined thresholds
#Value = the measured metric value (RSS, SNR, load)
#low/high_thresh = thresholds for categorizing the metric as low, medium, or high
#invert = True for load since lower load is better, False for RSS and SNR where higher is better
def fuzzy_score(value, low_thresh, high_thresh, invert=False):
    if value <= low_thresh:
        raw = 0.0   # low
    elif value >= high_thresh:
        raw = 1.0   # high
    else:
        raw = 0.5   # medium
 
    # For load, a lower percentage is better, so we flip the score
    return (1.0 - raw) if invert else raw


class BaseStation:
    def __init__(self, id, x, y, power, noise, congestion, max_capacity):
        #unique identifier for the base station
        self.id = id

        #Base station location
        self.x = x
        self.y = y

        self.power = power  #in dBm
        self.noise = noise  
        self.congestion = congestion
        self.max_capacity = max_capacity #max number of simultaneous calls this base station can handle
        
        #minimum guaranteed level of noise that exists for each BS
        self.noise_floor  = -100

        #List of mobile stations currently connected to this base station
        self.active_calls = []


    #add an MS to the list of active calls connected to the BS
    def add_call(self, ms):
        if len(self.active_calls) < self.max_capacity:
            self.active_calls.append(ms)
            return True
        return False

    #remove an MS from the list of active calls when it disconnects or hands off to another BS
    def remove_call(self, ms):
        if ms in self.active_calls:
            self.active_calls.remove(ms)
            return True
        return False
    
    #Return current occupancy as a percentage (0–100).
    def get_cell_load(self):
        return (len(self.active_calls) / self.max_capacity) * 100

    #Euclidean distance between the BS and a given MS
    def calculate_distance(self, ms):
        return math.sqrt((self.x - ms.x)**2 + (self.y - ms.y)**2)

    #Calculate the RSS at the MSs location
    #This is done with a simple path loss model
    def calculate_rss(self, ms):
        distance = self.calculate_distance(ms)
        
        if distance == 0:
            distance = 0.1
        
        path_loss = 10 * 2 * math.log10(distance)
        noise = random.gauss(0, self.noise)
        congestion_penalty = len(self.active_calls) * self.congestion
        
        rss = self.power - path_loss - congestion_penalty + noise
        return rss
    
    #Calculcate the SNR at the MSs location
    #This is where the noise floor is used
    def calculate_snr(self, ms):
        #SNR = RSS − noise_floor
        return self.calculate_rss(ms) - self.noise_floor
    
    
    #Calculate the Full Fuzzy Decision Score for this BS
    #FFDS = w_rss  * score(RSS) + w_snr  * score(SNR) + w_load * score(Load)
    #Returns a value in [0, 1]; higher is better.
    def calculate_ffds(self, ms):
       
        rss  = self.calculate_rss(ms)
        snr  = self.calculate_snr(ms)
        load = self.get_load()
 
        rss_score  = fuzzy_score(rss,  RSS_THRESHOLDS["low"],  RSS_THRESHOLDS["high"],  invert=False)
        snr_score  = fuzzy_score(snr,  SNR_THRESHOLDS["low"],  SNR_THRESHOLDS["high"],  invert=False)
        load_score = fuzzy_score(load, LOAD_THRESHOLDS["low"], LOAD_THRESHOLDS["high"], invert=True)
 
        ffds = (
            FFDS_WEIGHTS["rss"]  * rss_score +
            FFDS_WEIGHTS["snr"]  * snr_score +
            FFDS_WEIGHTS["load"] * load_score
        )
        return ffds
    
    #helper function that acts as print(bs) to show all the info regarding this BS (special modifiable python function)
    def __repr__(self):
        return (
            f"BaseStation(id={self.id}, pos=({self.x:.0f},{self.y:.0f}), "
            f"load={self.get_load():.0f}%, calls={len(self.active_calls)})"
        )