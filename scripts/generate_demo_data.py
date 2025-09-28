import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd

def generate_enhanced_argo_profiles():
    """Generate additional ARGO float profiles with realistic oceanographic data"""
    
    # Define realistic parameter ranges for different ocean regions
    regions = {
        'tropical': {
            'lat_range': (-10, 10),
            'surface_temp': (27, 30),
            'surface_salinity': (34, 36),
            'thermocline_depth': (80, 120)
        },
        'subtropical': {
            'lat_range': (10, 30),
            'surface_temp': (24, 28),
            'surface_salinity': (35, 37),
            'thermocline_depth': (100, 150)
        },
        'temperate': {
            'lat_range': (30, 50),
            'surface_temp': (18, 24),
            'surface_salinity': (34, 36),
            'thermocline_depth': (150, 200)
        }
    }
    
    # Standard depth levels for ARGO floats
    depths = [0, 5, 10, 20, 30, 50, 75, 100, 150, 200, 300, 400, 500, 600, 750, 1000, 1250, 1500, 1750, 2000]
    
    enhanced_floats = []
    
    for region_name, params in regions.items():
        for i in range(2):  # Generate 2 floats per region
            float_id = f"290{len(enhanced_floats) + 1240:04d}"
            
            # Random position within region
            lat = np.random.uniform(*params['lat_range'])
            lon = np.random.uniform(60, 95)  # Indian Ocean longitude range
            
            # Generate realistic temperature profile
            surface_temp = np.random.uniform(*params['surface_temp'])
            thermocline_depth = np.random.uniform(*params['thermocline_depth'])
            
            temperatures = []
            salinities = []
            pressures = []
            
            for depth in depths:
                # Temperature profile with thermocline
                if depth < thermocline_depth:
                    temp = surface_temp - (depth / thermocline_depth) * 2
                else:
                    temp = surface_temp - 2 - ((depth - thermocline_depth) / 1800) * 25
                
                temp = max(temp, 2.0)  # Deep water minimum
                temperatures.append(round(temp, 1))
                
                # Salinity profile
                surface_sal = np.random.uniform(*params['surface_salinity'])
                if depth < 100:
                    sal = surface_sal + (depth / 100) * 0.3
                elif depth < 1000:
                    sal = surface_sal + 0.3 + ((depth - 100) / 900) * 0.2
                else:
                    sal = surface_sal + 0.5 - ((depth - 1000) / 1000) * 0.3
                
                salinities.append(round(sal, 2))
                
                # Pressure (approximately depth/10)
                pressures.append(round(depth / 10, 1))
            
            # Generate trajectory
            trajectory = []
            base_date = datetime.now() - timedelta(days=30)
            for j in range(6):
                traj_date = base_date + timedelta(days=j*5)
                drift_lat = lat + np.random.uniform(-0.5, 0.5)
                drift_lon = lon + np.random.uniform(-0.5, 0.5)
                trajectory.append({
                    "lat": round(drift_lat, 2),
                    "lon": round(drift_lon, 2),
                    "date": traj_date.strftime("%Y-%m-%d")
                })
            
            float_data = {
                "id": float_id,
                "name": f"{region_name.title()} Ocean Float {i+1}",
                "lat": round(lat, 2),
                "lon": round(lon, 2),
                "status": "active",
                "lastUpdate": datetime.now().isoformat() + "Z",
                "trajectory": trajectory,
                "profiles": [{
                    "date": datetime.now().isoformat() + "Z",
                    "depth": depths,
                    "temperature": temperatures,
                    "salinity": salinities,
                    "pressure": pressures
                }]
            }
            
            enhanced_floats.append(float_data)
    
    return enhanced_floats

