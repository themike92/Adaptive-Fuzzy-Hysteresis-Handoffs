#Group 6
#Adam Tremblay - 101264116
#Michael Roy - 101260953
#Controls the visual animation of the simulation, using matplotlib


import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from matplotlib.lines import Line2D
import math

class Visualizer:
    # Initialize the visualizer with the network, cell radius, and signal radius. 
    # Set up the Matplotlib figure and axes, and draw the initial state of the network
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
        
        #axis tick and label colors
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#4a9eff')
        
        self.bs_scatter  = None
        self.ms_scatter  = None
        self.connections = []
        self.hex_patches = []
        
        #draw all the hexagonal cells and the signal range circles for each BS
        self._draw_hex_grid()
        #Set the circle representing the MS movement boundary
        self._draw_boundary(cx=500, cy=500, boundary_radius=450)
        # draw the initial positions of the BSs and MSs, and set up the legend in the top right
        self._init_stations()

        self.sub_frames    = 4   # animation frames between each sim step
        self.current_sub   = 0
    
    
    # calculate the corners of a hexagon for a given center point
    # Draw the hexagonal grid representing the BS coverage areas
    def _hex_corners(self, cx, cy):
        corners = []
        for i in range(6):
            angle = math.radians(60 * i)  # flat-top orientation
            x = cx + self.cell_radius * math.cos(angle)
            y = cy + self.cell_radius * math.sin(angle)
            corners.append((x, y))
        return corners
    
    
    # Draw the hexagonal grid representing the BS coverage areas, and the faint circles representing signal range
    def _draw_hex_grid(self):
        
        # hex grid
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
                alpha=0.1  # very faint
            )
            self.ax.add_patch(range_circle)
    
    
    # initialize the station markers and labels, and set up the legend
    def _init_stations(self):
        # draw BS markers
        bs_x = [bs.x for bs in self.network.base_stations]
        bs_y = [bs.y for bs in self.network.base_stations]
        self.bs_scatter = self.ax.scatter(
            bs_x, bs_y,
            c='#4a9eff', s=150, zorder=5,
            marker='^'
        )
        
        # label each BS
        for bs in self.network.base_stations:
            self.ax.text(
                bs.x, bs.y + 20, f'BS-{bs.id}',
                color='#4a9eff', fontsize=8,
                ha='center', zorder=6
            )
        
        # draw MS markers
        ms_x = [ms.x for ms in self.network.mobile_stations]
        ms_y = [ms.y for ms in self.network.mobile_stations]
        self.ms_scatter = self.ax.scatter(
            ms_x, ms_y,
            c='#ff6b6b', s=60, zorder=5,
            marker='o'
        )

        # MS labels
        self.ms_labels = []
        for ms in self.network.mobile_stations:
            label = self.ax.text(
                ms.x, ms.y + 15, f'MS-{ms.id}',
                color='white', fontsize=6,
                ha='center', zorder=7
            )
            self.ms_labels.append(label)
        
        # legend
        legend_elements = [
            Line2D([0], [0], marker='^', color='w', markerfacecolor='#4a9eff', markersize=10, label='Base Station', linestyle='None'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#44ff88', markersize=8, label='MS - Connected', linestyle='None'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#bf5fff', markersize=8, label='MS - Handoff', linestyle='None'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff4444', markersize=8, label='MS - Call Dropped', linestyle='None'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#888888', markersize=8, label='MS - Out of Range', linestyle='None'),
        ]

        self.ax.legend(
            handles=legend_elements,
            loc='upper right',
            facecolor='#16213e',
            edgecolor='#4a9eff',
            labelcolor='white'
        )
    
    
    # Update the positions and colors of the MSs, and redraw the connection lines to the BSs if needed
    def update(self, frame, t):
        ms_x = [ms.prev_x + (ms.x - ms.prev_x) * t for ms in self.network.mobile_stations]
        ms_y = [ms.prev_y + (ms.y - ms.prev_y) * t for ms in self.network.mobile_stations]
        self.ms_scatter.set_offsets(list(zip(ms_x, ms_y)))
        
        # update MS labels
        for i, ms in enumerate(self.network.mobile_stations):
            self.ms_labels[i].set_position((ms_x[i], ms_y[i] + 15))

        # update MS colors based on state
        colors = []
        for ms in self.network.mobile_stations:
            if ms.handoff_flash > 0:
                colors.append('#bf5fff')   # purple - handoff
                ms.handoff_flash -= 1
            elif ms.drop_flash > 0:
                colors.append('#ff4444')   # red - call dropped
                ms.drop_flash -= 1
            elif ms.connected_bs is None:
                colors.append('#888888')   # grey - out of range
            else:
                colors.append('#44ff88')   # green - connected
        self.ms_scatter.set_color(colors)

        # clear old connection lines
        for line in self.connections:
            line.remove()
        self.connections = []
        
        for i, ms in enumerate(self.network.mobile_stations):
            if ms.connected_bs:
                line, = self.ax.plot(
                    [ms_x[i], ms.connected_bs.x],
                    [ms_y[i], ms.connected_bs.y],
                    color='#ffd700', linewidth=0.8,
                    alpha=0.4, zorder=3
                )
                self.connections.append(line)
        
        return [self.ms_scatter] + self.connections
    
    
    # Start the animation
    # use sim_step_fn to advance the simulation state every few frames
    # use the update fucntion to redraw the positions and connections every frame
    def start(self, sim_step_fn, interval, duration):
        self.frame_count = 0
        self.duration = duration
        
        def animate(frame):
            # only advance simulation every sub_frames animation frames
            if self.current_sub == 0:
                if self.frame_count >= self.duration:
                    self.ani.event_source.stop()
                    plt.close()
                    return [self.ms_scatter]
                sim_step_fn()
                self.frame_count += 1

            # interpolation factor: 0.0 at start of step, 1.0 at end
            t = self.current_sub / self.sub_frames
            self.current_sub = (self.current_sub + 1) % self.sub_frames

            return self.update(frame, t)
        
        self.ani = animation.FuncAnimation(
            self.fig, animate,
            interval=interval,
            blit=False,
            cache_frame_data=False
        )
        plt.tight_layout()
        plt.show()
        
    
    # Draw the circle boundary representing the MS movement area
    def _draw_boundary(self, cx, cy, boundary_radius):
        boundary_circle = patches.Circle(
            (cx, cy),
            radius=boundary_radius,
            fill=False,
            edgecolor='#ffffff',
            linewidth=1.5,
            linestyle='--',
            alpha=0.3,
            zorder=2
        )
        self.ax.add_patch(boundary_circle)