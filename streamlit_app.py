"""
Argo AI Ocean Assistant - Streamlit Application
Converted from Next.js to Streamlit for oceanographic data visualization and analysis.
"""
print("Hello from Awadhoot!")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import json
import requests
from datetime import datetime, timedelta
import io
import base64
from typing import List, Dict, Any, Optional, Tuple
import os
import sys

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import backend modules
try:
    from backend.rag_pipeline import RagPipeline
    from backend.config import Config
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    st.warning("Backend modules not available. Running in demo mode.")

# Page configuration
st.set_page_config(
    page_title="Argo AI Ocean Assistant",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Modern Dashboard Theme
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global font family */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Main app background - Dark theme */
    .stApp > header {
        background-color: #0D1B2A;
    }
    
    .stApp {
        background-color: #0F172A;
    }
    
    /* Main header styling - Professional and minimal */
    .main-header {
        background: linear-gradient(135deg, #0D1B2A 0%, #1E293B 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 20px rgba(13, 27, 42, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-header h1 {
        color: white !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin: 0 0 0.5rem 0 !important;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.8) !important;
        font-size: 1.125rem !important;
        font-weight: 400;
        margin: 0 !important;
        line-height: 1.6;
    }
    
    /* Chat message styling - Dark theme */
    .chat-message {
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        font-size: 15px;
        line-height: 1.6;
        font-weight: 400;
    }
    
    .user-message {
        background: #1E293B;
        border-left: 4px solid #14B8A6;
        color: #FFFFFF !important;
        font-weight: 500;
    }
    
    .assistant-message {
        background: #1E293B;
        border-left: 4px solid #38BDF8;
        color: #FFFFFF !important;
        font-weight: 500;
    }
    
    /* Modern button styling */
    .stButton > button {
        background: #14B8A6;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        font-size: 14px;
        padding: 0.75rem 1.5rem;
        box-shadow: 0 2px 4px rgba(20, 184, 166, 0.2);
        transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .stButton > button:hover {
        background: #0F9488;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(20, 184, 166, 0.3);
    }
    
    /* Secondary button styling - Dark theme */
    .stButton > button[kind="secondary"] {
        background: transparent;
        color: #E2E8F0;
        border: 1px solid #475569;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #334155;
        border-color: #64748B;
    }
    
    /* Metric cards - Dark theme */
    .metric-card {
        background: #1E293B;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Sidebar styling - Professional dark theme */
    .css-1d391kg {
        background: #0D1B2A;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .css-1d391kg .stMarkdown {
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Responsive sidebar */
    @media (max-width: 768px) {
        .mobile-menu-toggle {
            display: block !important;
            position: fixed !important;
            top: 1rem !important;
            left: 1rem !important;
            z-index: 1000 !important;
        }
        
        .css-1d391kg {
            width: 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            height: 100vh !important;
            z-index: 999 !important;
            transform: translateX(-100%) !important;
            transition: transform 0.3s ease-in-out !important;
        }
        
        .css-1d391kg[data-testid="stSidebar"][aria-expanded="true"] {
            transform: translateX(0) !important;
        }
        
        /* Add overlay when sidebar is open */
        .sidebar-overlay {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            background: rgba(0, 0, 0, 0.5) !important;
            z-index: 998 !important;
            display: none !important;
        }
        
        .css-1d391kg[data-testid="stSidebar"][aria-expanded="true"] + .sidebar-overlay {
            display: block !important;
        }
        
        /* Main content adjustment for mobile */
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        
        /* Mobile header adjustments */
        .main-header {
            padding: 1rem !important;
            margin: 0.5rem !important;
        }
        
        .main-header h1 {
            font-size: 1.5rem !important;
        }
        
        .main-header p {
            font-size: 0.9rem !important;
        }
        
        /* Mobile chat interface */
        .chat-container {
            padding: 0.5rem !important;
        }
        
        .user-message,
        .assistant-message {
            padding: 0.75rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Mobile visualization adjustments */
        .js-plotly-plot {
            height: 300px !important;
        }
        
        /* Mobile button adjustments */
        .stButton > button {
            width: 100% !important;
            margin: 0.25rem 0 !important;
        }
        
        /* Mobile metric cards */
        .metric-card {
            margin: 0.5rem 0 !important;
            padding: 1rem !important;
        }
        
        /* Mobile tabs */
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            min-width: auto !important;
            flex: 1 !important;
            font-size: 0.9rem !important;
        }
    }
    
    @media (max-width: 480px) {
        /* Extra small screens */
        .main-header h1 {
            font-size: 1.25rem !important;
        }
        
        .main-header p {
            font-size: 0.8rem !important;
        }
        
        .user-message,
        .assistant-message {
            padding: 0.5rem !important;
            font-size: 0.9rem !important;
        }
        
        .js-plotly-plot {
            height: 250px !important;
        }
        
        .metric-card {
            padding: 0.75rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 0.8rem !important;
            padding: 0.5rem !important;
        }
    }
    
    /* Tablet adjustments */
    @media (min-width: 769px) and (max-width: 1024px) {
        .css-1d391kg {
            width: 280px !important;
            min-width: 280px !important;
        }
        
        .main .block-container {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        
        .js-plotly-plot {
            height: 400px !important;
        }
    }
    
    /* Large screen optimizations */
    @media (min-width: 1200px) {
        .main .block-container {
            max-width: 1200px !important;
            margin: 0 auto !important;
        }
        
        .js-plotly-plot {
            height: 500px !important;
        }
    }
    
    /* Text input styling - Dark theme */
    .stTextInput > div > div > input {
        background-color: #1E293B;
        border: 1px solid #475569;
        border-radius: 8px;
        font-size: 14px;
        color: #FFFFFF;
        padding: 0.75rem 1rem;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #14B8A6;
        box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.2);
        outline: none;
    }
    
    /* Selectbox styling - Dark theme */
    .stSelectbox > div > div {
        background-color: #1E293B;
        border: 1px solid #475569;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        color: #FFFFFF;
    }
    
    /* Tabs styling - Dark theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #334155;
        border-radius: 8px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: nowrap;
        background: transparent;
        border-radius: 6px;
        padding: 0 1rem;
        font-weight: 500;
        color: #94A3B8;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: #1E293B;
        color: #FFFFFF !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* Chart styling - Dark theme */
    .js-plotly-plot {
        background-color: #1E293B !important;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Alert styling - Clean and modern */
    .stAlert {
        border-radius: 8px;
        font-weight: 400;
        border: none;
        font-family: 'Inter', sans-serif;
    }
    
    .stInfo {
        background: #EFF6FF;
        color: #1E40AF;
        border-left: 4px solid #3B82F6;
    }
    
    .stSuccess {
        background: #ECFDF5;
        color: #065F46;
        border-left: 4px solid #10B981;
    }
    
    .stWarning {
        background: #FFFBEB;
        color: #92400E;
        border-left: 4px solid #F59E0B;
    }
    
    .stError {
        background: #FEF2F2;
        color: #991B1B;
        border-left: 4px solid #EF4444;
    }
    
    /* Typography improvements - Dark theme */
    .stMarkdown {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }
    
    .stMarkdown h1 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        margin-bottom: 1rem !important;
        letter-spacing: -0.02em;
    }
    
    .stMarkdown h2 {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 1.5rem !important;
        margin-bottom: 0.75rem !important;
        letter-spacing: -0.01em;
    }
    
    .stMarkdown h3 {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stMarkdown p {
        color: #E2E8F0 !important;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    /* Ensure all text is visible - Dark theme */
    .stText {
        color: #FFFFFF !important;
    }
    
    .stSelectbox label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    .stTextInput label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    .stFileUploader label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    .stButton label {
        color: #FFFFFF !important;
    }
    
    /* Sidebar text visibility */
    .css-1d391kg .stMarkdown {
        color: #FFFFFF !important;
    }
    
    .css-1d391kg .stText {
        color: #FFFFFF !important;
    }
    
    .css-1d391kg .stSelectbox label {
        color: #FFFFFF !important;
    }
    
    .css-1d391kg .stTextInput label {
        color: #FFFFFF !important;
    }
    
    .css-1d391kg .stButton label {
        color: #FFFFFF !important;
    }
    
    /* Metric styling - Dark theme */
    [data-testid="metric-container"] {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        font-family: 'Inter', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* File uploader styling - Dark theme */
    .stFileUploader > div {
        background: #1E293B;
        border: 2px dashed #475569;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #14B8A6;
        background: #0F172A;
    }
    
    /* Container spacing and layout */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Additional text visibility fixes - Dark theme */
    .stApp > div {
        color: #FFFFFF !important;
    }
    
    .stApp .main .block-container {
        color: #FFFFFF !important;
    }
    
    .stApp .main .block-container * {
        color: inherit !important;
    }
    
    /* Ensure all Streamlit text elements are visible - Dark theme */
    .stApp [data-testid="stText"] {
        color: #FFFFFF !important;
    }
    
    .stApp [data-testid="stMarkdown"] {
        color: #FFFFFF !important;
    }
    
    .stApp [data-testid="stSelectbox"] label {
        color: #FFFFFF !important;
    }
    
    .stApp [data-testid="stTextInput"] label {
        color: #FFFFFF !important;
    }
    
    .stApp [data-testid="stFileUploader"] label {
        color: #FFFFFF !important;
    }
    
    /* Sidebar specific fixes */
    .stApp .css-1d391kg * {
        color: #FFFFFF !important;
    }
    
    .stApp .css-1d391kg [data-testid="stText"] {
        color: #FFFFFF !important;
    }
    
    .stApp .css-1d391kg [data-testid="stMarkdown"] {
        color: #FFFFFF !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F3F4F6;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #D1D5DB;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #9CA3AF;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_visualization' not in st.session_state:
    st.session_state.current_visualization = None
if 'netcdf_summary' not in st.session_state:
    st.session_state.netcdf_summary = None
if 'ai_status' not in st.session_state:
    st.session_state.ai_status = {"aiEnhanced": False, "provider": "Demo Mode"}

# Sample data for demo
SAMPLE_DATA = [
    {"year": 2010, "temp": 14.1},
    {"year": 2011, "temp": 14.2},
    {"year": 2012, "temp": 14.3},
    {"year": 2013, "temp": 14.4},
    {"year": 2014, "temp": 14.6},
    {"year": 2015, "temp": 15.0},
    {"year": 2016, "temp": 16.1, "anomaly": True},
    {"year": 2017, "temp": 15.2},
    {"year": 2018, "temp": 15.0},
    {"year": 2019, "temp": 15.1},
    {"year": 2020, "temp": 15.3},
]

SAMPLE_QUERIES = [
    "Show me all float locations",
    "Compare temperature profiles",
    "Compare salinity data",
    "Arabian Sea temperature",
    "Bay of Bengal salinity",
    "Equatorial analysis",
    "Show T-S diagram",
    "Display float trajectories",
    "Southern Ocean temperature",
    "Show comprehensive oceanographic analysis",
    "Display thermocline depths and water masses"
]

def load_mock_data():
    """Load mock ARGO float data with error handling"""
    try:
        # Try to load from data directory first
        data_path = 'data/mock-argo-data.json'
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                data = json.load(f)
                st.success("✅ Loaded data from file")
                return data
    except Exception as e:
        st.warning(f"⚠️ Could not load data file: {e}")
    
    # Fallback mock data
    st.info("📊 Using built-in sample data")
    return {
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
        "sampleQueries": SAMPLE_QUERIES
    }

def generate_realistic_float_data(region: str, num_floats: int = 3) -> List[Dict]:
    """Generate realistic ARGO float data for different regions with seasonal variations"""
    import random
    import numpy as np
    
    base_data = load_mock_data()["floats"]
    
    # Add some seasonal variation
    seasonal_factor = random.uniform(0.8, 1.2)
    
    if region.lower() == "arabian sea":
        # Arabian Sea characteristics: higher salinity, warm temperatures
        region_floats = []
        for i in range(num_floats):
            lat = random.uniform(15, 25)
            lon = random.uniform(60, 75)
            float_data = {
                "id": f"590{1000 + i}",
                "name": f"Arabian Sea Float {i+1}",
                "lat": lat,
                "lon": lon,
                "status": "active",
                "lastUpdate": "2024-01-15T10:30:00Z",
                "trajectory": [
                    {"lat": lat, "lon": lon, "date": "2024-01-15T10:30:00Z"},
                    {"lat": lat + random.uniform(-0.5, 0.5), "lon": lon + random.uniform(-0.5, 0.5), "date": "2024-01-10T10:30:00Z"},
                    {"lat": lat + random.uniform(-1, 1), "lon": lon + random.uniform(-1, 1), "date": "2024-01-05T10:30:00Z"}
                ],
                "profiles": [{
                    "date": "2024-01-15T10:30:00Z",
                    "depth": [0, 10, 20, 50, 100, 200, 500, 1000],
                    "temperature": [(29.5 + random.uniform(-1, 1)) * seasonal_factor, 29.2 * seasonal_factor, 28.8 * seasonal_factor, 27.5 * seasonal_factor, 25.1, 19.2, 13.5, 8.2],
                    "salinity": [(36.2 + random.uniform(-0.2, 0.2)) * seasonal_factor, 36.3 * seasonal_factor, 36.4 * seasonal_factor, 36.6 * seasonal_factor, 36.8, 37.1, 37.5, 37.8],
                    "pressure": [0, 10, 20, 50, 100, 200, 500, 1000]
                }]
            }
            region_floats.append(float_data)
        return region_floats
    
    elif region.lower() == "bay of bengal":
        # Bay of Bengal characteristics: lower salinity, freshwater influence
        region_floats = []
        for i in range(num_floats):
            lat = random.uniform(10, 20)
            lon = random.uniform(80, 95)
            float_data = {
                "id": f"590{2000 + i}",
                "name": f"Bay of Bengal Float {i+1}",
                "lat": lat,
                "lon": lon,
                "status": "active",
                "lastUpdate": "2024-01-14T08:15:00Z",
                "trajectory": [
                    {"lat": lat, "lon": lon, "date": "2024-01-14T08:15:00Z"},
                    {"lat": lat + random.uniform(-0.5, 0.5), "lon": lon + random.uniform(-0.5, 0.5), "date": "2024-01-09T08:15:00Z"},
                    {"lat": lat + random.uniform(-1, 1), "lon": lon + random.uniform(-1, 1), "date": "2024-01-04T08:15:00Z"}
                ],
                "profiles": [{
                    "date": "2024-01-14T08:15:00Z",
                    "depth": [0, 10, 20, 50, 100, 200, 500, 1000],
                    "temperature": [(28.8 + random.uniform(-0.5, 0.5)) * seasonal_factor, 28.5 * seasonal_factor, 28.1 * seasonal_factor, 26.8 * seasonal_factor, 24.4, 18.7, 12.8, 8.1],
                    "salinity": [(33.8 + random.uniform(-0.3, 0.3)) * seasonal_factor, 33.9 * seasonal_factor, 34.0 * seasonal_factor, 34.2 * seasonal_factor, 34.4, 34.7, 35.2, 35.6],
                    "pressure": [0, 10, 20, 50, 100, 200, 500, 1000]
                }]
            }
            region_floats.append(float_data)
        return region_floats
    
    elif region.lower() == "equatorial":
        # Equatorial characteristics: warm, low salinity, strong thermocline
        region_floats = []
        for i in range(num_floats):
            lat = random.uniform(-5, 5)
            lon = random.uniform(75, 85)
            float_data = {
                "id": f"590{3000 + i}",
                "name": f"Equatorial Float {i+1}",
                "lat": lat,
                "lon": lon,
                "status": "active",
                "lastUpdate": "2024-01-13T14:20:00Z",
                "trajectory": [
                    {"lat": lat, "lon": lon, "date": "2024-01-13T14:20:00Z"},
                    {"lat": lat + random.uniform(-0.5, 0.5), "lon": lon + random.uniform(-0.5, 0.5), "date": "2024-01-08T14:20:00Z"},
                    {"lat": lat + random.uniform(-1, 1), "lon": lon + random.uniform(-1, 1), "date": "2024-01-03T14:20:00Z"}
                ],
                "profiles": [{
                    "date": "2024-01-13T14:20:00Z",
                    "depth": [0, 10, 20, 50, 100, 200, 500, 1000],
                    "temperature": [(30.2 + random.uniform(-0.5, 0.5)) * seasonal_factor, 29.9 * seasonal_factor, 29.5 * seasonal_factor, 28.2 * seasonal_factor, 25.8, 20.2, 14.2, 9.1],
                    "salinity": [(34.0 + random.uniform(-0.2, 0.2)) * seasonal_factor, 34.1 * seasonal_factor, 34.2 * seasonal_factor, 34.4 * seasonal_factor, 34.6, 34.9, 35.4, 35.8],
                    "pressure": [0, 10, 20, 50, 100, 200, 500, 1000]
                }]
            }
            region_floats.append(float_data)
        return region_floats
    
    elif region.lower() == "southern ocean":
        # Southern Ocean characteristics: cold, high salinity, deep mixed layer
        region_floats = []
        for i in range(num_floats):
            lat = random.uniform(-60, -40)
            lon = random.uniform(0, 60)
            float_data = {
                "id": f"590{4000 + i}",
                "name": f"Southern Ocean Float {i+1}",
                "lat": lat,
                "lon": lon,
                "status": "active",
                "lastUpdate": "2024-01-12T06:45:00Z",
                "trajectory": [
                    {"lat": lat, "lon": lon, "date": "2024-01-12T06:45:00Z"},
                    {"lat": lat + random.uniform(-0.5, 0.5), "lon": lon + random.uniform(-0.5, 0.5), "date": "2024-01-07T06:45:00Z"},
                    {"lat": lat + random.uniform(-1, 1), "lon": lon + random.uniform(-1, 1), "date": "2024-01-02T06:45:00Z"}
                ],
                "profiles": [{
                    "date": "2024-01-12T06:45:00Z",
                    "depth": [0, 10, 20, 50, 100, 200, 500, 1000],
                    "temperature": [(2.5 + random.uniform(-1, 1)) * seasonal_factor, 2.2 * seasonal_factor, 1.8 * seasonal_factor, 1.5 * seasonal_factor, 1.2, 0.8, 0.5, 0.2],
                    "salinity": [(34.8 + random.uniform(-0.1, 0.1)) * seasonal_factor, 34.9 * seasonal_factor, 35.0 * seasonal_factor, 35.1 * seasonal_factor, 35.2, 35.3, 35.4, 35.5],
                    "pressure": [0, 10, 20, 50, 100, 200, 500, 1000]
                }]
            }
            region_floats.append(float_data)
        return region_floats
    
    else:
        # Default: mix of different regions
        return base_data[:num_floats]

def process_natural_language_query(query: str) -> Dict[str, Any]:
    """Process natural language queries and return structured responses"""
    lower_query = query.lower()
    
    # Greeting handling
    greeting_regex = r'^(hi+|hello+|hey+|yo+|hiya|hola|namaste|good\s*(morning|afternoon|evening))\b|(how\s*are\s*you\??)$'
    if any(word in lower_query for word in ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return {
            "type": "greeting",
            "message": "Hi! I'm your Ocean Data Assistant. Ask me about ARGO float locations, temperature/salinity, or comparisons.",
            "suggestions": [
                "Show me all float locations",
                "Compare temperature at 100m",
                "Show salinity near equator",
            ],
        }
    
    # T-S diagram queries
    if any(word in lower_query for word in ['t-s diagram', 'temperature salinity', 'water mass', 'ts diagram']):
        arabian_floats = generate_realistic_float_data("arabian sea", 2)
        bengal_floats = generate_realistic_float_data("bay of bengal", 2)
        equatorial_floats = generate_realistic_float_data("equatorial", 2)
        all_floats = arabian_floats + bengal_floats + equatorial_floats
        
        return {
            "type": "ts_diagram",
            "floats": all_floats,
            "message": "Temperature-Salinity diagram showing water mass characteristics across different regions. Each curve represents a different water mass with distinct T-S properties.",
            "suggestions": [
                "Show temperature profiles by region",
                "Compare salinity stratification between regions",
                "Display float trajectories with temperature data",
            ],
        }
    
    # Advanced oceanographic analysis
    if any(word in lower_query for word in ['thermocline', 'water mass', 'analysis', 'mixed layer', 'density']):
        # Mix different regions for comprehensive analysis
        arabian_floats = generate_realistic_float_data("arabian sea", 2)
        bengal_floats = generate_realistic_float_data("bay of bengal", 2)
        equatorial_floats = generate_realistic_float_data("equatorial", 2)
        all_floats = arabian_floats + bengal_floats + equatorial_floats
        
        return {
            "type": "analysis",
            "floats": all_floats,
            "message": "Here's a comprehensive oceanographic analysis including thermocline depths, water mass identification, and regional comparisons across Arabian Sea, Bay of Bengal, and Equatorial regions.",
            "suggestions": [
                "Show me temperature profiles by region",
                "Compare salinity stratification between regions",
                "Display float trajectories with temperature data",
            ],
        }
    
    # Salinity queries
    if 'salinity' in lower_query:
        if 'compare' in lower_query or 'comparison' in lower_query:
            # Multi-region comparison
            arabian_floats = generate_realistic_float_data("arabian sea", 2)
            bengal_floats = generate_realistic_float_data("bay of bengal", 2)
            equatorial_floats = generate_realistic_float_data("equatorial", 2)
            all_floats = arabian_floats + bengal_floats + equatorial_floats
            
            return {
                "type": "comparison",
                "variable": "salinity",
                "floats": all_floats,
                "message": "Salinity comparison across different regions: Arabian Sea (high ~36.2-37.8 PSU), Bay of Bengal (low ~33.8-35.6 PSU), Equatorial (moderate ~34.0-35.8 PSU).",
                "suggestions": [
                    "Show temperature comparison",
                    "Display T-S diagram",
                    "Analyze water mass properties",
                ],
            }
        elif 'equator' in lower_query or 'equatorial' in lower_query:
            floats = generate_realistic_float_data("equatorial", 4)
            return {
                "type": "profile",
                "variable": "salinity",
                "floats": floats,
                "message": "Equatorial salinity profiles showing moderate salinity values (~34.0-35.8 PSU) due to high precipitation and freshwater input from rainfall.",
                "suggestions": [
                    "Compare with Arabian Sea salinity",
                    "Show temperature profiles",
                    "Display T-S diagram",
                ],
            }
        elif 'arabian' in lower_query:
            floats = generate_realistic_float_data("arabian sea", 4)
            return {
                "type": "profile",
                "variable": "salinity",
                "floats": floats,
                "message": "Arabian Sea salinity profiles showing high salinity values (~36.2-37.8 PSU) due to high evaporation rates and limited freshwater input.",
                "suggestions": [
                    "Compare with Bay of Bengal salinity",
                    "Show temperature profiles",
                    "Display water mass analysis",
                ],
            }
        elif 'bengal' in lower_query or 'bay of bengal' in lower_query:
            floats = generate_realistic_float_data("bay of bengal", 4)
            return {
                "type": "profile",
                "variable": "salinity",
                "floats": floats,
                "message": "Bay of Bengal salinity profiles showing low salinity values (~33.8-35.6 PSU) due to freshwater input from major rivers like Ganges and Brahmaputra.",
                "suggestions": [
                    "Compare with Arabian Sea salinity",
                    "Show temperature profiles",
                    "Display seasonal variations",
                ],
            }
        else:
            # Default salinity query - show comparison
            arabian_floats = generate_realistic_float_data("arabian sea", 2)
            bengal_floats = generate_realistic_float_data("bay of bengal", 2)
            equatorial_floats = generate_realistic_float_data("equatorial", 2)
            all_floats = arabian_floats + bengal_floats + equatorial_floats
            
            return {
                "type": "comparison",
                "variable": "salinity",
                "floats": all_floats,
                "message": "Salinity profiles across different ocean regions: Arabian Sea (high salinity), Bay of Bengal (low salinity), and Equatorial (moderate salinity).",
                "suggestions": [
                    "Show specific region analysis",
                    "Display temperature comparison",
                    "Analyze water mass properties",
                ],
            }
    
    # Temperature queries
    if 'temperature' in lower_query:
        if 'compare' in lower_query or 'comparison' in lower_query:
            # Multi-region comparison
            arabian_floats = generate_realistic_float_data("arabian sea", 2)
            bengal_floats = generate_realistic_float_data("bay of bengal", 2)
            equatorial_floats = generate_realistic_float_data("equatorial", 2)
            all_floats = arabian_floats + bengal_floats + equatorial_floats
            
            return {
                "type": "comparison",
                "variable": "temperature",
                "floats": all_floats,
                "message": "Temperature comparison across different regions: Equatorial (warmest ~30.2°C), Arabian Sea (warm ~29.5°C), Bay of Bengal (moderate ~28.8°C).",
                "suggestions": ["Show salinity comparison", "Display T-S diagram", "Analyze thermocline depths"],
            }
        elif 'arabian' in lower_query:
            floats = generate_realistic_float_data("arabian sea", 4)
            return {
                "type": "profile",
                "variable": "temperature",
                "floats": floats,
                "message": "Arabian Sea temperature profiles showing warm surface waters (~29.5°C) and strong thermocline development due to high solar radiation and limited mixing.",
                "suggestions": ["Compare with Bay of Bengal", "Show salinity profiles", "Display thermocline analysis"],
            }
        elif 'bengal' in lower_query or 'bay of bengal' in lower_query:
            floats = generate_realistic_float_data("bay of bengal", 4)
            return {
                "type": "profile",
                "variable": "temperature",
                "floats": floats,
                "message": "Bay of Bengal temperature profiles showing moderate surface temperatures (~28.8°C) with freshwater influence affecting the thermal structure.",
                "suggestions": ["Compare with Arabian Sea", "Show salinity profiles", "Display seasonal variations"],
            }
        elif 'equator' in lower_query or 'equatorial' in lower_query:
            floats = generate_realistic_float_data("equatorial", 4)
            return {
                "type": "profile",
                "variable": "temperature",
                "floats": floats,
                "message": "Equatorial temperature profiles showing the warmest surface waters (~30.2°C) with strong vertical temperature gradients and pronounced thermocline.",
                "suggestions": ["Compare with other regions", "Show salinity profiles", "Display T-S diagram"],
            }
        elif 'southern' in lower_query:
            floats = generate_realistic_float_data("southern ocean", 4)
            return {
                "type": "profile",
                "variable": "temperature",
                "floats": floats,
                "message": "Southern Ocean temperature profiles showing cold surface waters (~2.5°C) with deep mixed layers and minimal seasonal variation.",
                "suggestions": ["Compare with tropical regions", "Show salinity profiles", "Display seasonal variations"],
            }
        else:
            # Default temperature query - show comparison
            arabian_floats = generate_realistic_float_data("arabian sea", 2)
            bengal_floats = generate_realistic_float_data("bay of bengal", 2)
            equatorial_floats = generate_realistic_float_data("equatorial", 2)
            all_floats = arabian_floats + bengal_floats + equatorial_floats
            
            return {
                "type": "comparison",
                "variable": "temperature",
                "floats": all_floats,
                "message": "Temperature profiles from ARGO floats across different regions showing regional variations: Equatorial (warmest), Arabian Sea (warm), Bay of Bengal (moderate).",
                "suggestions": ["Show specific region analysis", "Display salinity comparison", "Analyze thermocline depths"],
            }
    
    # Location queries
    if any(word in lower_query for word in ['location', 'map', 'where']):
        if 'arabian' in lower_query:
            floats = generate_realistic_float_data("arabian sea", 4)
            return {
                "type": "map",
                "floats": floats,
                "message": "ARGO float locations in the Arabian Sea region, showing active monitoring network covering the northwestern Indian Ocean.",
                "suggestions": ["Show float trajectories", "Display temperature at locations", "Compare with other regions"],
            }
        elif 'bengal' in lower_query or 'bay of bengal' in lower_query:
            floats = generate_realistic_float_data("bay of bengal", 4)
            return {
                "type": "map",
                "floats": floats,
                "message": "ARGO float locations in the Bay of Bengal region, showing active monitoring network covering the northeastern Indian Ocean.",
                "suggestions": ["Show float trajectories", "Display salinity at locations", "Compare with Arabian Sea"],
            }
        elif 'equator' in lower_query or 'equatorial' in lower_query:
            floats = generate_realistic_float_data("equatorial", 4)
            return {
                "type": "map",
                "floats": floats,
                "message": "ARGO float locations near the equator, showing active monitoring network covering the tropical Indian Ocean.",
                "suggestions": ["Show float trajectories", "Display temperature at locations", "Compare with subtropical regions"],
            }
        else:
            # Show all regions
            arabian_floats = generate_realistic_float_data("arabian sea", 2)
            bengal_floats = generate_realistic_float_data("bay of bengal", 2)
            equatorial_floats = generate_realistic_float_data("equatorial", 2)
            southern_floats = generate_realistic_float_data("southern ocean", 2)
            all_floats = arabian_floats + bengal_floats + equatorial_floats + southern_floats
            
            return {
                "type": "map",
                "floats": all_floats,
                "message": "ARGO float locations across the Indian Ocean region, showing active monitoring network covering Arabian Sea, Bay of Bengal, Equatorial, and Southern Ocean regions.",
                "suggestions": ["Show float trajectories", "Display temperature at locations", "Focus on specific regions"],
            }
    
    # Trajectory queries
    if any(word in lower_query for word in ['trajectory', 'path', 'movement', 'drift']):
        arabian_floats = generate_realistic_float_data("arabian sea", 2)
        bengal_floats = generate_realistic_float_data("bay of bengal", 2)
        equatorial_floats = generate_realistic_float_data("equatorial", 2)
        all_floats = arabian_floats + bengal_floats + equatorial_floats
        
        return {
            "type": "map",
            "floats": all_floats,
            "showTrajectories": True,
            "message": "Float trajectories showing drift patterns influenced by ocean currents across different regions. Notice how currents affect float movement differently in each region.",
            "suggestions": ["Analyze current patterns", "Show temperature along trajectories", "Compare drift speeds"],
        }
    
    # Default response
    floats = generate_realistic_float_data("arabian sea", 2)
    return {
        "type": "profile",
        "variable": "temperature",
        "floats": floats,
        "message": "Here's oceanographic data from our ARGO float network. These autonomous instruments provide crucial data for understanding ocean dynamics and climate.",
        "suggestions": [
            "Show me comprehensive oceanographic analysis",
            "Compare temperature profiles by region",
            "Display thermocline and water mass analysis",
            "Show float trajectories and current patterns",
        ],
    }

def create_profile_chart(floats: List[Dict], variable: str, title: str = None):
    """Create temperature/salinity profile chart with error handling"""
    try:
        if not floats:
            st.warning("No float data available for visualization")
            return None
            
        fig = go.Figure()
        colors = ["#14B8A6", "#38BDF8", "#8B5CF6", "#F59E0B", "#EF4444", "#10B981", "#F97316"]
        
        for i, float_data in enumerate(floats):
            try:
                if not float_data.get("profiles") or len(float_data["profiles"]) == 0:
                    st.warning(f"No profile data for {float_data.get('name', 'Unknown float')}")
                    continue
                    
                profile = float_data["profiles"][0]
                
                if variable not in profile:
                    st.warning(f"Variable '{variable}' not found in profile data")
                    continue
                    
                depth_data = profile.get("depth", [])
                var_data = profile.get(variable, [])
                
                if not depth_data or not var_data:
                    st.warning(f"Incomplete data for {float_data.get('name', 'Unknown float')}")
                    continue
                
                # Ensure data lengths match
                min_len = min(len(depth_data), len(var_data))
                if min_len == 0:
                    st.warning(f"No valid data points for {float_data.get('name', 'Unknown float')}")
                    continue
                    
                y_values = [-d for d in depth_data[:min_len]]  # Negative for oceanographic convention
                x_values = var_data[:min_len]
                
                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=y_values,
                    mode='lines+markers',
                    name=float_data.get("name", f"Float {i+1}"),
                    line=dict(color=colors[i % len(colors)], width=2.5),
                    marker=dict(size=5, opacity=0.8),
                    hovertemplate=f"<b>{float_data.get('name', f'Float {i+1}')}</b><br>" +
                                 f"Depth: %{{y}}m<br>" +
                                 f"{variable.title()}: %{{x}}{'°C' if variable == 'temperature' else ' PSU'}<br>" +
                                 "<extra></extra>"
                ))
            except Exception as e:
                st.error(f"Error processing float {i+1}: {e}")
                continue
        
        if not fig.data:
            # Return empty figure instead of None
            fig = go.Figure()
            fig.update_layout(
                title="No Data Available",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor="#1E293B",
                paper_bgcolor="#1E293B",
                annotations=[dict(
                    text="No valid data to display",
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=16, color="#FFFFFF")
                )]
            )
            return fig
            
        fig.update_layout(
            title=dict(
                text=title or f"{variable.title()} Profiles",
                font=dict(size=20, color="#FFFFFF", family="Inter"),
                x=0.5,
                xanchor="center"
            ),
            xaxis=dict(
                title=f"{variable.title()} ({'°C' if variable == 'temperature' else 'PSU'})",
                titlefont=dict(size=14, color="#E2E8F0", family="Inter"),
                tickfont=dict(size=12, color="#94A3B8", family="Inter"),
                gridcolor="rgba(255,255,255,0.1)",
                gridwidth=1,
                zeroline=False,
                showline=True,
                linecolor="rgba(255,255,255,0.2)",
                linewidth=1,
                color="#FFFFFF"
            ),
            yaxis=dict(
                title="Depth (m)",
                titlefont=dict(size=14, color="#E2E8F0", family="Inter"),
                tickfont=dict(size=12, color="#94A3B8", family="Inter"),
                gridcolor="rgba(255,255,255,0.1)",
                gridwidth=1,
                zeroline=False,
                showline=True,
                linecolor="rgba(255,255,255,0.2)",
                linewidth=1,
                autorange="reversed",
                color="#FFFFFF"
            ),
            plot_bgcolor="#1E293B",
            paper_bgcolor="#1E293B",
            font=dict(color="#FFFFFF", size=12, family="Inter"),
            margin=dict(l=80, r=40, t=80, b=80),
            showlegend=True,
            legend=dict(
                x=1.02,
                y=1,
                bgcolor="rgba(30, 41, 59, 0.9)",
                bordercolor="rgba(255,255,255,0.1)",
                borderwidth=1,
                font=dict(size=12, family="Inter", color="#FFFFFF")
            ),
            hovermode='closest'
        )
        
        return fig
        
    except Exception as e:
        # Return error figure instead of None
        fig = go.Figure()
        fig.update_layout(
            title="Error Creating Chart",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="#1E293B",
            paper_bgcolor="#1E293B",
            annotations=[dict(
                text=f"Error creating profile chart: {str(e)}",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=16, color="#FFFFFF")
            )]
        )
        return fig

def create_float_map(floats: List[Dict], show_trajectories: bool = False, title: str = "ARGO Float Locations"):
    """Create interactive map of ARGO floats with error handling"""
    try:
        if not floats:
            st.warning("No float data available for map visualization")
            return None
        
        # Validate and filter floats with valid coordinates
        valid_floats = []
        for f in floats:
            try:
                lat = float(f.get("lat", 0))
                lon = float(f.get("lon", 0))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    valid_floats.append(f)
                else:
                    st.warning(f"Invalid coordinates for {f.get('name', 'Unknown float')}: lat={lat}, lon={lon}")
            except (ValueError, TypeError) as e:
                st.warning(f"Error processing coordinates for {f.get('name', 'Unknown float')}: {e}")
                continue
        
        if not valid_floats:
            st.error("No valid float coordinates found")
            return None
        
        # Calculate map center and bounds
        lats = [float(f["lat"]) for f in valid_floats]
        lons = [float(f["lon"]) for f in valid_floats]
        
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        colors = ["#14B8A6", "#38BDF8", "#8B5CF6", "#F59E0B", "#EF4444", "#10B981", "#F97316"]
        
        for i, float_data in enumerate(valid_floats):
            try:
                color = colors[i % len(colors)]
                lat = float(float_data["lat"])
                lon = float(float_data["lon"])
                
                # Get profile data safely
                profiles = float_data.get("profiles", [])
                latest_temp = "N/A"
                latest_salinity = "N/A"
                
                if profiles and len(profiles) > 0:
                    profile = profiles[0]
                    temp_data = profile.get("temperature", [])
                    sal_data = profile.get("salinity", [])
                    if temp_data:
                        latest_temp = f"{temp_data[0]:.1f}"
                    if sal_data:
                        latest_salinity = f"{sal_data[0]:.1f}"
                
                # Format last update date
                last_update = float_data.get("lastUpdate", "")
                try:
                    if last_update:
                        formatted_date = datetime.fromisoformat(last_update.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                    else:
                        formatted_date = "Unknown"
                except:
                    formatted_date = "Unknown"
                
                # Add current position marker
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=10,
                    popup=folium.Popup(
                        f"""
                        <div style="font-family: Arial, sans-serif; min-width: 200px;">
                            <h4 style="margin: 0 0 8px 0; color: #1f2937; font-size: 16px;">{float_data.get('name', f'Float {i+1}')}</h4>
                            <p style="margin: 0 0 5px 0; color: #6b7280; font-size: 12px;">ID: {float_data.get('id', 'Unknown')}</p>
                            <div style="font-size: 13px; color: #374151; line-height: 1.4;">
                                <div style="margin-bottom: 3px;">
                                    <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: {'#10b981' if float_data.get('status') == 'active' else '#ef4444'}; margin-right: 5px;"></span>
                                    Status: <strong>{float_data.get('status', 'Unknown').title()}</strong>
                                </div>
                                <div style="margin-bottom: 3px;">Last Update: {formatted_date}</div>
                                <div style="margin-bottom: 3px;">Latest Temp: <strong>{latest_temp}°C</strong></div>
                                <div style="margin-bottom: 3px;">Latest Salinity: <strong>{latest_salinity} PSU</strong></div>
                                <div>Location: {lat:.3f}°N, {lon:.3f}°E</div>
                            </div>
                        </div>
                        """,
                        max_width=250
                    ),
                    color="white",
                    weight=3,
                    fillColor=color,
                    fillOpacity=0.8
                ).add_to(m)
                
                # Add trajectory if requested
                if show_trajectories:
                    trajectory = float_data.get("trajectory", [])
                    if len(trajectory) > 1:
                        try:
                            trajectory_points = []
                            for point in trajectory:
                                traj_lat = float(point.get("lat", 0))
                                traj_lon = float(point.get("lon", 0))
                                if -90 <= traj_lat <= 90 and -180 <= traj_lon <= 180:
                                    trajectory_points.append([traj_lat, traj_lon])
                            
                            if len(trajectory_points) > 1:
                                folium.PolyLine(
                                    trajectory_points,
                                    color=color,
                                    weight=3,
                                    opacity=0.7,
                                    dashArray="8, 8"
                                ).add_to(m)
                        except Exception as e:
                            st.warning(f"Error adding trajectory for {float_data.get('name', f'Float {i+1}')}: {e}")
                            
            except Exception as e:
                st.error(f"Error processing float {i+1}: {e}")
                continue
        
        # Add scale control
        folium.plugins.MeasureControl().add_to(m)
        
        return m
        
    except Exception as e:
        st.error(f"Error creating map: {e}")
        return None

def create_temperature_salinity_diagram(floats: List[Dict], title: str = "Temperature-Salinity Diagram"):
    """Create T-S diagram showing water mass characteristics"""
    try:
        if not floats:
            # Return empty figure instead of None
            fig = go.Figure()
            fig.update_layout(
                title="No Data Available",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor="#1E293B",
                paper_bgcolor="#1E293B",
                annotations=[dict(
                    text="No float data available for T-S diagram",
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=16, color="#FFFFFF")
                )]
            )
            return fig
            
        fig = go.Figure()
        colors = ["#14B8A6", "#38BDF8", "#8B5CF6", "#F59E0B", "#EF4444", "#10B981", "#F97316"]
        
        for i, float_data in enumerate(floats):
            try:
                if not float_data.get("profiles") or len(float_data["profiles"]) == 0:
                    continue
                    
                profile = float_data["profiles"][0]
                temp_data = profile.get("temperature", [])
                sal_data = profile.get("salinity", [])
                
                if not temp_data or not sal_data:
                    continue
                
                # Ensure data lengths match
                min_len = min(len(temp_data), len(sal_data))
                if min_len == 0:
                    continue
                
                fig.add_trace(go.Scatter(
                    x=sal_data[:min_len],
                    y=temp_data[:min_len],
                    mode='lines+markers',
                    name=float_data.get("name", f"Float {i+1}"),
                    line=dict(color=colors[i % len(colors)], width=2.5),
                    marker=dict(size=5, opacity=0.8),
                    hovertemplate=f"<b>{float_data.get('name', f'Float {i+1}')}</b><br>" +
                                 f"Salinity: %{{x}} PSU<br>" +
                                 f"Temperature: %{{y}}°C<br>" +
                                 "<extra></extra>"
                ))
            except Exception as e:
                st.error(f"Error processing float {i+1} for T-S diagram: {e}")
                continue
        
        if not fig.data:
            # Return empty figure instead of None
            fig = go.Figure()
            fig.update_layout(
                title="No Data Available",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor="#1E293B",
                paper_bgcolor="#1E293B",
                annotations=[dict(
                    text="No valid data to display in T-S diagram",
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=16, color="#FFFFFF")
                )]
            )
            return fig
            
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=20, color="#FFFFFF", family="Inter"),
                x=0.5,
                xanchor="center"
            ),
            xaxis=dict(
                title="Salinity (PSU)",
                titlefont=dict(size=14, color="#E2E8F0", family="Inter"),
                tickfont=dict(size=12, color="#94A3B8", family="Inter"),
                gridcolor="rgba(255,255,255,0.1)",
                gridwidth=1,
                zeroline=False,
                showline=True,
                linecolor="rgba(255,255,255,0.2)",
                linewidth=1,
                color="#FFFFFF"
            ),
            yaxis=dict(
                title="Temperature (°C)",
                titlefont=dict(size=14, color="#E2E8F0", family="Inter"),
                tickfont=dict(size=12, color="#94A3B8", family="Inter"),
                gridcolor="rgba(255,255,255,0.1)",
                gridwidth=1,
                zeroline=False,
                showline=True,
                linecolor="rgba(255,255,255,0.2)",
                linewidth=1,
                color="#FFFFFF"
            ),
            plot_bgcolor="#1E293B",
            paper_bgcolor="#1E293B",
            font=dict(color="#FFFFFF", size=12, family="Inter"),
            margin=dict(l=80, r=40, t=80, b=80),
            showlegend=True,
            legend=dict(
                x=1.02,
                y=1,
                bgcolor="rgba(30, 41, 59, 0.9)",
                bordercolor="rgba(255,255,255,0.1)",
                borderwidth=1,
                font=dict(size=12, family="Inter", color="#FFFFFF")
            ),
            hovermode='closest'
        )
        
        return fig
        
    except Exception as e:
        # Return error figure instead of None
        fig = go.Figure()
        fig.update_layout(
            title="Error Creating Chart",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="#1E293B",
            paper_bgcolor="#1E293B",
            annotations=[dict(
                text=f"Error creating T-S diagram: {str(e)}",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=16, color="#FFFFFF")
            )]
        )
        return fig

