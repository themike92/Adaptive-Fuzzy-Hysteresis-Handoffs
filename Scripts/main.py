#main.py
#Adam Tremblay - 101264116
#Michael Roy - 

from sim import run_visual_simulation, run_all_simulations, generate_network, reset_network
from graphs import generate_all_graphs

def display_menu():
    print("\n=== Handoff Algorithm Simulator ===")
    print("1. Run All Algorithms (with comparison graphs)")
    print("2. Run Baseline RSS Threshold Algorithm")
    print("3. Run Adaptive Hysteresis Algorithm")
    print("4. Run Adaptive-Fuzzy Algorithm")
    print("5. Exit")

def get_user_choice():
    while True:
        try:
            choice = int(input("\nEnter your choice (1-5): "))
            if 1 <= choice <= 5:
                return choice
            print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Invalid input, please enter a number.")

def get_num_ms():
    return 140

def main():
    num_ms  = get_num_ms()
    network = generate_network(num_ms)

    while True:
        display_menu()
        choice = get_user_choice()

        if choice == 1:
            print("\nRunning all algorithms (headless)...")
            reset_network(network)
            all_results = run_all_simulations(network)
            generate_all_graphs(all_results, network.mobile_stations)
            
            # print summary for each algorithm
            for alg, results in all_results.items():
                results.print_summary(network.mobile_stations)
                
        elif choice == 2:
            reset_network(network)
            run_visual_simulation(algorithm="baseline", network=network)
        elif choice == 3:
            reset_network(network)
            run_visual_simulation(algorithm="adaptive", network=network)
        elif choice == 4:
            reset_network(network)
            run_visual_simulation(algorithm="fuzzy", network=network)
        elif choice == 5:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()