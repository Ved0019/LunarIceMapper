import numpy as np

def compute_rimm_ice_fraction(eps_eff, eps_reg=3.0, eps_ice=3.15):
    """
    Applies the Refractive Index Mixing Model (RIMM) to back-calculate 
    the volumetric ice fraction from the effective dielectric constant.
    
    Formula: phi_ice = (sqrt(eps_eff) - sqrt(eps_reg)) / (sqrt(eps_ice) - sqrt(eps_reg))
    """
    sqrt_reg = np.sqrt(eps_reg)
    sqrt_ice = np.sqrt(eps_ice)
    
    # Avoid numerical anomalies if the dielectric constants match exactly
    if np.isclose(sqrt_ice, sqrt_reg):
        return np.zeros_like(eps_eff)
        
    phi_ice = (np.sqrt(eps_eff) - sqrt_reg) / (sqrt_ice - sqrt_reg)
    # Clip bounds to ensure realistic physical limits [0, 1]
    return np.clip(phi_ice, 0.0, 1.0)

def calculate_radar_penetration_depth(wavelength_m, eps_real, loss_tangent=0.01):
    """
    Computes the electrical skin depth (penetration boundary) of the SAR signal.
    """
    denominator = 2 * np.pi * np.sqrt(eps_real) * loss_tangent
    if denominator == 0:
        return 0.0
    return wavelength_m / denominator

def estimate_total_crater_ice(ice_mask, pixel_resolution_m, target_depth_m=5.0, static_concentration=0.12):
    """
    Integrates total volume and mass of water ice within the identified 
    high-probability polarimetric mask areas.
    """
    # Calculate surface area of a single pixel
    pixel_area_sq_m = pixel_resolution_m ** 2
    
    # Sum up all matching pixels
    total_ice_pixels = np.sum(ice_mask)
    total_ice_area = total_ice_pixels * pixel_area_sq_m
    
    # Volume calculation bounded by maximum depth profile
    total_bulk_volume = total_ice_area * target_depth_m
    pure_ice_volume = total_bulk_volume * static_concentration
    
    # Density of pure compact water ice at lunar cryogenic temperatures (~930 kg/m^3)
    ice_density_kg_m3 = 930.0
    total_mass_kg = pure_ice_volume * ice_density_kg_m3
    
    metrics = {
        "ice_area_sq_m": total_ice_area,
        "bulk_volume_m3": total_bulk_volume,
        "pure_ice_volume_m3": pure_ice_volume,
        "total_mass_metric_tons": total_mass_kg / 1000.0
    }
    
    print("\n=== Resource Estimation Engine ===")
    print(f"Total Detected Ice Area: {metrics['ice_area_sq_m']:,.2f} sq meters")
    print(f"Estimated Resource Mass: {metrics['total_mass_metric_tons']:,.2f} Metric Tons")
    return metrics

if __name__ == "__main__":
    # Test script verification using synthetic matrix arrays
    mock_ice_mask = np.random.choice([True, False], size=(200, 200), p=[0.05, 0.95])
    # Assume Chandrayaan-2 DFSAR L-band data with ~5 meter spatial pixel resolution
    results = estimate_total_crater_ice(mock_ice_mask, pixel_resolution_m=5.0)