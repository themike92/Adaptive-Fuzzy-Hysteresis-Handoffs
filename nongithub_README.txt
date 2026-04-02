
COMP 4203 Final Project. Adam Tremblay - 101264116, Michael Roy - 101260953


Relevant files:


In the Script folder:

mobile_station.py:
	- Represents a mobile station object in the network. Includes speed and connection attributes, as well as movement logic.

base_station.py:
	- Represents a base station object in the network. Includes power, congestion, and noise attributes, as well as functions to manage the number of calls 
	and to calculate the relevant metrics (RSS, SNR, load).

network.py:
	- What generates and manages the network. Sets the initial parameters for MSs, BSs, and holds BS comparison logic.

sim.py:
	- What sets up and manages the simulation and visual environment, and where the logic for our 3 main algorithms lie. Uses the Simpy library.

visual.py:
	- What displays the visual simulation window to the user. Uses the Matplotlib library.

results.py:
	- Records and displays all relevat metrics. 

main.py:
	- Displays the menu for the user, and runs the correct algorithm based on user input.

graphs.py:
	- Generates the graphs folder, as well as the comparison graphs themselves. Matplotlib was also used here. 

graphs folder:
	- Folder containing all the generated comparison graphs.


Others:

Requirements.txt:
	- contains all the necessary libraries needed to successfully run this program. Instructions on how to run it below.


Instructions to run the program:

1. Ensure that all proper libraries are downloaded on your machine. To download them, run "pip install requirements.txt". 

2. In your terminal, move into the Scripts folder containing all the code files (.py)

3. to run the program, run "python main.py" in the terminal 

4. Follow the user prompt to either view all the algorithms individually (options 2 - 4), or to run them all at once (option 1)

5. Running each algorithm individually will have a visual display window pop up, and results will be printed in the terminal upon completion

6. When running option 1, all 3 simulations will run sequentially without a visual sim window. When the sim is done, there will be a graphs folder that appears 
in the Scripts folder. In this folder, there are many PNGs showing all the relevant comparisons between each algorithm. The results for each individual algorithm will 
appear in the terminal too.