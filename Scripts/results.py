class Results:
    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.handoffs   = []    # list of (time, ms_id, old_bs_id, new_bs_id)
        self.call_drops = []    # list of (time, ms_id)
        self.rss_log    = []    # list of (time, ms_id, rss)
        self.ping_pongs = []    # list of (time, ms_id)
    
    def record_handoff(self, time, ms, old_bs, new_bs):
        self.handoffs.append((time, ms.id, old_bs.id, new_bs.id))
    
    def record_call_drop(self, time, ms):
        self.call_drops.append((time, ms.id))
    
    def record_rss(self, time, ms, rss):
        self.rss_log.append((time, ms.id, rss))
    
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
        
        if self.rss_log:
            avg_rss = sum(r[2] for r in self.rss_log) / len(self.rss_log)
            print(f"  Average RSS      : {avg_rss:.2f} dBm")
            
            # call quality based on average RSS
            if avg_rss >= -70:
                quality = "Excellent"
            elif avg_rss >= -80:
                quality = "Good"
            elif avg_rss >= -90:
                quality = "Fair"
            else:
                quality = "Poor"
            print(f"  Call quality     : {quality} ({avg_rss:.2f} dBm)")
        
        # per MS breakdown
        print(f"\n  Per MS Breakdown")
        print(f"  {'-'*50}")
        print(f"  {'MS':<22} {'Handoffs':<12} {'Dropped':<10} {'Avg RSS':<12} {'Quality'}")
        print(f"  {'-'*50}")
        
        for ms in mobile_stations:
            ms_handoffs = [h for h in self.handoffs if h[1] == ms.id]
            ms_drops    = [d for d in self.call_drops if d[1] == ms.id]
            ms_rss      = [r[2] for r in self.rss_log if r[1] == ms.id]
            
            avg = sum(ms_rss) / len(ms_rss) if ms_rss else 0
            
            if avg >= -70:
                q = "Excellent"
            elif avg >= -80:
                q = "Good"
            elif avg >= -90:
                q = "Fair"
            else:
                q = "Poor"
            
            dropped = "Yes" if ms.call_dropped else "No"
            speed = ms.get_speed_category()
            print(f"  MS-{ms.id:<4} ({speed}){'':<{12-len(speed)}} {len(ms_handoffs):<12} {dropped:<10} {avg:<12.2f} {q}")
        
        print(f"\n{'='*55}\n")