#This will call our simulation with the algorithm we want to test

from sim import run_visual_simulation, run_all_simulations, generate_network, reset_network

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
    return 70

def main():
    print("\n=== Handoff Algorithm Simulator ===")
    num_ms  = get_num_ms()
    network = generate_network(num_ms)

    while True:
        display_menu()
        choice = get_user_choice()

        if choice == 1:
            print("\nRunning all algorithms...")
            run_all_simulations(network=network)
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