#!/usr/bin/env python3
"""
Test script for Streamlit application
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("SUCCESS: Streamlit imported successfully")
    except ImportError as e:
        print(f"ERROR: Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("SUCCESS: Pandas imported successfully")
    except ImportError as e:
        print(f"ERROR: Pandas import failed: {e}")
        return False
    
    try:
        import plotly.graph_objects as go
        print("SUCCESS: Plotly imported successfully")
    except ImportError as e:
        print(f"ERROR: Plotly import failed: {e}")
        return False
    
    try:
        import folium
        print("SUCCESS: Folium imported successfully")
    except ImportError as e:
        print(f"ERROR: Folium import failed: {e}")
        return False
    
    try:
        from streamlit_folium import st_folium
        print("SUCCESS: Streamlit-folium imported successfully")
    except ImportError as e:
        print(f"ERROR: Streamlit-folium import failed: {e}")
        return False
    
    return True

def test_app_imports():
    """Test if the Streamlit apps can be imported"""
    print("\nTesting app imports...")
    
    try:
        import streamlit_app
        print("SUCCESS: Basic app imported successfully")
    except Exception as e:
        print(f"ERROR: Basic app import failed: {e}")
        return False
    
    try:
        import streamlit_enhanced
        print("SUCCESS: Enhanced app imported successfully")
    except Exception as e:
        print(f"ERROR: Enhanced app import failed: {e}")
        return False
    
    return True

def test_data_loading():
    """Test data loading functions"""
    print("\nTesting data loading...")
    
    try:
        import streamlit_app
        data = streamlit_app.load_mock_data()
        
        if data and "floats" in data:
            print(f"SUCCESS: Data loaded successfully: {len(data['floats'])} floats")
            return True
        else:
            print("ERROR: Data loading failed: Invalid data structure")
            return False
    except Exception as e:
        print(f"ERROR: Data loading failed: {e}")
        return False

def test_visualization_functions():
    """Test visualization functions"""
    print("\nTesting visualization functions...")
    
    try:
        import streamlit_app
        
        # Test with sample data
        sample_floats = [
            {
                "id": "test1",
                "name": "Test Float 1",
                "lat": 15.5,
                "lon": 65.2,
                "status": "active",
                "lastUpdate": "2024-01-15T10:30:00Z",
                "trajectory": [{"lat": 15.5, "lon": 65.2, "date": "2024-01-15T10:30:00Z"}],
                "profiles": [{
                    "date": "2024-01-15T10:30:00Z",
                    "depth": [0, 10, 20, 50, 100],
                    "temperature": [28.5, 28.2, 27.8, 26.5, 24.1],
                    "salinity": [35.2, 35.3, 35.4, 35.6, 35.8],
                    "pressure": [0, 10, 20, 50, 100]
                }]
            }
        ]
        
        # Test profile chart
        try:
            chart = streamlit_app.create_profile_chart(sample_floats, "temperature")
            if chart:
                print("SUCCESS: Profile chart creation successful")
            else:
                print("ERROR: Profile chart creation failed - returned None")
                return False
        except Exception as e:
            print(f"ERROR: Profile chart creation failed: {e}")
            return False
        
        # Test map creation
        map_obj = streamlit_app.create_float_map(sample_floats)
        if map_obj:
            print("SUCCESS: Map creation successful")
        else:
            print("ERROR: Map creation failed")
            return False
        
        # Test anomaly chart
        sample_data = [{"year": 2020, "temp": 15.0}, {"year": 2021, "temp": 15.5}]
        anomaly_chart = streamlit_app.create_anomaly_chart(sample_data)
        if anomaly_chart is not None:
            print("SUCCESS: Anomaly chart creation successful")
        else:
            print("ERROR: Anomaly chart creation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"ERROR: Visualization testing failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Argo AI Ocean Assistant - Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_app_imports,
        test_data_loading,
        test_visualization_functions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("   streamlit run streamlit_app.py")
        print("   streamlit run streamlit_enhanced.py")
    else:
        print("ERROR: Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
