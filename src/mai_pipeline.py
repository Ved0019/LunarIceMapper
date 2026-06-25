"""
Bharatiya Antariksh Hackathon 2026: Lunar Ice Mapper Pipeline
This script replaces ENVI, MIDAS, and QGIS by running the entire 
remote sensing and routing pipeline natively in Python.
"""

import numpy as np
import rasterio
import matplotlib.pyplot as plt
import networkx as nx
from heapq import heappush, heappop

# ==========================================
# 1. ENVI / MIDAS EQUIVALENT: SAR Processing
# ==========================================
def process_sar_signatures(same_sense_band, opp_sense_band):
    """Computes Circular Polarization Ratio (CPR)."""
    print("[MIDAS Module] Computing Radar Polarimetry (CPR/DOP)...")
    # Avoid divide by zero
    safe_opp = np.where(opp_sense_band == 0, 1e-10, opp_sense_band)
    cpr = same_sense_band / safe_opp
    
    # Mock DOP for structural completeness (Replace with actual Stokes parameters if available)
    dop = np.random.uniform(0.05, 0.5, size=cpr.shape) 
    return cpr, dop

def detect_subsurface_ice(cpr, dop, cpr_thresh=1.0, dop_thresh=0.13):
    """Flags pixels as ice based on hackathon thresholds."""
    print("[Analysis Module] Masking Subsurface Ice...")
    ice_mask = (cpr > cpr_thresh) & (dop < dop_thresh)
    return ice_mask

# ==========================================
# 2. DEM TOOLS EQUIVALENT: Terrain Analysis
# ==========================================
def calculate_terrain_hazards(dem_array, resolution_meters=5):
    """Calculates slope from a Digital Elevation Model (DEM)."""
    print("[DEM Module] Calculating Slope and Terrain Hazards...")
    # Calculate gradients using numpy (rise over run)
    dy, dx = np.gradient(dem_array, resolution_meters)
    slope_radians = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_degrees = np.degrees(slope_radians)
    return slope_degrees

# ==========================================
# 3. AI / OPTIMIZATION EQUIVALENT: Path Planning
# ==========================================
def build_cost_surface(slope, ice_mask, max_safe_slope=15.0):
    """Creates a traversability grid for the rover."""
    print("[Routing Module] Generating Cost Surface Grid...")
    # Base cost is slope. If slope > max_safe_slope, cost is infinity (impassable)
    cost = np.where(slope > max_safe_slope, np.inf, slope * 2.0)
    
    # Reward moving towards ice (lower cost)
    cost = np.where(ice_mask, cost * 0.1, cost)
    return cost

def plan_rover_traverse(cost_surface, start_idx, target_idx):
    """A* Pathfinding Algorithm across the cost grid."""
    print("[Routing Module] Calculating Optimal Safe Path...")
    # (Simplified A* implementation for matrix grids)
    rows, cols = cost_surface.shape
    heap = [(0, start_idx)]
    came_from = {start_idx: None}
    cost_so_far = {start_idx: 0}

    while heap:
        current_cost, current = heappop(heap)
        
        if current == target_idx:
            break
            
        # Check 4-way neighbors
        for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
            neighbor = (current[0] + dr, current[1] + dc)
            
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols:
                move_cost = cost_surface[neighbor]
                if move_cost == np.inf:
                    continue # Hit a steep hazard
                    
                new_cost = cost_so_far[current] + move_cost
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + np.linalg.norm(np.array(target_idx) - np.array(neighbor))
                    heappush(heap, (priority, neighbor))
                    came_from[neighbor] = current
                    
    # Reconstruct path
    path = []
    curr = target_idx
    if curr in came_from:
        while curr != start_idx:
            path.append(curr)
            curr = came_from[curr]
        path.append(start_idx)
        path.reverse()
    return path

# ==========================================
# 4. QGIS / VISUALIZATION EQUIVALENT
# ==========================================
def render_mission_dashboard(dem, ice_mask, path):
    """Plots the final mission map."""
    print("[GIS Module] Rendering Final Mission Maps...")
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot DEM background
    im = ax.imshow(dem, cmap='copper', alpha=0.8)
    plt.colorbar(im, label='Elevation / Topography')
    
    # Overlay Ice in Cyan
    ice_overlay = np.ma.masked_where(~ice_mask, ice_mask)
    ax.imshow(ice_overlay, cmap='cool', alpha=0.9, interpolation='none')
    
    # Plot the Rover Path in bright Green
    if path:
        y_coords, x_coords = zip(*path)
        ax.plot(x_coords, y_coords, color='lime', linewidth=3, label='Rover Traverse')
        ax.scatter([x_coords[0]], [y_coords[0]], color='yellow', s=100, label='Landing Site', zorder=5)
        ax.scatter([x_coords[-1]], [y_coords[-1]], color='red', s=100, marker='X', label='Target Ice', zorder=5)
        
    ax.set_title("Lunar South Pole Mission Planner (Python Automated)")
    ax.legend()
    plt.show()

# ==========================================
# MISSION CONTROL EXECUTION
# ==========================================
if __name__ == "__main__":
    print("🚀 Initiating Lunar Ice Mapper Pipeline...\n")
    
    # 1. Mock Data Loading (Replace with actual rasterio.read() calls)
    grid_size = 100
    mock_dem = np.random.normal(50, 5, (grid_size, grid_size)) # Base terrain
    mock_same_sense = np.random.uniform(0, 10, (grid_size, grid_size))
    mock_opp_sense = np.random.uniform(0, 10, (grid_size, grid_size))
    
    # Simulate a deep crater in the middle with ice
    center_y, center_x = 50, 50
    Y, X = np.ogrid[:grid_size, :grid_size]
    dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
    
    # Crater morphology
    mock_dem[dist_from_center < 15] -= 20 # Deep crater
    mock_same_sense[dist_from_center < 10] = 50 # High backscatter in crater
    mock_opp_sense[dist_from_center < 10] = 5 # Low opposite sense
    
    # 2. Run Pipeline
    cpr, dop = process_sar_signatures(mock_same_sense, mock_opp_sense)
    ice_mask = detect_subsurface_ice(cpr, dop)
    slope = calculate_terrain_hazards(mock_dem)
    
    # 3. Routing
    cost_surface = build_cost_surface(slope, ice_mask)
    start_point = (10, 10)   # Safe, high-ground landing site
    target_point = (50, 50)  # Inside the crater ice deposit
    rover_path = plan_rover_traverse(cost_surface, start_point, target_point)
    
    # 4. Visualization
    render_mission_dashboard(mock_dem, ice_mask, rover_path)