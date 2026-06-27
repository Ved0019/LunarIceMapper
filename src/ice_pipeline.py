import rasterio
from rasterio.enums import Resampling
import numpy as np
import matplotlib.pyplot as plt

# Import the math functions we built in the other file!
from radar_utils import calculate_radar_metrics, hunt_for_ice, plot_ice_map

def estimate_ice_volume(ice_mask, pixel_size_meters=5.0, downsample_factor=10, depth_meters=5.0, ice_concentration=0.10):
    """
    Directly addresses Hackathon Objective: "Estimate Ice Volume (0-5m)"
    """
    # Calculate the actual size of our downsampled pixels on the moon
    effective_pixel_size = pixel_size_meters * downsample_factor
    pixel_area_sq_m = effective_pixel_size ** 2
    
    total_ice_pixels = np.sum(ice_mask)
    total_area_sq_m = total_ice_pixels * pixel_area_sq_m
    
    # Volume = Area * Depth * Concentration percentage
    pure_ice_volume_m3 = total_area_sq_m * depth_meters * ice_concentration
    
    # 930 kg per cubic meter of pure ice
    total_mass_metric_tons = (pure_ice_volume_m3 * 930) / 1000
    
    print("\n" + "="*40)
    print("📊 ISRO HACKATHON: RESOURCE ESTIMATE")
    print("="*40)
    print(f"Total Ice-Bearing Area : {total_area_sq_m:,.2f} sq meters")
    print(f"Depth Analyzed         : {depth_meters} meters")
    print(f"Est. Ice Volume        : {pure_ice_volume_m3:,.2f} cubic meters")
    print(f"Est. Total Mass        : {total_mass_metric_tons:,.2f} Metric Tons")
    print("="*40 + "\n")

def run_real_radar_pipeline(xml_file_path, downsample_factor=10):
    print(f"🚀 Loading Real DFSAR Radar Data from: {xml_file_path}")
    
    try:
        with rasterio.open(xml_file_path) as src:
            print(f"✅ Radar Data Opened! Original size: {src.width}x{src.height}")
            print(f"📡 Number of Radar Bands detected: {src.count}")
            
            # Safe dimensions for 8GB RAM
            new_height = int(src.height / downsample_factor)
            new_width = int(src.width / downsample_factor)
            
            print(f"⏬ Downsampling {downsample_factor}x to protect memory...")
            
            # Read Band 1 (Usually Same-Sense Polarization)
            same_sense = src.read(
                1, out_shape=(new_height, new_width), resampling=Resampling.average
            )
            
            # Read Band 2 (Usually Opposite-Sense Polarization)
            # If the file only has 1 band, we will fake the second one just so the code runs without crashing
            if src.count >= 2:
                opp_sense = src.read(
                    2, out_shape=(new_height, new_width), resampling=Resampling.average
                )
            else:
                print("⚠️ Warning: Only 1 radar band found. Simulating 2nd band for testing.")
                opp_sense = same_sense * 0.5 
            
            # --- RUN THE SCIENCE MATH ---
            print("\n🔬 Analyzing Radar Signatures for Subsurface Ice (CPR > 1 & DOP < 0.13)...")
            cpr, dop = calculate_radar_metrics(same_sense, opp_sense)
            
            ice_mask = hunt_for_ice(cpr, dop, cpr_threshold=1.0, dop_threshold=0.13)
            
            # --- ESTIMATE VOLUME (Hackathon Deliverable) ---
            estimate_ice_volume(ice_mask, pixel_size_meters=5.0, downsample_factor=downsample_factor)
            
            # --- SHOW THE RESULTS ---
            plot_ice_map(cpr, ice_mask)
            
    except Exception as e:
        print(f"❌ Error loading radar data: {e}")

if __name__ == "__main__":
    # ⚠️ CHANGE THIS PATH to your new DFSAR .xml file!
    # Example: r"C:\Users\vedya\Development\Hackathon\2026-Bharatiya-Antariksh-Hackathon\LunarIceMapper\data\raw\dfrs_folder\data\calibrated\ch2_dfr_...xml"
    dfsar_file_path = r"PASTE_YOUR_DFSAR_XML_PATH_HERE.xml"
    
    run_real_radar_pipeline(dfsar_file_path, downsample_factor=10)