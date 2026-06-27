import numpy as np
import matplotlib.pyplot as plt

def calculate_radar_metrics(same_sense_band, opp_sense_band):
    """
    Computes Circular Polarization Ratio (CPR).
    CPR = Same-Sense Polarization / Opposite-Sense Polarization
    """
    print("🧠 Calculating Circular Polarization Ratio (CPR)...")
    
    # Add a tiny number to the denominator to prevent "divide by zero" crashes
    safe_opp = np.where(opp_sense_band == 0, 1e-10, opp_sense_band)
    cpr = same_sense_band / safe_opp
    
    # Note: Real DOP requires full Stokes vectors from the radar data. 
    # If the hackathon data doesn't provide all 4 Stokes parameters, 
    # we simulate DOP derivation based on cross-polarization variance.
    print("🧠 Extracting Degree of Polarization (DOP)...")
    dop = safe_opp / (same_sense_band + safe_opp + 1e-10) 
    
    return cpr, dop

def hunt_for_ice(cpr, dop, cpr_threshold=1.0, dop_threshold=0.13):
    """
    Applies the hackathon's specific thresholds to flag subsurface ice.
    Criteria: CPR > 1.0 AND DOP < 0.13
    """
    print(f"🎯 Hunting for Ice (CPR > {cpr_threshold} & DOP < {dop_threshold})...")
    
    # Creates a binary mask (True = Ice, False = No Ice)
    ice_mask = (cpr > cpr_threshold) & (dop < dop_threshold)
    
    total_ice_pixels = np.sum(ice_mask)
    print(f"✅ Found {total_ice_pixels:,} pixels containing potential subsurface ice!")
    
    return ice_mask

def plot_ice_map(cpr, ice_mask):
    """
    Visualizes the radar data and highlights the detected ice in bright cyan.
    """
    plt.figure(figsize=(12, 8))
    
    # Plot the base radar image (CPR)
    plt.title("Subsurface Ice Detection Map")
    plt.imshow(cpr, cmap='gray', vmin=0, vmax=2)
    
    # Overlay the detected ice in bright cyan
    # We use numpy masked arrays to make the 'False' pixels transparent
    ice_overlay = np.ma.masked_where(~ice_mask, ice_mask)
    plt.imshow(ice_overlay, cmap='cool', alpha=0.8, interpolation='none')
    
    plt.colorbar(label='Radar CPR (Gray) / Ice Deposits (Cyan)')
    plt.show()

# --- For Testing the Math ---
if __name__ == "__main__":
    # Create fake radar data to test the logic
    print("Running synthetic test...")
    fake_same_sense = np.random.uniform(0.5, 2.0, (500, 500))
    fake_opp_sense = np.random.uniform(0.1, 1.5, (500, 500))
    
    # Inject a "block of ice" in the middle of our fake data
    fake_same_sense[200:300, 200:300] = 5.0 # High same-sense reflection
    fake_opp_sense[200:300, 200:300] = 0.5  # Low opposite-sense
    
    # Run the pipeline
    cpr, dop = calculate_radar_metrics(fake_same_sense, fake_opp_sense)
    ice_map = hunt_for_ice(cpr, dop)
    plot_ice_map(cpr, ice_map)