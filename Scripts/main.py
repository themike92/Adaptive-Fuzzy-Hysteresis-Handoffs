#Group 6
#Adam Tremblay - 101264116
#Michael Roy - 101260953

#This will call our simulation with the algorithm we want to test

#Import the simuation files we will need to run and the graph generation
from sim import run_visual_simulation, run_all_simulations, generate_network, reset_network
from graphs import generate_all_graphs

#User menu to select which algorithm they want to use
def display_menu():
    print("\n========== Handoff Algorithm Simulator ==========")
    print("1. Run All Algorithms (with comparison graphs)")
    print("2. Run Baseline RSS Threshold Algorithm")
    print("3. Run Adaptive Hysteresis Algorithm")
    print("4. Run Adaptive-Fuzzy Algorithm")
    print("5. Exit")

#Gets the user input for the menu
def get_user_choice():
    while True:
        try:
            choice = int(input("\nEnter your choice (1-5): "))
            if (choice >= 1 and choice <= 5):
                return choice
            print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Invalid input, please enter a number.")


def main():
    #Sets the number of mobile stations in the network for the simulation
    num_ms  = 150
    network = generate_network(num_ms)

    while True:
        display_menu()
        choice = get_user_choice()

        # Runs all the algorithms one after another but does not show visuals, and generate graph pngs
        if choice == 1:
            print("\nRunning all algorithms ...")
            #Make sure to start with a fresh network
            reset_network(network)
            
            #Runs all the algorithms on the same network and returns results
            all_results = run_all_simulations(network)

            #Generate graphs using results
            generate_all_graphs(all_results, network.mobile_stations)
            
            #Print summary for each algorithm
            for algorithm, results in all_results.items():
                results.print_summary(network.mobile_stations)

        #Will run the selected alg and will show visuals, will not generate graphs
        elif choice == 2:
            reset_network(network)
            run_visual_simulation("baseline", network)
        elif choice == 3:
            reset_network(network)
            run_visual_simulation("adaptive", network)
        elif choice == 4:
            reset_network(network)
            run_visual_simulation("fuzzy", network)
        elif choice == 5:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()