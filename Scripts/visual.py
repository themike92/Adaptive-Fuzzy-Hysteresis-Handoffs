import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import math

class Visualizer:
    def __init__(self, network, cell_radius, signal_radius):
        self.network = network
        self.cell_radius = cell_radius
        self.signal_radius = signal_radius
        
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.ax.set_xlim(network.bounds[0], network.bounds[1])
        self.ax.set_ylim(network.bounds[2], network.bounds[3])
        self.ax.set_aspect('equal')
        self.ax.set_title("Handoff Simulation", color='white', fontsize=14)
        self.ax.set_facecolor('#1a1a2e')
        self.fig.patch.set_facecolor('#1a1a2e')
        
        # fix axis tick and label colors
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#4a9eff')
        
        self.bs_scatter  = None
        self.ms_scatter  = None
        self.connections = []
        self.hex_patches = []
        
        self._draw_hex_grid()
        self._init_stations()
    
    def _hex_corners(self, cx, cy):
        corners = []
        for i in range(6):
            angle = math.radians(60 * i)  # flat-top orientation
            x = cx + self.cell_radius * math.cos(angle)
            y = cy + self.cell_radius * math.sin(angle)
            corners.append((x, y))
        return corners
    
    def _draw_hex_grid(self):
        for bs in self.network.base_stations:
            corners = self._hex_corners(bs.x, bs.y)
            hex_patch = patches.Polygon(
                corners,
                closed=True,
                fill=False,
                edgecolor='#4a9eff',
                linewidth=1.5,
                linestyle='--',
                alpha=0.5
            )
            self.ax.add_patch(hex_patch)

            # signal range circle
            range_circle = patches.Circle(
                (bs.x, bs.y),
                radius=self.signal_radius,
                fill=True,
                facecolor="#20456e",
                edgecolor='none',
                alpha=0.05  # very faint
            )
            self.ax.add_patch(range_circle)
    
    def _init_stations(self):
        # draw BS markers
        bs_x = [bs.x for bs in self.network.base_stations]
        bs_y = [bs.y for bs in self.network.base_stations]
        self.bs_scatter = self.ax.scatter(
            bs_x, bs_y,
            c='#4a9eff', s=150, zorder=5,
            marker='^', label='Base Station'
        )
        
        # label each BS
        for bs in self.network.base_stations:
            self.ax.text(
                bs.x, bs.y + 20, f'BS{bs.id}',
                color='#4a9eff', fontsize=8,
                ha='center', zorder=6
            )
        
        # draw MS markers
        ms_x = [ms.x for ms in self.network.mobile_stations]
        ms_y = [ms.y for ms in self.network.mobile_stations]
        self.ms_scatter = self.ax.scatter(
            ms_x, ms_y,
            c='#ff6b6b', s=60, zorder=5,
            marker='o', label='Mobile Station'
        )
        
        self.ax.legend(
            loc='upper right',
            facecolor='#16213e',
            edgecolor='#4a9eff',
            labelcolor='white'
        )
    
    def update(self, frame):
        # update MS positions
        ms_x = [ms.x for ms in self.network.mobile_stations]
        ms_y = [ms.y for ms in self.network.mobile_stations]
        self.ms_scatter.set_offsets(list(zip(ms_x, ms_y)))
        

         # update MS colors based on state
        colors = []
        for ms in self.network.mobile_stations:
            if ms.call_dropped or ms.connected_bs is None:
                colors.append('#888888')   # grey - dropped
            elif ms.handoff_flash > 0:
                colors.append('#bf5fff')   # purple - just handed off
                ms.handoff_flash -= 1
            else:
                colors.append('#ff6b6b')   # red - connected
        self.ms_scatter.set_color(colors)

        # clear old connection lines
        for line in self.connections:
            line.remove()
        self.connections = []
        
        # draw connection lines from each MS to its BS
        for ms in self.network.mobile_stations:
            if ms.connected_bs:
                line, = self.ax.plot(
                    [ms.x, ms.connected_bs.x],
                    [ms.y, ms.connected_bs.y],
                    color='#ffd700', linewidth=0.8,
                    alpha=0.4, zorder=3
                )
                self.connections.append(line)
        
        return [self.ms_scatter] + self.connections
    
    def start(self, sim_step_fn, interval=100):
        def animate(frame):
            sim_step_fn()         # advance simulation one step
            return self.update(frame)  # redraw
        
        self.ani = animation.FuncAnimation(
            self.fig, animate,
            interval=interval,
            blit=False
        )
        plt.tight_layout()
        plt.show()