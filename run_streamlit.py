#!/usr/bin/env python3
"""
Launcher script for Argo AI Ocean Assistant Streamlit applications
"""

import sys
import subprocess
import os
from pathlib import Path

def check_requirements():
    """Check if requirements are installed"""
    try:
        import streamlit
        import pandas
        import plotly
        import folium
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: python setup_streamlit.py")
        return False

def run_basic():
    """Run the basic Streamlit application"""
    print("🌊 Starting Argo AI Ocean Assistant (Basic Version)")
    print("=" * 60)
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])

def run_enhanced():
    """Run the enhanced Streamlit application"""
    print("🌊 Starting Argo AI Ocean Assistant (Enhanced Version)")
    print("=" * 60)
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_enhanced.py"])

def main():
    """Main launcher function"""
    print("🌊 Argo AI Ocean Assistant - Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("streamlit_app.py").exists():
        print("❌ streamlit_app.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Show menu
    print("\nChoose an option:")
    print("1. Run Basic Version (streamlit_app.py)")
    print("2. Run Enhanced Version (streamlit_enhanced.py)")
    print("3. Setup/Install Requirements")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            run_basic()
            break
        elif choice == "2":
            run_enhanced()
            break
        elif choice == "3":
            print("Running setup...")
            subprocess.run([sys.executable, "setup_streamlit.py"])
            break
        elif choice == "4":
            print("Goodbye! 🌊")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
