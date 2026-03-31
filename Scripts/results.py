#Group 6
#Adam Tremblay - 101264116
#Michael Roy - 101260953

#This is our results object class and will hold all the data we collect from the simulations
class Results:
    def __init__(self, algorithm):
        #It has an algorithm and the key metrics we wanted to track for the simulation
        self.algorithm  = algorithm
        self.handoffs   = []
        self.call_drops = []
        self.rss_log    = []
        self.load_log   = []
        self.snr_log    = []
        self.ping_pongs = []
    
    #Methods that record the data as it comes it adding it to the list for each metric
    def record_handoff(self, time, ms, old_bs, new_bs):
        self.handoffs.append((time, ms.id, old_bs.id, new_bs.id))
    
    def record_call_drop(self, time, ms, reason="unknown"):
        self.call_drops.append((time, ms.id, reason))
    
    def record_rss(self, time, ms, rss):
        self.rss_log.append((time, ms.id, rss))
        
    def record_load(self, time, bs):
        self.load_log.append((time, bs.id, bs.get_load()))

    def record_snr(self, time, ms, snr):
        self.snr_log.append((time, ms.id, snr))
    
    def record_ping_pong(self, time, ms):
        self.ping_pongs.append((time, ms.id))
    
    #We will detect ping pongs by looking for handoffs where the same MS switches back to a recently left BS within a set window
    def detect_ping_pongs(self, window=2):
        self.ping_pongs = []  # reset before detecting so no duplicates on repeated calls
        #Go through handoff history and find rapid switches back to a previous BS
        for i in range(len(self.handoffs)):
            time_i, ms_id, old_bs, new_bs = self.handoffs[i]

            for j in range(i + 1, len(self.handoffs)):
                time_j, ms_id_j, old_bs_j, new_bs_j = self.handoffs[j]

                #check to see if the ms is the same
                if ms_id_j != ms_id:
                    continue
                #Check to see if the handoff timing is within the window
                if time_j - time_i > window:
                    break

                #Switched back to the BS it just left if the BSs are the same
                if new_bs_j == old_bs:
                    self.ping_pongs.append((time_j, ms_id))
                    break
    
    #We will measure the time between handoffs to see which algorithm is slower or faster when triggering handoffs
    def avg_time_between_handoffs(self):
        if len(self.handoffs) < 2:
            return 0
        
        #Group by MS all the handoffs it was involved in
        ms_handoff_times = {}
        for time, ms_id, old_bs, new_bs in self.handoffs:
            ms_handoff_times.setdefault(ms_id, []).append(time)
        
        #Measure the gaps between handoffs for each MS and then take the average
        gaps = []
        for ms_id, times in ms_handoff_times.items():
            sorted_times = sorted(times)
            for i in range(1, len(sorted_times)):
                gaps.append(sorted_times[i] - sorted_times[i-1])
        
        #Calculate the average gap for all MSs
        return sum(gaps) / len(gaps) if gaps else 0
    
    #Print the results formatted to see each of the data points after running an algorithm
    def print_summary(self, mobile_stations):
        self.detect_ping_pongs()
        
        print(f"\n{'='*55}")
        print(f"  Simulation Results — {self.algorithm.upper()} ALGORITHM")
        print(f"{'='*55}")
        
        #Overall stats (General Summary)
        print(f"\n  Overall")
        print(f"  {'-'*40}")
        print(f"  Total handoffs   : {len(self.handoffs)}")
        print(f"  Ping-pong events : {len(self.ping_pongs)}")

        #Specific drops by type
        rss_drops = []
        snr_drops = []

        for d in self.call_drops:
            if d[2] == "rss":
                rss_drops.append(d)
            elif d[2] == "snr":
                snr_drops.append(d)

        print(f"  Total call drops : {len(self.call_drops)}")
        print(f"    - RSS          : {len(rss_drops)}")
        print(f"    - SNR          : {len(snr_drops)}")
        
        #Prints the average rss
        if self.rss_log:
            avg_rss = 0
            for r in self.rss_log:
                avg_rss += r[2]
            avg_rss = avg_rss / len(self.rss_log)
            print(f"  Average RSS      : {avg_rss:.2f} dBm")

        #Prints the average snr
        if self.snr_log:
            avg_snr = 0
            for r in self.snr_log:
                avg_snr += r[2]
            avg_snr = avg_snr / len(self.snr_log)
            
            if avg_snr >= 67:
                quality = "Excellent"
            elif avg_snr >= 65:
                quality = "Good"
            elif avg_snr >= 63:
                quality = "Fair"
            else:
                quality = "Poor"
            print(f"  Average SNR      : {avg_snr:.2f} dB")
            print(f"  Call quality     : {quality} ({avg_snr:.2f} dB)")

        #Per MS breakdown
        print(f"\n  Per MS Breakdown")
        print(f"  {'-'*70}")
        print(f"  {'MS':<22} {'Handoffs':<12} {'Dropped':<10} {'Avg SNR':<12} {'Quality'}")
        print(f"  {'-'*70}")

        #Goes through each of the MSs and shows the specifics for them individually
        for ms in mobile_stations:
            ms_handoffs = []
            for h in self.handoffs:
                if h[1] == ms.id:
                    ms_handoffs.append(h)

            ms_snr = []
            for r in self.snr_log:
                if r[1] == ms.id:
                    ms_snr.append(r[2])
            
            if ms_snr:
                avg_snr = 0
                for s in ms_snr:
                    avg_snr += s
                avg_snr = avg_snr / len(ms_snr)
                avg_str = f"{avg_snr:.2f}"
                if avg_snr >= 67.5:
                    q = "Excellent"
                elif avg_snr >= 65.5:
                    q = "Good"
                elif avg_snr >= 63.75:
                    q = "Fair"
                else:
                    q = "Poor"
            else:
                avg_str = "N/A"
                q       = "No data"
            
            speed = ms.get_speed_category()
            print(f"  MS-{ms.id:<4} ({speed}){'':<{12-len(speed)}} {len(ms_handoffs):<12} {ms.drop_count:<10} {avg_str:<12} {q}")
        
        #Shows the summary of drops by each speed category
        print(f"\n\n  Drops by Speed Category")
        print(f"  {'-'*71}")
        print(f"  {'Speed':<14} {'# of MS':<10} {'Handoffs':<12} {'RSS Drops':<12} {'SNR Drops':<12} {'Total'}")
        print(f"  {'-'*71}")

        speed_categories = ["stationary", "slow", "fast", "very_fast"]
        for category in speed_categories:
            category_ms = []
            for ms in mobile_stations:
                if ms.get_speed_category() == category:
                    category_ms.append(ms)
            if not category_ms:
                continue
            
            ms_ids = []
            for ms in category_ms:
                ms_ids.append(ms.id)

            total_handoffs = 0
            for ms in category_ms:
                total_handoffs += ms.handoff_count

            rss_drops = 0
            for d in self.call_drops:
                if d[1] in ms_ids and d[2] == "rss":
                    rss_drops += 1

            snr_drops = 0
            for d in self.call_drops:
                if d[1] in ms_ids and d[2] == "snr":
                    snr_drops += 1

            total_drops = rss_drops + snr_drops
            print(f"  {category:<14} {len(category_ms):<10} {total_handoffs:<12} {rss_drops:<12} {snr_drops:<12} {total_drops}")

        print(f"\n{'='*71}\n")
        
        #Shows the summary of the overall load the base stations faced during the simulation
        if self.load_log:
            print(f"\n  Cell Load Summary")
            print(f"  {'-'*55}")

            bs_ids = []
            for entry in self.load_log:
                if entry[1] not in bs_ids:
                    bs_ids.append(entry[1])
            bs_ids.sort()

            for bs_id in bs_ids:
                bs_loads = []
                for entry in self.load_log:
                    if entry[1] == bs_id:
                        bs_loads.append(entry[2])

                avg_load = 0
                for load in bs_loads:
                    avg_load += load
                avg_load = avg_load / len(bs_loads)

                max_load = bs_loads[0]
                for load in bs_loads:
                    if load > max_load:
                        max_load = load

                print(f"  BS{bs_id:<4} avg load: {avg_load:>5.1f}%   peak load: {max_load:>5.1f}%")

        print(f"\n{'='*55}\n")