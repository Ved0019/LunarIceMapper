import numpy as np

def calculate_cpr(same_sense_band, opp_sense_band):
    """
    Calculates the Circular Polarization Ratio (CPR).
    Formula: CPR = Same-Sense / Opposite-Sense
    """
    print("Calculating CPR...")
    # Add a tiny number (1e-10) to prevent 'divide by zero' errors on empty pixels
    safe_opp = np.where(opp_sense_band == 0, 1e-10, opp_sense_band)
    cpr = same_sense_band / safe_opp
    return cpr

def create_ice_mask(cpr_array, dop_array, cpr_threshold=1.0, dop_threshold=0.13):
    """
    Flags pixels that match the hackathon's specific subsurface ice criteria:
    CPR > 1.0 AND DOP < 0.13
    """
    print(f"Creating ice mask (CPR > {cpr_threshold}, DOP < {dop_threshold})...")
    # Creates a boolean (True/False) map of where ice is located
    ice_mask = (cpr_array > cpr_threshold) & (dop_array < dop_threshold)
    return ice_mask

def estimate_ice_volume(ice_mask, pixel_area_sq_meters, depth_meters=5, ice_concentration=0.10):
    """
    Estimates the total volume of subsurface ice in the top 5 meters.
    """
    total_ice_pixels = np.sum(ice_mask)
    total_volume = total_ice_pixels * pixel_area_sq_meters * depth_meters * ice_concentration
    print(f"Estimated Ice Volume: {total_volume:,.2f} cubic meters")
    return total_volume