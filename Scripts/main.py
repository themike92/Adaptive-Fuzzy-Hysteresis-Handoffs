#This will call our simulation with the algorithm we want to test

from sim import run_simulation, run_visual_simulation

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

def main():
    while True:
        display_menu()
        choice = get_user_choice()

        if choice == 1:
            print("\nRunning all algorithms...")
            # run_simulation("all")  # returns comparison graph data
        elif choice == 2:
            run_visual_simulation(algorithm="baseline", num_ms=10)
        elif choice == 3:
            run_visual_simulation(algorithm="adaptive", num_ms=10)
        elif choice == 4:
            print("\nRunning Adaptive Fuzzy...")
            # run_simulation("fuzzy")  # visual only
        elif choice == 5:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()