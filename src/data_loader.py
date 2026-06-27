import rasterio
from rasterio.enums import Resampling
import matplotlib.pyplot as plt
import numpy as np

def inspect_pradan_radar(xml_file_path, downsample_factor=20):
    print(f"Attempting to load ISRO PDS4 data from: {xml_file_path}")
    
    try:
        # Open the dataset
        with rasterio.open(xml_file_path) as src:
            print("✅ Data Loaded Successfully!")
            print(f"Coordinate Reference System (CRS): {src.crs}")
            print(f"Original Dimensions: {src.width} x {src.height} pixels")
            
            # Calculate the new, safe dimensions for your RAM
            new_height = int(src.height / downsample_factor)
            new_width = int(src.width / downsample_factor)
            
            print(f"⏬ Downsampling {downsample_factor}x to safe dimensions: {new_width} x {new_height} pixels...")
            
            # Read the array at the lower resolution
            band_1 = src.read(
                1,
                out_shape=(new_height, new_width),
                resampling=Resampling.average
            )
            
            # Plotting the data
            plt.figure(figsize=(10, 8))
            plt.title(f"Chandrayaan-2 OHRC - Downsampled {downsample_factor}x")
            
            # Ignore complete black space (0s or negatives) to get good contrast
            valid_data = band_1[band_1 > 0]
            if len(valid_data) > 0:
                vmin, vmax = np.percentile(valid_data, 2), np.percentile(valid_data, 98)
            else:
                vmin, vmax = None, None

            plt.imshow(band_1, cmap='gray', vmin=vmin, vmax=vmax)
            plt.colorbar(label='Intensity')
            plt.show()

            return band_1, src

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None, None

if __name__ == "__main__":
    # The 'r' ensures Windows paths are read correctly
    file_path = r"C:\Users\vedya\Development\Hackathon\2026-Bharatiya-Antariksh-Hackathon\LunarIceMapper\data\raw\20260103\ch2_ohr_ncp_20260103T1005176450_d_img_d18.xml" 
    
    print("Testing ISRO OHRC Image Load (Safe RAM Mode)...")
    band_1_data, metadata = inspect_pradan_radar(file_path, downsample_factor=20)