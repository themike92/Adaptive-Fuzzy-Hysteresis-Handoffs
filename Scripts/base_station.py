#This will be the code for our base stations
import random
import math

# Fuzzy scoring thresholds
RSS_THRESHOLDS  = {"low": -65, "high": -50}   # dBm
SNR_THRESHOLDS  = {"low": 15,  "high": 30}    # dB  (SNR = RSS - noise_floor(-100), so range is ~35-55)
LOAD_THRESHOLDS = {"low": 45, "high": 75}    # %
 
# FFDS weights 
FFDS_WEIGHTS = {"rss": 0.70, "snr": 0.12, "load": 0.18}
#These thresholds and weights can be adjusted if needed

REFERENCE_LOAD = 22

#Returns a fuzzy score (0.0 to 1.0) for a given metric value based on defined thresholds
#Value = the measured metric value (RSS, SNR, load)
#low/high_thresh = thresholds for categorizing the metric as low, medium, or high
#invert = True for load since lower load is better, False for RSS and SNR where higher is better
def fuzzy_score(value, low_thresh, high_thresh, invert=False):
    if value <= low_thresh:
        score = 0.0   # low
    elif value >= high_thresh:
        score = 1.0   # high
    else:
        score = 0.5   # medium
 
    # For load, a lower percentage is better, so we flip the score
    if invert == True:
        return 1.0 - score
    else:
        return score


class BaseStation:
    def __init__(self, id, x, y, power, noise, congestion, coverage_radius):
        #unique identifier for the base station
        self.id = id

        #Base station location
        self.x = x
        self.y = y

        self.power = power  #in dBm
        self.noise = noise  
        self.congestion = congestion
        
        #minimum guaranteed level of noise that exists for each BS
        self.noise_floor  = -100

        #List of mobile stations currently connected to this base station
        self.active_calls = []

        self.coverage_radius = coverage_radius


    #add an MS to the list of active calls connected to the BS
    def add_call(self, ms):
        if len(self.active_calls) >= REFERENCE_LOAD:
            return False  # refuse connection, MS stays unconnected or tries next BS
        self.active_calls.append(ms)
        return True
    
    

    #remove an MS from the list of active calls when it disconnects or hands off to another BS
    def remove_call(self, ms):
        if ms in self.active_calls:
            self.active_calls.remove(ms)
            return True
        return False
       
    
    #Return current occupancy
    def get_load(self):
        return (len(self.active_calls) / REFERENCE_LOAD) * 100


    #Euclidean distance between the BS and a given MS
    def calculate_distance(self, ms):
        return math.sqrt((self.x - ms.x)**2 + (self.y - ms.y)**2)



    #Calculate the RSS at the MSs location
    #This is done with a path loss model
    def calculate_rss(self, ms):
        
        distance = self.calculate_distance(ms)
        if distance == 0:
            distance = 0.1
        
        path_loss = 10 * 4.0 * math.log10(distance)
        noise = random.gauss(0, self.noise)
        congestion_penalty = len(self.active_calls) * self.congestion
        
        rss = self.power - path_loss - congestion_penalty + noise
        return rss
    
    def get_cached_rss(self, ms):
        return ms.rss_cache.get(self.id, float('-inf'))
    
    #Calculcate the SNR at the MSs location
    #This is where the noise floor is used
    def calculate_snr(self, ms):
        #SNR = RSS − noise_floor

        cached_rss = self.get_cached_rss(ms)
        effective_noise_floor = self.noise_floor + (self.get_load() * 0.25)
        return cached_rss - effective_noise_floor
    
    #Calculate the Full Fuzzy Decision Score for this BS
    #Returns a value in [0, 1]. higher is better. Load score is inverted since for that lower is better
    def calculate_ffds(self, ms):
        rss  = self.get_cached_rss(ms)
        snr  = self.calculate_snr(ms)   # use dynamic SNR not static noise_floor
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