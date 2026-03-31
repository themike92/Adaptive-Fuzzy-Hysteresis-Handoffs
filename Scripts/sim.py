#Simulation file, uses simpy to run our simulation
#This is where all handoff logic (baseline, adaptive, and fuzzy) will be determined and applies

import random
#RANDOM_SEED = 42
RANDOM_SEED = 12345

import simpy
from network import Network
from base_station import BaseStation
from mobile_station import MobileStation
from visual import Visualizer
from results import Results

#Hysteresis constants. All H values are in dBm
H_FIXED = 9             # fixed margin used by the baseline algorithm
H_DEF   = 9             # default margin for adaptive and fuzzy algorithms
H_MIN   = 1             # minimum margin so it never gets too small
H_MAX   = 12            # maximum margin so it never gets too large
K       = 0.1           # sensitivity constant, controls how much speed affects the margin

# Drop threshold, in dBm
RSS_DROP_THRESHOLD = -32
SNR_DROP_THRESHOLD = 44

# Simulation defaults
SIM_DURATION = 200
SIM_INTERVAL = 50

def ms_process(env, ms, network, algorithm, results):
    while True:
        ms.move()
        
        # Refresh RSS cache once per time step so all comparisons use consistent values
        ms.rss_cache = {bs.id: bs.calculate_rss(ms) for bs in network.base_stations}
        
        if ms.connected_bs is not None:
            if algorithm == "baseline":
                target = baseline_handoff_decision(ms, network)

            elif algorithm == "adaptive":
                target = adaptive_hysteresis_handoff_decision(ms, network)

            elif algorithm == "fuzzy":
                target = fuzzy_handoff_decision(ms, network)
            
            if target:
                perform_handoff(ms, target, env.now, results)
            
            
        dropped = check_call_drop(ms, env.now, results)
        
        if dropped:
            # try to reconnect if a BS is in range
            best_bs = network.find_strongest_bs(ms)
            if best_bs:
                best_bs.add_call(ms)
                ms.connected_bs = best_bs
                ms.call_dropped = False  # reconnected, reset dropped flag
            
        yield env.timeout(1)
       

#ALGORITHM 1, BASELINE
#Decide whether to handoff using a fixed hysteresis (H_FIXED) and a basic RSS comparison
def baseline_handoff_decision(ms, network):
    
    if ms.connected_bs is None:
        # If not currently connected, try to connect to the strongest BS
        best_bs = network.find_strongest_bs(ms)
        if best_bs and best_bs.calculate_rss(ms) > RSS_DROP_THRESHOLD:
            best_bs.add_call(ms)
            ms.connected_bs = best_bs 
        return None
    
    current_rss = ms.connected_bs.get_cached_rss(ms)
    neighboring_bss = network.get_neighbor_stations(ms.connected_bs,ms)
    
    #Find the best BS in the list of neighbors
    best_targetBS = None
    RSS_to_beat = current_rss + H_FIXED
    
    #Compare the RSS of each neighboring BS, select the best one
    for bs in neighboring_bss:
        rss = bs.get_cached_rss(ms) 
        if rss > RSS_to_beat:
            RSS_to_beat = rss
            best_targetBS = bs
            
    return best_targetBS
    
    
#ALGORITHM 2, ADAPTIVE HYSTERESIS
#Calculate the adaptive margin based on the MSs speed
#Decide whether or not the handoff decision should be made based on the adaptive margin and the RSS  

def calculate_adaptive_H_Value(ms):
    value = H_DEF - K * ms.speed
    
    if value < H_MIN:
        value = H_MIN
    elif value > H_MAX:
        value = H_MAX
        
    return value

def adaptive_hysteresis_handoff_decision(ms, network):
    
    if ms.connected_bs is None:
        # If not currently connected, try to connect to the strongest BS
        best_bs = network.find_strongest_bs(ms)
        if best_bs and best_bs.calculate_rss(ms) > RSS_DROP_THRESHOLD:
            best_bs.add_call(ms)
            ms.connected_bs = best_bs 
        return None
    
    adaptive_H_margin = calculate_adaptive_H_Value(ms)
    
    current_rss = ms.connected_bs.get_cached_rss(ms) 
    neighboring_bss = network.get_neighbor_stations(ms.connected_bs, ms)
    
    #Find the best BS in the list of neighbors
    #The RSS to beat is now using the adaptive hysteresis margin instead of the fixed value
    best_targetBS = None
    RSS_to_beat = current_rss + adaptive_H_margin
    
    #Compare the RSS of each neighboring BS, select the best one
    for bs in neighboring_bss:
        rss = bs.get_cached_rss(ms) 
        if rss > RSS_to_beat:
            RSS_to_beat = rss
            best_targetBS = bs
            
    return best_targetBS

#TO DO NEXT
#ALGORITHM 3, FUZZY QOS + ADAPTIVE HYSTERESIS
#Calculate the FFDS for each neighboring BS, select the one with the highest score
#Also calculate the adaptive hysteresis margin

def fuzzy_handoff_decision(ms, network):
    
    if ms.connected_bs is None:
        best_bs = network.find_strongest_bs(ms)
        if best_bs and best_bs.calculate_rss(ms) > RSS_DROP_THRESHOLD:
            best_bs.add_call(ms)
            ms.connected_bs = best_bs
        return None
    
    adaptive_H_margin = calculate_adaptive_H_Value(ms)
    current_rss       = ms.connected_bs.get_cached_rss(ms)
    neighboring_bss   = network.get_neighbor_stations(ms.connected_bs, ms)

    # step 1 — find candidate BSs that beat the adaptive margin
    # this is the same gate as adaptive hysteresis
    candidates = []
    for bs in neighboring_bss:
        rss = bs.get_cached_rss(ms)
        if rss > current_rss + adaptive_H_margin:
            candidates.append(bs)

    if not candidates:
        return None

    # step 2 — among candidates, pick the one with the highest FFDS score
    # this is where fuzzy adds quality awareness over pure RSS
    best_targetBS  = None
    best_ffds      = -1

    for bs in candidates:
        ffds = bs.calculate_ffds(ms)
        if ffds > best_ffds:
            best_ffds     = ffds
            best_targetBS = bs

    return best_targetBS