def create_anomaly_chart(data: List[Dict]):
    """Create anomaly detection chart with error handling"""
    try:
        if not data:
            # Return simple empty figure
            fig = go.Figure()
            fig.update_layout(
                title="No Data Available",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor="#1E293B",
                paper_bgcolor="#1E293B",
                annotations=[dict(
                    text="No data available for anomaly chart",
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=16, color="#FFFFFF")
                )]
            )
            return fig
            
        df = pd.DataFrame(data)
        
        if 'year' not in df.columns or 'temp' not in df.columns:
            # Return simple empty figure
            fig = go.Figure()
            fig.update_layout(
                title="Invalid Data Format",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor="#1E293B",
                paper_bgcolor="#1E293B",
                annotations=[dict(
                    text="Required columns 'year' and 'temp' not found in data",
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=16, color="#FFFFFF")
                )]
            )
            return fig
        
        fig = go.Figure()
        
        # Add main temperature line
        fig.add_trace(go.Scatter(
            x=df['year'],
            y=df['temp'],
            mode='lines+markers',
            name='Temperature',
            line=dict(color='#14B8A6', width=2.5),
            marker=dict(size=6, color='#14B8A6', opacity=0.8),
            hovertemplate="<b>Year:</b> %{x}<br><b>Temperature:</b> %{y}°C<extra></extra>"
        ))
        
        # Add anomaly markers if anomaly column exists
        if 'anomaly' in df.columns:
            anomalies = df[df['anomaly'] == True]
            if not anomalies.empty:
                fig.add_trace(go.Scatter(
                    x=anomalies['year'],
                    y=anomalies['temp'],
                    mode='markers',
                    name='Anomaly',
                    marker=dict(color='#EF4444', size=10, symbol='diamond', opacity=0.9),
                    hovertemplate="<b>🚨 Anomaly Detected</b><br>Year: %{x}<br>Temperature: %{y}°C<extra></extra>"
                ))
        
        # Add trend line
        try:
            z = np.polyfit(df['year'], df['temp'], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=df['year'],
                y=p(df['year']),
                mode='lines',
                name='Trend',
                line=dict(color='#10B981', width=2, dash='dash'),
                hovertemplate="<b>Trend:</b> %{y:.2f}°C<extra></extra>"
            ))
        except:
            pass  # Skip trend line if data is insufficient
        
        fig.update_layout(
            title="Temperature Anomaly Detection",
            xaxis_title="Year",
            yaxis_title="Temperature (°C)",
            plot_bgcolor="#1E293B",
            paper_bgcolor="#1E293B",
            font=dict(color="#FFFFFF", size=12),
            margin=dict(l=80, r=40, t=80, b=80),
            legend=dict(
                x=1.02,
                y=1,
                bgcolor="rgba(30, 41, 59, 0.9)",
                bordercolor="rgba(255,255,255,0.1)",
                borderwidth=1,
                font=dict(color="#FFFFFF")
            ),
            hovermode='closest',
            xaxis=dict(
                color="#FFFFFF",
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.2)"
            ),
            yaxis=dict(
                color="#FFFFFF",
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.2)"
            )
        )
        
        return fig
        
    except Exception as e:
        # Return simple error figure
        fig = go.Figure()
        fig.update_layout(
            title="Error Creating Chart",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="#1E293B",
            paper_bgcolor="#1E293B",
            annotations=[dict(
                text=f"Error creating anomaly chart: {str(e)}",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=16, color="#FFFFFF")
            )]
        )
        return fig

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Ocean Data Assistant</h1>
        <p>Professional oceanographic data analysis and visualization platform powered by ARGO float network</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        # Mobile menu toggle (hidden on desktop)
        st.markdown("""
        <div class="mobile-menu-toggle" style="display: none;">
            <button onclick="toggleSidebar()" style="
                background: #14B8A6;
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                margin-bottom: 1rem;
            ">☰ Menu</button>
        </div>
        """, unsafe_allow_html=True)
        
        st.header("Ocean Data Assistant")
        
        # AI Status
        ai_status = st.session_state.ai_status
        if ai_status["aiEnhanced"]:
            st.success(f"🤖 Enhanced AI ({ai_status['provider']})")
        else:
            st.info(f"🤖 Demo Mode ({ai_status['provider']})")
        
        st.markdown("---")
        
        # Sample Queries
        st.subheader("💡 Try These Queries")
        for query in SAMPLE_QUERIES[:6]:
            if st.button(query, key=f"sample_{query}", use_container_width=True):
                process_query(query)
        
        st.markdown("---")
        
        # File Upload
        st.subheader("📁 Upload NetCDF File")
        uploaded_file = st.file_uploader(
            "Choose a .nc file",
            type=['nc'],
            help="Upload NetCDF files for analysis"
        )
        
        if uploaded_file is not None:
            st.session_state.netcdf_summary = {
                "filename": uploaded_file.name,
                "size": uploaded_file.size
            }
            st.success(f"✅ Loaded: {uploaded_file.name}")
        
        # Quick Actions
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📍 Float Map", use_container_width=True):
                process_query("Show me all float locations")
        with col2:
            if st.button("🌡️ Temperature", use_container_width=True):
                process_query("Compare temperature profiles")
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("🧂 Salinity", use_container_width=True):
                process_query("Show salinity data")
        with col4:
            if st.button("📊 Analysis", use_container_width=True):
                process_query("Show comprehensive oceanographic analysis")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat Interface
        st.subheader("💬 Chat Interface")
        
        # Display messages
        for message in st.session_state.messages:
            with st.container():
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong> {message["content"]}
                        <div style="font-size: 0.8em; opacity: 0.7; margin-top: 0.5rem;">
                            {message["timestamp"].strftime("%H:%M:%S")}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>🤖 Assistant:</strong> {message["content"]}
                        <div style="font-size: 0.8em; opacity: 0.7; margin-top: 0.5rem;">
                            {message["timestamp"].strftime("%H:%M:%S")}
                            {f' • {message.get("aiEnhanced", False) and "AI Enhanced" or ""}'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show suggestions if available
                    if message.get("suggestions"):
                        st.markdown("**💡 You might also ask:**")
                        cols = st.columns(min(len(message["suggestions"]), 3))
                        for i, suggestion in enumerate(message["suggestions"]):
                            with cols[i % 3]:
                                if st.button(suggestion, key=f"suggestion_{i}_{message['timestamp']}", use_container_width=True):
                                    process_query(suggestion)
        
        # Chat input
        user_input = st.text_input(
            "Ask about ocean data...",
            placeholder="e.g., 'Show salinity near equator' or 'Compare Arabian Sea temperatures'",
            key="chat_input"
        )
        
        col_send, col_clear = st.columns([1, 1])
        with col_send:
            if st.button("Send", type="primary", use_container_width=True):
                if user_input:
                    process_query(user_input)
                    st.rerun()
        
        with col_clear:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
    
    with col2:
        # Visualization Panel
        st.subheader("📊 Visualizations")
        
        if st.session_state.current_visualization:
            viz_data = st.session_state.current_visualization
            
            # Show data summary
            if viz_data.get("floats"):
                st.metric("Floats", len(viz_data["floats"]))
                if viz_data.get("variable"):
                    st.metric("Variable", viz_data["variable"].title())
                if viz_data.get("type"):
                    st.metric("Type", viz_data["type"].title())
            
            # Render visualizations based on type
            try:
                if viz_data["type"] == "profile" and viz_data.get("floats"):
                    chart = create_profile_chart(
                        viz_data["floats"],
                        viz_data.get("variable", "temperature"),
                        f"{viz_data.get('variable', 'temperature').title()} Profiles"
                    )
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                    else:
                        st.warning("Unable to create profile chart with the available data")
                
                elif viz_data["type"] == "comparison" and viz_data.get("floats"):
                    # Show comparison charts with tabs
                    variable = viz_data.get("variable", "temperature")
                    tab1, tab2, tab3 = st.tabs([f"📊 {variable.title()} Comparison", "🗺️ Map View", "📈 T-S Diagram"])
                    
                    with tab1:
                        chart = create_profile_chart(
                            viz_data["floats"],
                            variable,
                            f"{variable.title()} Comparison Across Regions"
                        )
                        if chart:
                            st.plotly_chart(chart, use_container_width=True)
                        else:
                            st.warning("Unable to create comparison chart")
                    
                    with tab2:
                        map_obj = create_float_map(
                            viz_data["floats"],
                            False,
                            f"{variable.title()} Comparison - Float Locations"
                        )
                        if map_obj:
                            st_folium(map_obj, width=400, height=300)
                        else:
                            st.warning("Unable to create map")
                    
                    with tab3:
                        ts_chart = create_temperature_salinity_diagram(viz_data["floats"])
                        if ts_chart:
                            st.plotly_chart(ts_chart, use_container_width=True)
                        else:
                            st.warning("Unable to create T-S diagram")
                
                elif viz_data["type"] == "map" and viz_data.get("floats"):
                    map_obj = create_float_map(
                        viz_data["floats"],
                        viz_data.get("showTrajectories", False),
                        "ARGO Float Locations"
                    )
                    if map_obj:
                        st_folium(map_obj, width=400, height=300)
                    else:
                        st.warning("Unable to create map with the available data")
                
                elif viz_data["type"] == "ts_diagram" and viz_data.get("floats"):
                    ts_chart = create_temperature_salinity_diagram(viz_data["floats"])
                    if ts_chart:
                        st.plotly_chart(ts_chart, use_container_width=True)
                    else:
                        st.warning("Unable to create T-S diagram")
                
                elif viz_data["type"] == "analysis" and viz_data.get("floats"):
                    # Show multiple visualizations for analysis
                    tab1, tab2, tab3, tab4 = st.tabs(["🌡️ Temperature", "🧂 Salinity", "📊 T-S Diagram", "🗺️ Map"])
                    
                    with tab1:
                        temp_chart = create_profile_chart(viz_data["floats"], "temperature")
                        if temp_chart:
                            st.plotly_chart(temp_chart, use_container_width=True)
                        else:
                            st.warning("Unable to create temperature chart")
                    
                    with tab2:
                        sal_chart = create_profile_chart(viz_data["floats"], "salinity")
                        if sal_chart:
                            st.plotly_chart(sal_chart, use_container_width=True)
                        else:
                            st.warning("Unable to create salinity chart")
                    
                    with tab3:
                        ts_chart = create_temperature_salinity_diagram(viz_data["floats"])
                        if ts_chart:
                            st.plotly_chart(ts_chart, use_container_width=True)
                        else:
                            st.warning("Unable to create T-S diagram")
                    
                    with tab4:
                        map_obj = create_float_map(viz_data["floats"])
                        if map_obj:
                            st_folium(map_obj, width=400, height=300)
                        else:
                            st.warning("Unable to create map")
                
                else:
                    st.info("No visualization data available for this query type")
                    
            except Exception as e:
                st.error(f"Error rendering visualization: {e}")
                st.info("Please try a different query or check your data")
        
        else:
            st.info("Visualizations will appear here after you run a query.")
        
        # Anomaly Chart
        st.markdown("---")
        st.subheader("🚨 Anomaly Detection")
        st.plotly_chart(
            create_anomaly_chart(SAMPLE_DATA),
            use_container_width=True
        )
        
        # AI Insight
        st.markdown("---")
        st.subheader("🤖 AI Insight")
        st.info("Map pe click karo to insight dikhai dega." if not st.session_state.current_visualization else "Analysis complete. Check the visualizations above for insights.")

def process_query(query: str):
    """Process user query and add to chat"""
    # Add user message
    user_message = {
        "role": "user",
        "content": query,
        "timestamp": datetime.now()
    }
    st.session_state.messages.append(user_message)
    
    # Process query
    response = process_natural_language_query(query)
    
    # Add assistant message
    assistant_message = {
        "role": "assistant",
        "content": response["message"],
        "timestamp": datetime.now(),
        "suggestions": response.get("suggestions", []),
        "aiEnhanced": False
    }
    st.session_state.messages.append(assistant_message)
    
    # Update visualization
    st.session_state.current_visualization = response

if __name__ == "__main__":
    # Add JavaScript for mobile menu toggle
    st.markdown("""
    <script>
    function toggleSidebar() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const isExpanded = sidebar.getAttribute('aria-expanded') === 'true';
        sidebar.setAttribute('aria-expanded', !isExpanded);
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const toggle = document.querySelector('.mobile-menu-toggle');
        
        if (window.innerWidth <= 768 && 
            sidebar.getAttribute('aria-expanded') === 'true' &&
            !sidebar.contains(event.target) && 
            !toggle.contains(event.target)) {
            sidebar.setAttribute('aria-expanded', 'false');
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (window.innerWidth > 768) {
            sidebar.setAttribute('aria-expanded', 'true');
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    main()
