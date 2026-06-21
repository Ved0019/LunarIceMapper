from src.data_loader import load_dfsar
from src.radar_utils import calculate_cpr
from src.router import find_optimal_path

def main():
    print("1. Loading lunar spatial data...")
    # data = load_dfsar('data/raw/dfsar_image.tif')
    
    print("2. Computing radar signatures (CPR/DOP)...")
    # ice_mask = calculate_cpr(data)
    
    print("3. Generating safe rover traverse...")
    # path = find_optimal_path(ice_mask, start_coords)
    
    print("Pipeline complete. Check outputs/maps/")

if __name__ == "__main__":
    main()