#HELPER FUNCTION: PERFORM HANDOFF
#disconnect from current BS, then connect to the new target BS
#time = env.now simpy variable
#results = We can create a results class to store all the relevant info regarding handoffs, call drops, etc. that we can use for analysis after the simulation is done
def perform_handoff(ms, target_bs, time, results):
    old_BS = ms.connected_bs
    
    #disconnect the MS from the current BS
    old_BS.remove_call(ms)
    
    if target_bs.add_call(ms):
        ms.connected_bs = target_bs
        ms.handoff_count += 1
        ms.handoff_flash = 2

        if results:
            results.record_handoff(time, ms, old_BS, target_bs)
        
        #This is just what logging could look like when we get there (placeholder for now)
    else:
        #target BS is full, stay on old BS
        old_BS.add_call(ms)
        
    
    
    
#HELPER FUNCTION: CHECK FOR CALL DROP
#checks to see if the MSs current RSS has fallen below the drop threshold
# if so, mark the call as dropped and disconnect
def check_call_drop(ms, curr_time, results):
    
    if ms.connected_bs is None:
        ms.call_dropped = True
        return True

    curr_rss = ms.connected_bs.get_cached_rss(ms)
    curr_snr = ms.connected_bs.calculate_snr(ms)

    # if curr_snr < SNR_DROP_THRESHOLD:
    #     print(f"SNR DROP MS-{ms.id} rss={curr_rss:.1f} snr={curr_snr:.1f} load={ms.connected_bs.get_load():.1f}%")

    if results:
        results.record_rss(curr_time, ms, curr_rss)
        results.record_snr(curr_time, ms, curr_snr)

    rss_drop        = curr_rss < RSS_DROP_THRESHOLD
    snr_drop        = curr_snr < SNR_DROP_THRESHOLD

    if rss_drop or snr_drop:
        ms.connected_bs.remove_call(ms)
        ms.connected_bs = None
        ms.call_dropped = True
        ms.drop_count   += 1
        ms.drop_flash = 2
        ms._drop_flash_set = True
        
        if rss_drop:
            reason = "rss"
        elif snr_drop:
            reason = "snr"

        if results:
            results.record_call_drop(curr_time, ms, reason)

        return True

    return False

def generate_network(num_ms):
    random.seed(RANDOM_SEED)
    network = Network()
    network.generate_base_stations()
    network.generate_mobile_stations(num_ms)
    
    for ms in network.mobile_stations:
        ms.initial_x         = ms.x
        ms.initial_y         = ms.y
        ms.initial_speed     = ms.speed
        ms.initial_direction = ms.direction
        ms.initial_steps     = ms._steps_since_direction_change
        
    return network

def reset_network(network):
    random.seed(RANDOM_SEED)

    for bs in network.base_stations:
        bs.active_calls = []

    for ms in network.mobile_stations:
        # reset the movement RNG to its original seed so movement is identical
        ms.move_rng = random.Random(ms.id)

        # restore full movement state to initial snapshot
        ms.x         = ms.initial_x
        ms.y         = ms.initial_y
        ms.speed     = ms.initial_speed
        ms.direction = ms.initial_direction
        ms._steps_since_direction_change = ms.initial_steps

        ms.connected_bs  = None
        ms.call_dropped  = False
        ms.drop_count    = 0
        ms.handoff_count = 0
        ms.handoff_flash = 0
        ms.drop_flash    = 0
        ms.prev_x        = ms.x
        ms.prev_y        = ms.y
        ms.next_x        = ms.x
        ms.next_y        = ms.y
        ms.rss_cache     = {}


def _build_env(network, algorithm, results):
    env = simpy.Environment()
    network.initial_connections()
    network.print_summary()
    
    for ms in network.mobile_stations:
        env.process(ms_process(env, ms, network, algorithm, results))
    
    def load_logger(env):
        while True:
            for bs in network.base_stations:
                if results:
                    results.record_load(env.now, bs)
            yield env.timeout(1)

    env.process(load_logger(env))
    return env

def run_all_simulations(network):
    algorithms = ["baseline", "adaptive", "fuzzy"]
    all_results = {}
    
    for algorithm in algorithms:
        print(f"\nRunning {algorithm}...")
        reset_network(network)
        
        results = Results(algorithm)
        env     = _build_env(network, algorithm, results)
        
        env.run(until=SIM_DURATION)
        
        print(f"  Complete — {len(network.mobile_stations)} MSs, {SIM_DURATION} steps")
        
        all_results[algorithm] = results
    
    return all_results


def run_visual_simulation(algorithm, network):
    results = Results(algorithm)
    env     = _build_env(network, algorithm, results)
    
    
    viz = Visualizer(network, cell_radius=80, signal_radius=170)
    
    def sim_step():
        next_time = env.now + 1
        while env.peek() <= next_time and env.peek() < float('inf'):
            env.step()
    
    viz.start(sim_step, SIM_INTERVAL, SIM_DURATION)

    # window closed, print summary
    print(f"\nSimulation complete.")
    print(f"  Algorithm : {algorithm}")
    print(f"  Duration  : {SIM_DURATION} time steps")
    print(f"  MSs       : {len(network.mobile_stations)}")
    
    results.print_summary(network.mobile_stations)