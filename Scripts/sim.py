#Simulation file, uses simpy to run our simulation


#This is where all handoff logic (baseline, adaptive, and fuzzy) will be determined and applies


import simpy

env = simpy.Environment()  # the simulation clock/world

def ms_process(env):
    while True:
        # move MS, check signal, trigger handoff if needed
        yield env.timeout(1)  # wait 1 time unit then repeat

env.process(ms_process(env))
env.run(until=100)  # run for 100 time units