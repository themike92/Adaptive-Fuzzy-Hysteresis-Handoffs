class Results:
    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.handoffs   = []    # list of (time, ms_id, old_bs_id, new_bs_id)
        self.call_drops = []    # list of (time, ms_id)
        self.rss_log    = []    # list of (time, ms_id, rss)
        self.load_log   = []    # list of (time, bs_id, load_percent)
        self.snr_log    = []
        self.ping_pongs = []    # list of (time, ms_id)
    
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
    
    def detect_ping_pongs(self, window=5):
        # go through handoff history and find rapid switches back to a previous BS
        for i in range(len(self.handoffs)):
            time_i, ms_id, old_bs, new_bs = self.handoffs[i]
            for j in range(i + 1, len(self.handoffs)):
                time_j, ms_id_j, old_bs_j, new_bs_j = self.handoffs[j]
                if ms_id_j != ms_id:
                    continue
                if time_j - time_i > window:
                    break
                # switched back to the BS it just left
                if new_bs_j == old_bs:
                    self.ping_pongs.append((time_j, ms_id))
                    break
    
    def print_summary(self, mobile_stations):
        self.detect_ping_pongs()
        
        print(f"\n{'='*55}")
        print(f"  Simulation Results — {self.algorithm.upper()} ALGORITHM")
        print(f"{'='*55}")
        
        # overall stats
        print(f"\n  Overall")
        print(f"  {'-'*40}")
        print(f"  Total handoffs   : {len(self.handoffs)}")
        print(f"  Total call drops : {len(self.call_drops)}")
        print(f"  Ping-pong events : {len(self.ping_pongs)}")

        rss_drops        = [d for d in self.call_drops if d[2] == "rss"]
        snr_drops        = [d for d in self.call_drops if d[2] == "snr"]

        print(f"  Total call drops : {len(self.call_drops)}")
        print(f"    - RSS          : {len(rss_drops)}")
        print(f"    - SNR          : {len(snr_drops)}")
        
        if self.rss_log:
            avg_rss = sum(r[2] for r in self.rss_log) / len(self.rss_log)
            print(f"  Average RSS      : {avg_rss:.2f} dBm")
            
            # call quality based on average RSS
            if avg_rss >= -55:
                quality = "Excellent"
            elif avg_rss >= -62:
                quality = "Good"
            elif avg_rss >= -68:
                quality = "Fair"
            else:
                quality = "Poor"
            print(f"  Call quality     : {quality} ({avg_rss:.2f} dBm)")
        
        # per MS breakdown
        print(f"\n  Per MS Breakdown")
        print(f"  {'-'*70}")
        print(f"  {'MS':<22} {'Handoffs':<12} {'Dropped':<10} {'Avg RSS':<12} {'Quality'}")
        print(f"  {'-'*70}")
        
        for ms in mobile_stations:
            ms_handoffs = [h for h in self.handoffs if h[1] == ms.id]
            ms_rss      = [r[2] for r in self.rss_log if r[1] == ms.id]
            
            if ms_rss:
                avg     = sum(ms_rss) / len(ms_rss)
                avg_str = f"{avg:.2f}"
                if avg >= -55:
                    q = "Excellent"
                elif avg >= -62:
                    q = "Good"
                elif avg >= -68:
                    q = "Fair"
                else:
                    q = "Poor"
            else:
                avg_str = "N/A"
                q       = "No data"
            
            speed = ms.get_speed_category()
            print(f"  MS-{ms.id:<4} ({speed}){'':<{12-len(speed)}} {len(ms_handoffs):<12} {ms.drop_count:<10} {avg_str:<12} {q}")
        
        print(f"\n  Drops by Speed Category")
        print(f"  {'-'*65}")
        print(f"  {'Speed':<14} {'# of MS':<10} {'Handoffs':<12} {'RSS Drops':<12} {'SNR Drops':<12} {'Total'}")
        print(f"  {'-'*65}")

        speed_categories = ["stationary", "slow", "fast", "very_fast"]
        for category in speed_categories:
            category_ms = [ms for ms in mobile_stations if ms.get_speed_category() == category]
            if not category_ms:
                continue
            
            ms_ids         = [ms.id for ms in category_ms]
            total_handoffs = sum(ms.handoff_count for ms in category_ms)
            rss_drops      = len([d for d in self.call_drops if d[1] in ms_ids and d[2] == "rss"])
            snr_drops      = len([d for d in self.call_drops if d[1] in ms_ids and d[2] == "snr"])
            total_drops    = rss_drops + snr_drops
            
            print(f"  {category:<14} {len(category_ms):<10} {total_handoffs:<12} {rss_drops:<12} {snr_drops:<12} {total_drops}")

        print(f"\n{'='*65}\n")

        if self.load_log:
            print(f"\n  Cell Load Summary")
            print(f"  {'-'*70}")
            
            for bs_id in sorted(set(entry[1] for entry in self.load_log)):
                bs_loads = [entry[2] for entry in self.load_log if entry[1] == bs_id]
                avg_load = sum(bs_loads) / len(bs_loads)
                max_load = max(bs_loads)
                print(f"  BS{bs_id:<4} avg load: {avg_load:>5.1f}%   peak load: {max_load:>5.1f}%")
        
        print(f"\n{'='*75}\n")