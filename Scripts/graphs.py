# graphs.py
# Generates comparison graphs for all three algorithms after run_all_simulations
from base_station import RSS_THRESHOLDS, SNR_THRESHOLDS
import os
import matplotlib.pyplot as plt
import matplotlib
#matplotlib.use('Agg')  # non-interactive backend so graphs save without opening windows

GRAPHS_DIR = os.path.join(os.path.dirname(__file__), "graphs")
COLORS     = {
    "baseline": "#4a9eff",
    "adaptive": "#bf5fff",
    "fuzzy":    "#44ff88"
}
ALGORITHMS = ["baseline", "adaptive", "fuzzy"]


def ensure_graphs_dir():
    os.makedirs(GRAPHS_DIR, exist_ok=True)


def save_fig(filename):
    path = os.path.join(GRAPHS_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    print(f"  Saved: {filename}")


def apply_dark_style(ax, title, xlabel, ylabel):
    ax.set_facecolor('#16213e')
    ax.set_title(title,  color='white', fontsize=13, pad=12)
    ax.set_xlabel(xlabel, color='white', fontsize=10)
    ax.set_ylabel(ylabel, color='white', fontsize=10)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#4a9eff')
    ax.yaxis.grid(True, color='#2a3a5e', linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)


# 1. Total handoffs per algorithm
def plot_total_handoffs(all_results):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('#1a1a2e')

    values = [len(all_results[alg].handoffs) for alg in ALGORITHMS]
    bars   = ax.bar(ALGORITHMS, values, color=[COLORS[a] for a in ALGORITHMS], width=0.5)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                str(val), ha='center', va='bottom', color='white', fontsize=10)

    apply_dark_style(ax, "Total Handoffs per Algorithm", "Algorithm", "Handoff Count")
    save_fig("1_total_handoffs.png")


# 2. Ping-pong rate per algorithm
def plot_ping_pong(all_results):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('#1a1a2e')

    for alg in ALGORITHMS:
        all_results[alg].detect_ping_pongs()

    values = [len(all_results[alg].ping_pongs) for alg in ALGORITHMS]
    bars   = ax.bar(ALGORITHMS, values, color=[COLORS[a] for a in ALGORITHMS], width=0.5)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                str(val), ha='center', va='bottom', color='white', fontsize=10)

    apply_dark_style(ax, "Ping-Pong Events per Algorithm", "Algorithm", "Ping-Pong Count")
    save_fig("2_ping_pong_rate.png")


# 3. Call drops per algorithm
def plot_call_drops(all_results):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('#1a1a2e')

    rss_drops = [len([d for d in all_results[alg].call_drops if d[2] == "rss"]) for alg in ALGORITHMS]
    snr_drops = [len([d for d in all_results[alg].call_drops if d[2] == "snr"]) for alg in ALGORITHMS]

    x     = range(len(ALGORITHMS))
    width = 0.35
    bars1 = ax.bar([i - width/2 for i in x], rss_drops, width, label='RSS Drops', color='#ff4444')
    bars2 = ax.bar([i + width/2 for i in x], snr_drops, width, label='SNR Drops', color='#ffaa00')

    for bar, val in zip(bars1, rss_drops):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                str(val), ha='center', va='bottom', color='white', fontsize=9)
    for bar, val in zip(bars2, snr_drops):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                str(val), ha='center', va='bottom', color='white', fontsize=9)

    ax.set_xticks(list(x))
    ax.set_xticklabels(ALGORITHMS)
    ax.legend(facecolor='#16213e', edgecolor='#4a9eff', labelcolor='white')
    apply_dark_style(ax, "Call Drops per Algorithm", "Algorithm", "Drop Count")
    save_fig("3_call_drops.png")


# 4. Average RSS over time per algorithm
def plot_rss_over_time(all_results):
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#1a1a2e')

    for alg in ALGORITHMS:
        rss_log = all_results[alg].rss_log
        if not rss_log:
            continue

        # group by time step and average
        time_rss = {}
        for time, ms_id, rss in rss_log:
            time_rss.setdefault(time, []).append(rss)

        times   = sorted(time_rss.keys())
        avg_rss   = [sum(time_rss[t]) / len(time_rss[t]) for t in times]
        smoothed  = smooth(avg_rss, window=8)
        ax.plot(times, smoothed, label=alg, color=COLORS[alg], linewidth=2)

    ax.legend(facecolor='#16213e', edgecolor='#4a9eff', labelcolor='white')
    apply_dark_style(ax, "Average RSS Over Time", "Time Step", "Average RSS (dBm)")
    save_fig("4_rss_over_time.png")


