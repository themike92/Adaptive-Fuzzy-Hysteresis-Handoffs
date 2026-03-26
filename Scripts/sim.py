#Simulation file, uses simpy to run our simulation
#This is where all handoff logic (baseline, adaptive, and fuzzy) will be determined and applies

import simpy
from network import Network
from base_station import BaseStation
from mobile_station import MobileStation
from visual import Visualizer

#Hysteresis constants. All H values are in dBm
H_FIXED = 5             # fixed margin used by the baseline algorithm
H_DEF   = 8             # default margin for adaptive and fuzzy algorithms
H_MIN   = 2             # minimum margin so it never gets too small
H_MAX   = 10            # maximum margin so it never gets too large
K       = 0.06          # sensitivity constant, controls how much speed affects the margin

# Drop threshold, in dBm
RSS_DROP_THRESHOLD = -95    

def ms_process(env, ms, network, algorithm):
    while True:
        ms.move()
        
        dropped = check_call_drop(ms, env.now, results=None)
        
        if not dropped:
            if algorithm == "baseline":
                target = baseline_handoff_decision(ms, network)
            elif algorithm == "adaptive":
                target = adaptive_hysteresis_handoff_decision(ms, network)
            
            if target:
                perform_handoff(ms, target, env.now, results=None)
        
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
    
    current_rss = ms.connected_bs.calculate_rss(ms)
    neighboring_bss = network.get_neighbor_stations(ms.connected_bs)
    
    #Find the best BS in the list of neighbors
    best_targetBS = None
    RSS_to_beat = current_rss + H_FIXED
    
    #Compare the RSS of each neighboring BS, select the best one
    for bs in neighboring_bss:
        rss = bs.calculate_rss(ms)
        if rss > RSS_to_beat:
            RSS_to_beat = rss
            best_targetBS = bs
            
    return best_targetBS
    
    
    
    
#ALGORITHM 2, ADAPTIVE HYSTERESIS
#Calculate the adaptive margin based on the MSs speed
#Decide whether or not the handoff decision should be made based on the adaptive margin and the RSS  

def calculate_adaptive_H_Value(ms):
    value = H_DEF + K * ms.speed
    
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
    
    current_rss = ms.connected_bs.calculate_rss(ms)
    neighboring_bss = network.get_neighbor_stations(ms.connected_bs)
    
    #Find the best BS in the list of neighbors
    #The RSS to beat is now using the adaptive hysteresis margin instead of the fixed value
    best_targetBS = None
    RSS_to_beat = current_rss + adaptive_H_margin
    
    #Compare the RSS of each neighboring BS, select the best one
    for bs in neighboring_bss:
        rss = bs.calculate_rss(ms)
        if rss > RSS_to_beat:
            RSS_to_beat = rss
            best_targetBS = bs
            
    return best_targetBS





#TO DO NEXT
#ALGORITHM 3, FUZZY QOS + ADAPTIVE HYSTERESIS
#Calculate the FFDS for each neighboring BS, select the one with the highest score
#Also calculate the adaptive hysteresis margin







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
        
        #This is just what logging could look like when we get there (placeholder for now)
        #results.record_handoff(time, ms, old_BS, target_bs)
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
    
    curr_rss = ms.connected_bs.calculate_rss(ms)
    
    if curr_rss < RSS_DROP_THRESHOLD:
        ms.connected_bs.remove_call(ms)
        ms.connected_bs = None
        ms.call_dropped = True
        
        #logging
        #results.record_call_drop....
        
        return True

    return False
    

def run_simulation(algorithm="baseline", num_ms=10, duration=50):
    env = simpy.Environment()
    
    network = Network()
    network.generate_base_stations()
    network.generate_mobile_stations(num_ms)
    network.initial_connections()
    
    network.print_summary()
    
    for ms in network.mobile_stations:
        env.process(ms_process(env, ms, network, algorithm))
    
    env.run(until=duration)
    
    print("\nSimulation complete.")
    print(f"Algorithm : {algorithm}")
    print(f"Duration  : {duration} time steps")
    print(f"MSs ran   : {num_ms}")


def run_visual_simulation(algorithm="baseline", num_ms=10):
    env = simpy.Environment()
    
    network = Network()
    network.generate_base_stations()
    network.generate_mobile_stations(num_ms)
    network.initial_connections()
    
    network.print_summary()
    
    # register all MS processes
    for ms in network.mobile_stations:
        env.process(ms_process(env, ms, network, algorithm))
    
    viz = Visualizer(network, cell_radius=170)
    
    def sim_step():
        env.step()  # advance simpy one event at a time
    
    viz.start(sim_step, interval=100)