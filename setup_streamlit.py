#!/usr/bin/env python3
"""
Setup script for Argo AI Ocean Assistant Streamlit application
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_streamlit.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = ["data", "logs", "cache"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_sample_data():
    """Create sample data file if it doesn't exist"""
    print("\n📊 Creating sample data...")
    data_file = Path("data/mock-argo-data.json")
    
    if not data_file.exists():
        sample_data = {
            "floats": [
                {
                    "id": "5901234",
                    "name": "Float 5901234",
                    "lat": 15.5,
                    "lon": 65.2,
                    "status": "active",
                    "lastUpdate": "2024-01-15T10:30:00Z",
                    "trajectory": [
                        {"lat": 15.5, "lon": 65.2, "date": "2024-01-15T10:30:00Z"},
                        {"lat": 15.3, "lon": 65.4, "date": "2024-01-10T10:30:00Z"},
                        {"lat": 15.1, "lon": 65.6, "date": "2024-01-05T10:30:00Z"}
                    ],
                    "profiles": [
                        {
                            "date": "2024-01-15T10:30:00Z",
                            "depth": [0, 10, 20, 50, 100, 200, 500, 1000],
                            "temperature": [28.5, 28.2, 27.8, 26.5, 24.1, 18.2, 12.5, 8.1],
                            "salinity": [35.2, 35.3, 35.4, 35.6, 35.8, 36.1, 36.5, 36.8],
                            "pressure": [0, 10, 20, 50, 100, 200, 500, 1000]
                        }
                    ]
                },
                {
                    "id": "5901235",
                    "name": "Float 5901235",
                    "lat": 12.3,
                    "lon": 78.1,
                    "status": "active",
                    "lastUpdate": "2024-01-14T08:15:00Z",
                    "trajectory": [
                        {"lat": 12.3, "lon": 78.1, "date": "2024-01-14T08:15:00Z"},
                        {"lat": 12.1, "lon": 78.3, "date": "2024-01-09T08:15:00Z"},
                        {"lat": 11.9, "lon": 78.5, "date": "2024-01-04T08:15:00Z"}
                    ],
                    "profiles": [
                        {
                            "date": "2024-01-14T08:15:00Z",
                            "depth": [0, 10, 20, 50, 100, 200, 500, 1000],
                            "temperature": [29.1, 28.9, 28.5, 27.2, 24.8, 19.1, 13.2, 8.5],
                            "salinity": [34.8, 34.9, 35.0, 35.2, 35.4, 35.7, 36.2, 36.6],
                            "pressure": [0, 10, 20, 50, 100, 200, 500, 1000]
                        }
                    ]
                },
                {
                    "id": "5901236",
                    "name": "Float 5901236",
                    "lat": 0.5,
                    "lon": 80.2,
                    "status": "active",
                    "lastUpdate": "2024-01-13T14:20:00Z",
                    "trajectory": [
                        {"lat": 0.5, "lon": 80.2, "date": "2024-01-13T14:20:00Z"},
                        {"lat": 0.3, "lon": 80.4, "date": "2024-01-08T14:20:00Z"},
                        {"lat": 0.1, "lon": 80.6, "date": "2024-01-03T14:20:00Z"}
                    ],
                    "profiles": [
                        {
                            "date": "2024-01-13T14:20:00Z",
                            "depth": [0, 10, 20, 50, 100, 200, 500, 1000],
                            "temperature": [29.8, 29.5, 29.1, 27.8, 25.2, 19.8, 13.8, 8.9],
                            "salinity": [34.2, 34.3, 34.4, 34.6, 34.8, 35.1, 35.6, 36.0],
                            "pressure": [0, 10, 20, 50, 100, 200, 500, 1000]
                        }
                    ]
                }
            ],
            "sampleQueries": [
                "Show me all float locations",
                "Compare temperature profiles",
                "Show salinity data",
                "Arabian Sea analysis",
                "Show comprehensive oceanographic analysis",
                "Display thermocline depths and water masses",
                "Analyze water mass properties",
                "Show temperature-salinity diagrams",
                "Compare mixed layer depths by region"
            ]
        }
        
        with open(data_file, 'w') as f:
            json.dump(sample_data, f, indent=2)
        print(f"✅ Created sample data: {data_file}")
    else:
        print(f"✅ Sample data already exists: {data_file}")

def create_env_template():
    """Create environment variables template"""
    print("\n🔧 Creating environment template...")
    env_file = Path(".env.template")
    
    if not env_file.exists():
        env_content = """# Argo AI Ocean Assistant - Environment Variables
# Copy this file to .env and fill in your API keys

# Optional: For enhanced AI capabilities
GEMINI_API_KEY=your_gemini_api_key_here
ARGOVIS_API_KEY=your_argovis_api_key_here
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here

# Optional: For RAG pipeline configuration
MISTRAL_MODEL_ID=mistralai/Mistral-7B-Instruct-v0.2
ARGO_DUCKDB_PATH=data/argo.duckdb
ARGO_DATA_DIR=data
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created environment template: {env_file}")
    else:
        print(f"✅ Environment template already exists: {env_file}")

def check_streamlit_files():
    """Check if Streamlit files exist"""
    print("\n📄 Checking Streamlit files...")
    files = ["streamlit_app.py", "streamlit_enhanced.py", "requirements_streamlit.txt"]
    
    for file in files:
        if Path(file).exists():
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
            return False
    return True

def run_basic_test():
    """Run a basic test of the Streamlit application"""
    print("\n🧪 Running basic test...")
    try:
        # Import the basic app to check for syntax errors
        import streamlit_app
        print("✅ Basic app imports successfully")
        return True
    except Exception as e:
        print(f"❌ Basic app test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🌊 Argo AI Ocean Assistant - Streamlit Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check Streamlit files
    if not check_streamlit_files():
        print("\n❌ Required Streamlit files are missing")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create sample data
    create_sample_data()
    
    # Create environment template
    create_env_template()
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed during requirements installation")
        sys.exit(1)
    
    # Run basic test
    if not run_basic_test():
        print("\n❌ Setup failed during basic test")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Copy .env.template to .env and add your API keys (optional)")
    print("2. Run the basic version: streamlit run streamlit_app.py")
    print("3. Run the enhanced version: streamlit run streamlit_enhanced.py")
    print("\n📚 For more information, see README_STREAMLIT.md")
    print("\n🌊 Happy ocean data exploring!")

if __name__ == "__main__":
    main()
