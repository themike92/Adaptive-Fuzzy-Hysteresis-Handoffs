# Adaptive Fuzzy Hysteresis Handoff Simulation
**COMP4203 — Group 6**
Adam Tremblay · Michael Roy

---

## Overview

This project simulates and compares three cellular network handoff algorithms across a hexagonal base station grid with mobile stations moving throughout the network. The simulation is built using SimPy for discrete-event simulation and Matplotlib for live visualization and graph generation.

The three algorithms implemented are:
- **Baseline RSS Threshold** — fixed hysteresis margin, handoff triggered purely by RSS
- **Adaptive Hysteresis** — hysteresis margin adjusts dynamically based on mobile station speed
- **Fuzzy QoS (FFDS)** — uses a weighted fuzzy scoring system combining RSS, SNR, and load to select the best target base station

---

## Requirements

- Python 3.10 or higher
- Install dependencies using:

```bash
pip install -r requirements.txt
```

---

## Project Structure

```
project/
│
├── main.py              # Entry point — run this to start the simulation
├── sim.py               # Simulation logic, all three handoff algorithms
├── network.py           # Network generation, hex grid, BS/MS placement
├── base_station.py      # BaseStation class, RSS/SNR/FFDS calculations
├── mobile_station.py    # MobileStation class, movement logic
├── visual.py            # Live Matplotlib animation visualizer
├── results.py           # Results tracking, summary printing
├── graphs.py            # Graph generation for all comparison metrics
│
├── requirements.txt     # Python dependencies
├── README.md            # This file
│
└── graphs/              # Auto-generated when running all algorithms (option 1)
    ├── 1_total_handoffs.png
    ├── 2_ping_pong_rate.png
    ├── 3_call_drops.png
    ├── 4_rss_over_time.png
    ├── 5_snr_over_time.png
    ├── 6_drops_by_speed.png
    ├── 7_handoff_delay.png
    ├── 8_avg_rss_comparison.png
    ├── 9_avg_time_between_handoffs.png
    └── 10_quality_distribution.png
```

---

## How to Run

1. Clone or download the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the simulation:
```bash
python main.py
```
4. You will be prompted to enter the number of mobile stations
5. Select an option from the menu

---

## Menu Options

```
=== Handoff Algorithm Simulator ===
1. Run All Algorithms (with comparison graphs)
2. Run Baseline RSS Threshold Algorithm
3. Run Adaptive Hysteresis Algorithm
4. Run Adaptive-Fuzzy Algorithm
5. Exit
```

**Option 1 — Run All Algorithms**
Runs all three algorithms headlessly (no live visualization) using the same network and mobile station configuration. After all three complete, a full set of comparison graphs is automatically generated and saved to a `/graphs` folder in the same directory as `main.py`. A detailed summary for each algorithm is also printed to the console.

**Options 2, 3, 4 — Individual Algorithm**
Runs the selected algorithm with a live Matplotlib visualization showing:
- The hexagonal cell grid and base station coverage areas
- Mobile stations moving in real time, colour coded by status:
  - 🟢 **Green** — connected, active call
  - 🟣 **Purple** — handoff just occurred
  - 🔴 **Red flash** — call just dropped
  - ⚫ **Grey** — out of range, no connection
- Connection lines from each mobile station to its serving base station

After the simulation window closes, a detailed results summary is printed to the console including handoffs, call drops, ping-pong events, average RSS, average SNR, call quality, and a breakdown by speed category.

---

## Graphs Folder

When running **Option 1**, a `/graphs` folder is automatically created in the same directory as `main.py`. If the folder already exists, graphs are overwritten. The folder contains 10 PNG files comparing all three algorithms across the key evaluation metrics defined in the project proposal.

---

## Simulation Parameters

Key parameters can be adjusted in `sim.py`:

| Parameter | Default | Description |
|---|---|---|
| `SIM_DURATION` | 200 | Number of simulation time steps |
| `H_FIXED` | 9 | Baseline fixed hysteresis margin (dBm) |
| `H_DEF` | 8 | Adaptive/fuzzy default margin (dBm) |
| `K` | 0.1 | Speed sensitivity for adaptive margin |
| `RSS_DROP_THRESHOLD` | -32 | Minimum RSS before call drops (dBm) |
| `SNR_DROP_THRESHOLD` | 44 | Minimum SNR before call drops (dB) |
| `RANDOM_SEED` | 42 | Seed for reproducible results |

Network parameters can be adjusted in `network.py` and `base_station.py`.

---

## Notes

- The simulation uses a fixed random seed (`RANDOM_SEED = 12345` in `sim.py`) to ensure reproducible results across all algorithm runs. Change this value to run with a different network configuration.
- The number of mobile stations is entered once at startup and shared across all algorithm runs to ensure fair comparison.
- All three algorithms run on identical network topology and mobile station configurations — only the handoff decision logic differs.
