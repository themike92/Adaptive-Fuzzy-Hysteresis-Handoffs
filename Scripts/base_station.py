
#Group 6
#Adam Tremblay - 101264116
#Michael Roy - 101260953

#This will be the code for our base stations
import random
import math

#Fuzzy scoring thresholds
RSS_THRESHOLDS  = {"low": -40, "high": -10}   # dBm
SNR_THRESHOLDS  = {"low": 63,  "high": 68}    # dB
LOAD_THRESHOLDS = {"low": 20, "high": 80}    # %
 
#FFDS weights 
FFDS_WEIGHTS    = {"rss": 0.40, "snr": 0.40, "load": 0.20}
#These thresholds and weights can be adjusted if needed

#Load limit that base stations will use to determine what percentage of the cpacity they are at
REFERENCE_LOAD = 15

#Returns a fuzzy score (0.0 to 1.0) for a given metric value based on defined thresholds
#Value = the measured metric value (RSS, SNR, load)
#low/high_thresh = thresholds for categorizing the metric as low, medium, or high
#invert = True for load since lower load is better, False for RSS and SNR where higher is better
def fuzzy_score(value, low_thresh, high_thresh, invert=False):
    #If it falls in high or low then it will become either 0 or 1 otherwise it will be between 0 and 1
    if value <= low_thresh:
        score = 0.0
    elif value >= high_thresh:
        score = 1.0
    else:
        score = (value - low_thresh) / (high_thresh - low_thresh)

    if invert:
        score = 1.0 - score
    return score

#Our base station object that will be created in the network
class BaseStation:
    # It has an id, location (x,y), power, noise level, congestion level, and coverage radius
    def __init__(self, id, x, y, power, noise, congestion, coverage_radius):
        #Unique identifier for the base station
        self.id = id

        #Base station location
        self.x = x
        self.y = y

        self.power = power  #in dBm
        self.noise = noise  
        self.congestion = congestion
        self.coverage_radius = coverage_radius
        
        #minimum guaranteed level of noise that exists for each BS
        self.noise_floor  = -100

        #List of mobile stations currently connected to this base station
        self.active_calls = []


    #Add an MS to the list of active calls connected to the BS
    def add_call(self, ms):
        #Checks to see if it exceeds the load limits
        if len(self.active_calls) >= REFERENCE_LOAD:
            return False  # refuse connection, MS stays unconnected or tries next BS
        #Connects to bs and has a call with that bs
        self.active_calls.append(ms)
        return True
    
    
    #Remove an MS from the list of active calls when it disconnects or hands off to another BS
    def remove_call(self, ms):
        if ms in self.active_calls:
            self.active_calls.remove(ms)
            return True
        return False
       
    
    #Return current number of calls as a percentage of the load limit
    def get_load(self):
        return (len(self.active_calls) / REFERENCE_LOAD) * 100


    #Distance between the BS and a given MS
    def calculate_distance(self, ms):
        return math.sqrt((self.x - ms.x)**2 + (self.y - ms.y)**2)



    #Calculate the RSS at the MSs location
    #This is done with a path loss model
    def calculate_rss(self, ms):
        
        distance = self.calculate_distance(ms)
        #Has to have a minimum distance so we dont get infinite values
        if distance == 0:
            distance = 0.1
        
        #Free space path loss equation
        path_loss = 10 * 2.0 * math.log10(distance)
        noise = random.gauss(0, self.noise)
        congestion_penalty = len(self.active_calls) * self.congestion
        
        #Simplified RSS model for simulation, does not need wavelength or frequency
        rss = self.power - path_loss - congestion_penalty + noise
        return rss
    
    #Returns the cached RSS for the ms on that base station
    def get_cached_rss(self, ms):
        return ms.rss_cache.get(self.id, float('-inf'))
    
    #Calculcate the SNR at the MSs location
    def calculate_snr(self, ms):
        #SNR = RSS − noise_floor

        #Uses the MSs cached RSS on this BS and find the noise on the base station to find the difference
        cached_rss = self.get_cached_rss(ms)
        effective_noise_floor = self.noise_floor + (self.get_load() * 0.285)
        return cached_rss - effective_noise_floor
    
    #Calculate the Full Fuzzy Decision Score for this BS
    #Returns a value in [0, 1]. higher is better 
    #Load score is inverted since for that lower is better
    def calculate_ffds(self, ms):
        rss  = self.get_cached_rss(ms)
        snr  = self.calculate_snr(ms)
        load = self.get_load()

        #Get the fuzzy scores for the metrics
        rss_score  = fuzzy_score(rss,  RSS_THRESHOLDS["low"],  RSS_THRESHOLDS["high"],  False)
        snr_score  = fuzzy_score(snr,  SNR_THRESHOLDS["low"],  SNR_THRESHOLDS["high"],  False)
        load_score = fuzzy_score(load, LOAD_THRESHOLDS["low"], LOAD_THRESHOLDS["high"], True)

        #Set the score for the ffds (It will be between 0 and 1)
        ffds = (
            FFDS_WEIGHTS["rss"]  * rss_score +
            FFDS_WEIGHTS["snr"]  * snr_score +
            FFDS_WEIGHTS["load"] * load_score
        )
        return ffds
    
    #Helper function that acts as print(bs) to show all the info regarding this BS (special modifiable python function)
    def __repr__(self):
        return (
            f"BaseStation(id={self.id}, pos=({self.x:.0f},{self.y:.0f}), "
            f"load={self.get_load():.0f}%, calls={len(self.active_calls)})"
        )