def analyze_water_masses(floats_data):
    """Analyze water mass characteristics from ARGO data"""
    
    analysis_results = {
        "water_masses": [],
        "regional_stats": {},
        "thermocline_analysis": []
    }
    
    for float_data in floats_data:
        profile = float_data['profiles'][0]
        depths = profile['depth']
        temps = profile['temperature']
        sals = profile['salinity']
        
        # Find thermocline depth (maximum temperature gradient)
        max_gradient = 0
        thermocline_depth = 0
        
        for i in range(1, len(temps)-1):
            if depths[i+1] - depths[i-1] > 0:
                gradient = abs((temps[i-1] - temps[i+1]) / (depths[i+1] - depths[i-1]))
                if gradient > max_gradient:
                    max_gradient = gradient
                    thermocline_depth = depths[i]
        
        # Mixed layer depth (0.2°C criterion)
        mixed_layer_depth = 0
        surface_temp = temps[0]
        for i, temp in enumerate(temps):
            if surface_temp - temp >= 0.2:
                mixed_layer_depth = depths[i]
                break
        
        # Water mass classification
        surface_temp = temps[0]
        surface_sal = sals[0]
        
        if surface_temp > 28 and surface_sal < 35:
            water_mass = "Tropical Surface Water"
        elif surface_temp > 25 and surface_sal > 35.5:
            water_mass = "Arabian Sea Water"
        elif surface_temp < 25 and surface_sal < 35:
            water_mass = "Bay of Bengal Water"
        else:
            water_mass = "Mixed Water Mass"
        
        analysis_results["thermocline_analysis"].append({
            "float_id": float_data['id'],
            "float_name": float_data['name'],
            "thermocline_depth": thermocline_depth,
            "mixed_layer_depth": mixed_layer_depth,
            "surface_temp": surface_temp,
            "surface_salinity": surface_sal,
            "water_mass": water_mass
        })
    
    return analysis_results

def create_visualization_data():
    """Create data specifically formatted for visualization components"""
    
    # Load existing data
    with open('../data/mock-argo-data.json', 'r') as f:
        existing_data = json.load(f)
    
    # Generate additional floats
    new_floats = generate_enhanced_argo_profiles()
    
    # Combine datasets
    all_floats = existing_data['floats'] + new_floats
    
    # Perform analysis
    analysis = analyze_water_masses(all_floats)
    
    # Create enhanced dataset
    enhanced_dataset = {
        "floats": all_floats,
        "analysis": analysis,
        "sampleQueries": [
            "Show me temperature profiles comparing tropical vs subtropical regions",
            "Display the thermocline depth across all floats",
            "Compare salinity stratification between Arabian Sea and Bay of Bengal",
            "Show me temperature-salinity diagrams for water mass analysis",
            "Display mixed layer depth variations across regions",
            "Compare density profiles between equatorial and southern ocean floats",
            "Show seasonal temperature variations at 100m depth",
            "Display float trajectories with temperature anomalies",
            "Analyze water mass properties and distribution",
            "Show thermocline strength and depth variations"
        ],
        "metadata": {
            "total_floats": len(all_floats),
            "regions_covered": ["Arabian Sea", "Bay of Bengal", "Equatorial Indian Ocean", "Southern Indian Ocean"],
            "depth_range": "0-2000m",
            "parameters": ["Temperature", "Salinity", "Pressure"],
            "last_updated": datetime.now().isoformat()
        }
    }
    
    # Save enhanced dataset
    with open('../data/enhanced-argo-data.json', 'w') as f:
        json.dump(enhanced_dataset, f, indent=2)
    
    print(f"Generated enhanced ARGO dataset with {len(all_floats)} floats")
    print(f"Analysis includes {len(analysis['thermocline_analysis'])} thermocline measurements")
    print("Data saved to enhanced-argo-data.json")
    
    return enhanced_dataset

if __name__ == "__main__":
    # Generate the enhanced dataset
    dataset = create_visualization_data()
    
    # Print summary statistics
    print("\n=== ARGO Dataset Summary ===")
    print(f"Total Floats: {dataset['metadata']['total_floats']}")
    print(f"Regions: {', '.join(dataset['metadata']['regions_covered'])}")
    print(f"Parameters: {', '.join(dataset['metadata']['parameters'])}")
    
    # Print thermocline analysis summary
    thermocline_data = dataset['analysis']['thermocline_analysis']
    avg_thermocline = np.mean([t['thermocline_depth'] for t in thermocline_data])
    avg_mld = np.mean([t['mixed_layer_depth'] for t in thermocline_data])
    
    print(f"\n=== Oceanographic Analysis ===")
    print(f"Average Thermocline Depth: {avg_thermocline:.1f}m")
    print(f"Average Mixed Layer Depth: {avg_mld:.1f}m")
    
    water_masses = {}
    for t in thermocline_data:
        wm = t['water_mass']
        water_masses[wm] = water_masses.get(wm, 0) + 1
    
    print(f"\n=== Water Mass Distribution ===")
    for wm, count in water_masses.items():
        print(f"{wm}: {count} floats")