# 5. Average SNR over time per algorithm
def plot_snr_over_time(all_results):
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#1a1a2e')

    for alg in ALGORITHMS:
        snr_log = all_results[alg].snr_log
        if not snr_log:
            continue

        time_snr = {}
        for time, ms_id, snr in snr_log:
            time_snr.setdefault(time, []).append(snr)

        times   = sorted(time_snr.keys())
        avg_snr = [sum(time_snr[t]) / len(time_snr[t]) for t in times]

        smoothed  = smooth(avg_snr, window=8)
        ax.plot(times, smoothed, label=alg, color=COLORS[alg], linewidth=2)

    ax.legend(facecolor='#16213e', edgecolor='#4a9eff', labelcolor='white')
    apply_dark_style(ax, "Average SNR Over Time", "Time Step", "Average SNR (dB)")
    save_fig("5_snr_over_time.png")


# 6. Drops by speed category per algorithm
def plot_drops_by_speed(all_results, mobile_stations):
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#1a1a2e')

    speed_categories = ["stationary", "slow", "fast", "very_fast"]
    x     = range(len(speed_categories))
    width = 0.25

    for idx, alg in enumerate(ALGORITHMS):
        drops = []
        for category in speed_categories:
            ms_ids       = [ms.id for ms in mobile_stations if ms.get_speed_category() == category]
            total_drops  = len([d for d in all_results[alg].call_drops if d[1] in ms_ids])
            drops.append(total_drops)

        offset = (idx - 1) * width
        bars   = ax.bar([i + offset for i in x], drops, width, label=alg, color=COLORS[alg])

        for bar, val in zip(bars, drops):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                    str(val), ha='center', va='bottom', color='white', fontsize=8)

    ax.set_xticks(list(x))
    ax.set_xticklabels(speed_categories)
    ax.legend(facecolor='#16213e', edgecolor='#4a9eff', labelcolor='white')
    apply_dark_style(ax, "Call Drops by Speed Category", "Speed Category", "Drop Count")
    save_fig("6_drops_by_speed.png")

def plot_handoff_delay(all_results):
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#1a1a2e')

    for alg in ALGORITHMS:
        handoffs = all_results[alg].handoffs
        if not handoffs:
            continue

        # group handoffs by time step
        time_counts = {}
        for time, ms_id, old_bs, new_bs in handoffs:
            time_counts[time] = time_counts.get(time, 0) + 1

        times  = sorted(time_counts.keys())
        counts = [time_counts[t] for t in times]

        # cumulative handoffs over time
        cumulative = []
        total = 0
        for c in counts:
            total += c
            cumulative.append(total)

        ax.plot(times, cumulative, label=alg, color=COLORS[alg], linewidth=1.5)

    ax.legend(facecolor='#16213e', edgecolor='#4a9eff', labelcolor='white')
    apply_dark_style(ax, "Cumulative Handoffs Over Time", "Time Step", "Total Handoffs")
    save_fig("7_handoff_timing.png")


def plot_avg_rss_comparison(all_results):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('#1a1a2e')

    values = []
    for alg in ALGORITHMS:
        rss_log = all_results[alg].rss_log
        if rss_log:
            avg = sum(r[2] for r in rss_log) / len(rss_log)
        else:
            avg = 0
        values.append(avg)

    bars = ax.bar(ALGORITHMS, values, color=[COLORS[a] for a in ALGORITHMS], width=0.5)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 1,
                f'{val:.2f}', ha='center', va='top', color='white', fontsize=10)

    apply_dark_style(ax, "Average RSS per Algorithm (Higher is Better)", 
                    "Algorithm", "Average RSS (dBm)")
    save_fig("8_avg_rss_comparison.png")
    








def plot_rss_distribution(all_results):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('#1a1a2e')

    means, mins, maxs = [], [], []
    for alg in ALGORITHMS:
        rss_vals = [r[2] for r in all_results[alg].rss_log]
        means.append(sum(rss_vals) / len(rss_vals))
        mins.append(min(rss_vals))
        maxs.append(max(rss_vals))

    x = range(len(ALGORITHMS))
    bars = ax.bar(ALGORITHMS, means, color=[COLORS[a] for a in ALGORITHMS], width=0.5)

    # whiskers
    for i, (mn, mx) in enumerate(zip(mins, maxs)):
        ax.vlines(i, mn, mx, color='white', linewidth=1.5, alpha=0.4)
        ax.hlines([mn, mx], i - 0.06, i + 0.06, color='white', linewidth=1.5, alpha=0.4)

    # threshold lines from your constants
    ax.axhline(RSS_THRESHOLDS["low"],  color='#ff4444', linestyle='--', linewidth=1, alpha=0.6, label='Low threshold')
    ax.axhline(RSS_THRESHOLDS["high"], color='#44ff88', linestyle='--', linewidth=1, alpha=0.6, label='High threshold')

    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 1,
                f'{val:.1f}', ha='center', va='top', color='white', fontsize=9)

    ax.legend(facecolor='#16213e', edgecolor='#4a9eff', labelcolor='white')
    apply_dark_style(ax, "RSS Distribution per Algorithm (Mean ± Range)", "Algorithm", "RSS (dBm)")
    save_fig("4_rss_distribution.png")




def plot_snr_distribution(all_results):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('#1a1a2e')

    means, mins, maxs = [], [], []
    for alg in ALGORITHMS:
        snr_vals = [r[2] for r in all_results[alg].snr_log]
        means.append(sum(snr_vals) / len(snr_vals))
        mins.append(min(snr_vals))
        maxs.append(max(snr_vals))

    x = range(len(ALGORITHMS))
    bars = ax.bar(ALGORITHMS, means, color=[COLORS[a] for a in ALGORITHMS], width=0.5)

    # whiskers
    for i, (mn, mx) in enumerate(zip(mins, maxs)):
        ax.vlines(i, mn, mx, color='white', linewidth=1.5, alpha=0.4)
        ax.hlines([mn, mx], i - 0.06, i + 0.06, color='white', linewidth=1.5, alpha=0.4)

    # threshold lines from your constants
    ax.axhline(SNR_THRESHOLDS["low"],  color='#ff4444', linestyle='--', linewidth=1, alpha=0.6, label='Low threshold')
    ax.axhline(SNR_THRESHOLDS["high"], color='#44ff88', linestyle='--', linewidth=1, alpha=0.6, label='High threshold')

    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 1,
                f'{val:.1f}', ha='center', va='top', color='white', fontsize=9)

    ax.legend(facecolor='#16213e', edgecolor='#4a9eff', labelcolor='white')
    apply_dark_style(ax, "SNR Distribution per Algorithm (Mean ± Range)", "Algorithm", "SNR (dB)")
    save_fig("5_snr_distribution.png")




# Main entry point — call this from sim.py after run_all_simulations
def generate_all_graphs(all_results, mobile_stations):
    ensure_graphs_dir()
    print("\nGenerating graphs...")
    
    # switch to non-interactive backend just for saving
    original_backend = matplotlib.get_backend()
    matplotlib.use('Agg')
    
    plot_total_handoffs(all_results)
    plot_ping_pong(all_results)
    plot_call_drops(all_results)
    plot_rss_over_time(all_results)
    plot_snr_over_time(all_results)
    plot_drops_by_speed(all_results, mobile_stations)
    plot_handoff_delay(all_results)
    plot_avg_rss_comparison(all_results)
    plot_rss_distribution(all_results)
    plot_snr_distribution(all_results)
    
    # restore original backend so visual.py still works
    matplotlib.use(original_backend)
    
    print(f"\nAll graphs saved to /graphs folder.")


#HELPER
def smooth(values, window=5):
    smoothed = []
    for i in range(len(values)):
        start = max(0, i - window)
        smoothed.append(sum(values[start:i+1]) / (i - start + 1))
    return smoothed