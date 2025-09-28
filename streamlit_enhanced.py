"""
Argo AI Ocean Assistant - Enhanced Streamlit Application
Integrates with the existing Python RAG pipeline for advanced AI capabilities.
"""

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
import tempfile
import xarray as xr
import netCDF4

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import backend modules
try:
    from backend.rag_pipeline import RagPipeline
    from backend.config import Config
    from backend.data_processing import process_netcdf_file
    from backend.social_impact import analyze_social_impact
    BACKEND_AVAILABLE = True
except ImportError as e:
    BACKEND_AVAILABLE = False
    st.warning(f"Backend modules not available: {e}. Running in demo mode.")

# Page configuration
st.set_page_config(
    page_title="Argo AI Ocean Assistant",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ocean theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0ea5e9, #06b6d4);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #0ea5e9;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
    }
    .chat-message {
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 15px;
        border-left: 5px solid #0ea5e9;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
    }
    .user-message {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        border-left-color: #3b82f6;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        border-left-color: #06b6d4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        border-radius: 8px 8px 0px 0px;
        gap: 2px;
        padding: 12px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0ea5e9, #06b6d4);
        color: white;
    }
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-active { background-color: #10b981; }
    .status-inactive { background-color: #ef4444; }
    .insight-box {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border: 1px solid #f59e0b;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .anomaly-alert {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        border: 1px solid #ef4444;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
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
if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = None
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

# Initialize RAG pipeline if backend is available
@st.cache_resource
def initialize_rag_pipeline():
    """Initialize the RAG pipeline with caching"""
    if BACKEND_AVAILABLE:
        try:
            config = Config()
            pipeline = RagPipeline(config)
            # Try to load existing index
            if pipeline._load_index():
                st.session_state.ai_status = {"aiEnhanced": True, "provider": "RAG Pipeline"}
                return pipeline
            else:
                st.info("Building FAISS index from data... This may take a moment.")
                pipeline.build_faiss()
                if pipeline._load_index():
                    st.session_state.ai_status = {"aiEnhanced": True, "provider": "RAG Pipeline"}
                    return pipeline
        except Exception as e:
            st.error(f"Failed to initialize RAG pipeline: {e}")
    return None

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
    "Show salinity data",
    "Arabian Sea analysis",
    "Show comprehensive oceanographic analysis",
    "Display thermocline depths and water masses",
    "Analyze water mass properties",
    "Show temperature-salinity diagrams",
    "Compare mixed layer depths by region"
]

def load_mock_data():
    """Load mock ARGO float data"""
    try:
        with open('data/mock-argo-data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Enhanced fallback mock data
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

def process_netcdf_upload(uploaded_file):
    """Process uploaded NetCDF file"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.nc') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Process with xarray
        ds = xr.open_dataset(tmp_file_path)
        
        # Extract basic information
        summary = {
            "filename": uploaded_file.name,
            "size": uploaded_file.size,
            "variables": list(ds.data_vars.keys()),
            "dimensions": dict(ds.dims),
            "coordinates": list(ds.coords.keys()),
            "attributes": dict(ds.attrs)
        }
        
        # Try to process with backend if available
        if BACKEND_AVAILABLE and st.session_state.rag_pipeline:
            try:
                processed_data = process_netcdf_file(tmp_file_path)
                summary["processed"] = True
                summary["profiles_count"] = len(processed_data) if processed_data else 0
            except Exception as e:
                st.warning(f"Backend processing failed: {e}")
                summary["processed"] = False
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        return summary
        
    except Exception as e:
        st.error(f"Failed to process NetCDF file: {e}")
        return None

def process_query_with_rag(query: str):
    """Process query using RAG pipeline if available"""
    if st.session_state.rag_pipeline:
        try:
            result = st.session_state.rag_pipeline.ask(query)
            return {
                "message": result["summary"],
                "type": "analysis",
                "floats": load_mock_data()["floats"],  # Use mock data for visualization
                "suggestions": [
                    "Show me temperature profiles by region",
                    "Compare salinity stratification between regions",
                    "Display float trajectories with temperature data",
                ],
                "aiEnhanced": True,
                "sql": result.get("sql", ""),
                "rows": result.get("rows", 0)
            }
        except Exception as e:
            st.error(f"RAG processing failed: {e}")
    
    # Fallback to mock processing
    return process_natural_language_query(query)

def process_natural_language_query(query: str) -> Dict[str, Any]:
    """Process natural language queries and return structured responses"""
    lower_query = query.lower()
    
    # Greeting handling
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
    
    # Advanced oceanographic analysis
    if any(word in lower_query for word in ['thermocline', 'water mass', 'analysis', 't-s diagram', 'mixed layer', 'density']):
        return {
            "type": "analysis",
            "floats": load_mock_data()["floats"],
            "message": "Here's a comprehensive oceanographic analysis including thermocline depths, water mass identification, and regional comparisons.",
            "suggestions": [
                "Show me temperature profiles by region",
                "Compare salinity stratification between regions",
                "Display float trajectories with temperature data",
            ],
        }
    
    # Salinity queries
    if 'salinity' in lower_query:
        if 'equator' in lower_query:
            return {
                "type": "profile",
                "variable": "salinity",
                "floats": [f for f in load_mock_data()["floats"] if abs(f["lat"]) < 5],
                "message": "Here are the salinity profiles near the equator from our ARGO floats. Notice the lower salinity values typical of equatorial regions.",
                "suggestions": [
                    "Compare with Arabian Sea salinity",
                    "Show temperature-salinity relationship",
                    "Display salinity at different depths",
                ],
            }
        return {
            "type": "comparison",
            "variable": "salinity",
            "floats": load_mock_data()["floats"],
            "message": "Comparing salinity profiles across all available ARGO floats.",
            "suggestions": [
                "Focus on specific regions",
                "Show salinity at specific depths",
                "Display temperature-salinity diagrams",
            ],
        }
    
    # Temperature queries
    if 'temperature' in lower_query:
        if 'arabian' in lower_query:
            return {
                "type": "profile",
                "variable": "temperature",
                "floats": [f for f in load_mock_data()["floats"] if 10 < f["lat"] < 25 and 60 < f["lon"] < 75],
                "message": "Temperature data from Arabian Sea floats showing warm surface waters and strong thermocline development.",
                "suggestions": ["Compare with Bay of Bengal", "Show thermocline depth analysis", "Display seasonal variations"],
            }
        return {
            "type": "profile",
            "variable": "temperature",
            "floats": load_mock_data()["floats"],
            "message": "Temperature profiles from ARGO floats showing vertical structure and regional variations.",
            "suggestions": ["Try different depths", "Show vertical profiles", "Compare with salinity at same depth"],
        }
    
    # Location queries
    if any(word in lower_query for word in ['location', 'map', 'where']):
        return {
            "type": "map",
            "floats": load_mock_data()["floats"],
            "message": "ARGO float locations across the Indian Ocean region, showing active monitoring network.",
            "suggestions": ["Show float trajectories", "Display temperature at locations", "Focus on specific regions"],
        }
    
    # Default response
    return {
        "type": "profile",
        "variable": "temperature",
        "floats": load_mock_data()["floats"][:3],
        "message": "Here's oceanographic data from our ARGO float network. These autonomous instruments provide crucial data for understanding ocean dynamics and climate.",
        "suggestions": [
            "Show me comprehensive oceanographic analysis",
            "Compare temperature profiles by region",
            "Display thermocline and water mass analysis",
            "Show float trajectories and current patterns",
        ],
    }

def create_profile_chart(floats: List[Dict], variable: str, title: str = None):
    """Create temperature/salinity profile chart"""
    fig = go.Figure()
    
    colors = ["#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#f97316"]
    
    for i, float_data in enumerate(floats):
        profile = float_data["profiles"][0]
        y_values = [-d for d in profile["depth"]]  # Negative for oceanographic convention
        x_values = profile[variable]
        
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name=float_data["name"],
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=6),
            hovertemplate=f"<b>{float_data['name']}</b><br>" +
                         f"Depth: %{{y}}m<br>" +
                         f"{variable.title()}: %{{x}}{'°C' if variable == 'temperature' else ' PSU'}<br>" +
                         "<extra></extra>"
        ))
    
    fig.update_layout(
        title=dict(
            text=title or f"{variable.title()} Profiles",
            font=dict(size=18, color="#1f2937")
        ),
        xaxis_title=f"{variable.title()} ({'°C' if variable == 'temperature' else 'PSU'})",
        yaxis_title="Depth (m)",
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#374151", size=12),
        margin=dict(l=80, r=40, t=60, b=80),
        showlegend=True,
        legend=dict(
            x=1.02,
            y=1,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
        hovermode='closest'
    )
    
    return fig

def create_float_map(floats: List[Dict], show_trajectories: bool = False, title: str = "ARGO Float Locations"):
    """Create interactive map of ARGO floats"""
    if not floats:
        return None
    
    # Calculate map center and bounds
    lats = [f["lat"] for f in floats]
    lons = [f["lon"] for f in floats]
    
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    colors = ["#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#f97316"]
    
    for i, float_data in enumerate(floats):
        color = colors[i % len(colors)]
        status_class = "status-active" if float_data["status"] == "active" else "status-inactive"
        
        # Add current position marker
        folium.CircleMarker(
            location=[float_data["lat"], float_data["lon"]],
            radius=10,
            popup=folium.Popup(
                f"""
                <div style="font-family: Arial, sans-serif; min-width: 200px;">
                    <h4 style="margin: 0 0 8px 0; color: #1f2937; font-size: 16px;">{float_data['name']}</h4>
                    <p style="margin: 0 0 5px 0; color: #6b7280; font-size: 12px;">ID: {float_data['id']}</p>
                    <div style="font-size: 13px; color: #374151; line-height: 1.4;">
                        <div style="margin-bottom: 3px;">
                            <span class="status-indicator {status_class}"></span>
                            Status: <strong>{float_data['status'].title()}</strong>
                        </div>
                        <div style="margin-bottom: 3px;">Last Update: {datetime.fromisoformat(float_data['lastUpdate'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')}</div>
                        <div style="margin-bottom: 3px;">Latest Temp: <strong>{float_data['profiles'][0]['temperature'][0]}°C</strong></div>
                        <div style="margin-bottom: 3px;">Latest Salinity: <strong>{float_data['profiles'][0]['salinity'][0]} PSU</strong></div>
                        <div>Location: {float_data['lat']:.3f}°N, {float_data['lon']:.3f}°E</div>
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
        if show_trajectories and len(float_data["trajectory"]) > 1:
            trajectory_points = [[point["lat"], point["lon"]] for point in float_data["trajectory"]]
            folium.PolyLine(
                trajectory_points,
                color=color,
                weight=3,
                opacity=0.7,
                dash_array="8, 8"
            ).add_to(m)
            
            # Add trajectory markers
            for j, point in enumerate(float_data["trajectory"][1:], 1):
                folium.CircleMarker(
                    location=[point["lat"], point["lon"]],
                    radius=6,
                    popup=folium.Popup(
                        f"""
                        <div style="font-family: Arial, sans-serif;">
                            <h5 style="margin: 0 0 3px 0; color: #1f2937; font-size: 14px;">{float_data['name']}</h5>
                            <p style="margin: 0; color: #6b7280; font-size: 11px;">Date: {datetime.fromisoformat(point['date'].replace('Z', '+00:00')).strftime('%Y-%m-%d')}</p>
                        </div>
                        """,
                        max_width=150
                    ),
                    color="white",
                    weight=2,
                    fillColor=color,
                    fillOpacity=0.6
                ).add_to(m)
    
    # Add scale control
    folium.plugins.MeasureControl().add_to(m)
    
    return m

def create_anomaly_chart(data: List[Dict]):
    """Create anomaly detection chart"""
    df = pd.DataFrame(data)
    
    fig = go.Figure()
    
    # Add main temperature line
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['temp'],
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8, color='#3b82f6'),
        hovertemplate="<b>Year:</b> %{x}<br><b>Temperature:</b> %{y}°C<extra></extra>"
    ))
    
    # Add anomaly markers
    anomalies = df[df.get('anomaly', False)]
    if not anomalies.empty:
        fig.add_trace(go.Scatter(
            x=anomalies['year'],
            y=anomalies['temp'],
            mode='markers',
            name='Anomaly',
            marker=dict(color='#ef4444', size=12, symbol='diamond'),
            hovertemplate="<b>🚨 Anomaly Detected</b><br>Year: %{x}<br>Temperature: %{y}°C<extra></extra>"
        ))
    
    # Add trend line
    z = np.polyfit(df['year'], df['temp'], 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=p(df['year']),
        mode='lines',
        name='Trend',
        line=dict(color='#10b981', width=2, dash='dash'),
        hovertemplate="<b>Trend:</b> %{y:.2f}°C<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text="Temperature Anomaly Detection",
            font=dict(size=18, color="#1f2937")
        ),
        xaxis_title="Year",
        yaxis_title="Temperature (°C)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#374151", size=12),
        margin=dict(l=80, r=40, t=60, b=80),
        legend=dict(
            x=1.02,
            y=1,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
        hovermode='closest'
    )
    
    return fig

def create_ts_diagram(floats: List[Dict]):
    """Create Temperature-Salinity diagram"""
    fig = go.Figure()
    
    colors = ["#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#f97316"]
    
    for i, float_data in enumerate(floats):
        profile = float_data["profiles"][0]
        temp = profile["temperature"]
        sal = profile["salinity"]
        
        fig.add_trace(go.Scatter(
            x=sal,
            y=temp,
            mode='lines+markers',
            name=float_data["name"],
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=6),
            hovertemplate=f"<b>{float_data['name']}</b><br>" +
                         f"Temperature: %{{y}}°C<br>" +
                         f"Salinity: %{{x}} PSU<br>" +
                         "<extra></extra>"
        ))
    
    fig.update_layout(
        title=dict(
            text="Temperature-Salinity Diagram",
            font=dict(size=18, color="#1f2937")
        ),
        xaxis_title="Salinity (PSU)",
        yaxis_title="Temperature (°C)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#374151", size=12),
        margin=dict(l=80, r=40, t=60, b=80),
        showlegend=True,
        legend=dict(
            x=1.02,
            y=1,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
        hovermode='closest'
    )
    
    return fig

def main():
    """Main Streamlit application"""
    
    # Initialize RAG pipeline
    if st.session_state.rag_pipeline is None:
        st.session_state.rag_pipeline = initialize_rag_pipeline()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; display: flex; align-items: center; gap: 15px;">
            🌊 Argo AI Ocean Assistant
        </h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">
            AI-powered oceanographic data analysis and visualization with advanced RAG capabilities
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🌊 Ocean Data Assistant")
        
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
            with st.spinner("Processing NetCDF file..."):
                summary = process_netcdf_upload(uploaded_file)
                if summary:
                    st.session_state.netcdf_summary = summary
                    st.success(f"✅ Loaded: {uploaded_file.name}")
                    st.json(summary)
        
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
        
        # Social Impact Analysis
        if st.session_state.current_visualization and st.session_state.current_visualization.get("floats"):
            st.markdown("---")
            st.subheader("🌍 Social Impact")
            if st.button("Analyze Impact", use_container_width=True):
                with st.spinner("Analyzing social impact..."):
                    try:
                        impact = analyze_social_impact(st.session_state.current_visualization["floats"])
                        st.session_state.social_impact = impact
                    except Exception as e:
                        st.error(f"Impact analysis failed: {e}")
    
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
                    
                    # Show SQL query if available
                    if message.get("sql"):
                        with st.expander("🔍 Generated SQL Query"):
                            st.code(message["sql"], language="sql")
                    
                    # Show suggestions if available
                    if message.get("suggestions"):
                        st.write("**You might also ask:**")
                        cols = st.columns(len(message["suggestions"]))
                        for i, suggestion in enumerate(message["suggestions"]):
                            with cols[i]:
                                if st.button(suggestion, key=f"suggestion_{i}_{message['timestamp']}"):
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
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Floats", len(viz_data["floats"]))
                with col2:
                    if viz_data.get("variable"):
                        st.metric("Variable", viz_data["variable"].title())
                with col3:
                    if viz_data.get("type"):
                        st.metric("Type", viz_data["type"].title())
            
            # Render visualizations based on type
            if viz_data["type"] == "profile" and viz_data.get("floats"):
                st.plotly_chart(
                    create_profile_chart(
                        viz_data["floats"],
                        viz_data.get("variable", "temperature"),
                        f"{viz_data.get('variable', 'temperature').title()} Profiles"
                    ),
                    use_container_width=True
                )
            
            elif viz_data["type"] == "map" and viz_data.get("floats"):
                map_obj = create_float_map(
                    viz_data["floats"],
                    viz_data.get("showTrajectories", False),
                    "ARGO Float Locations"
                )
                if map_obj:
                    st_folium(map_obj, width=400, height=300)
            
            elif viz_data["type"] == "analysis" and viz_data.get("floats"):
                # Show multiple visualizations for analysis
                tab1, tab2, tab3, tab4 = st.tabs(["Temperature", "Salinity", "T-S Diagram", "Map"])
                
                with tab1:
                    st.plotly_chart(
                        create_profile_chart(viz_data["floats"], "temperature"),
                        use_container_width=True
                    )
                
                with tab2:
                    st.plotly_chart(
                        create_profile_chart(viz_data["floats"], "salinity"),
                        use_container_width=True
                    )
                
                with tab3:
                    st.plotly_chart(
                        create_ts_diagram(viz_data["floats"]),
                        use_container_width=True
                    )
                
                with tab4:
                    map_obj = create_float_map(viz_data["floats"])
                    if map_obj:
                        st_folium(map_obj, width=400, height=300)
        
        else:
            st.info("Visualizations will appear here after you run a query.")
        
        # Anomaly Chart
        st.markdown("---")
        st.subheader("🚨 Anomaly Detection")
        st.plotly_chart(
            create_anomaly_chart(SAMPLE_DATA),
            use_container_width=True
        )
        
        # Social Impact Analysis
        if hasattr(st.session_state, 'social_impact') and st.session_state.social_impact:
            st.markdown("---")
            st.subheader("🌍 Social Impact Analysis")
            impact = st.session_state.social_impact
            
            if impact.get("anomalies"):
                st.markdown("""
                <div class="anomaly-alert">
                    <h4 style="margin: 0 0 0.5rem 0; color: #dc2626;">🚨 Anomalies Detected</h4>
                    <p style="margin: 0; color: #7f1d1d;">{}</p>
                </div>
                """.format(impact["anomalies"]), unsafe_allow_html=True)
            
            if impact.get("health_index"):
                st.metric("Ecosystem Health Index", f"{impact['health_index']}/100")
            
            if impact.get("educational_summary"):
                st.markdown("""
                <div class="insight-box">
                    <h4 style="margin: 0 0 0.5rem 0; color: #92400e;">📚 Educational Summary</h4>
                    <p style="margin: 0; color: #78350f;">{}</p>
                </div>
                """.format(impact["educational_summary"]), unsafe_allow_html=True)
        
        # AI Insight
        st.markdown("---")
        st.subheader("🤖 AI Insight")
        if not st.session_state.current_visualization:
            st.info("Map pe click karo to insight dikhai dega.")
        else:
            st.success("Analysis complete. Check the visualizations above for insights.")

def process_query(query: str):
    """Process user query and add to chat"""
    # Add user message
    user_message = {
        "role": "user",
        "content": query,
        "timestamp": datetime.now()
    }
    st.session_state.messages.append(user_message)
    
    # Process query with RAG if available
    response = process_query_with_rag(query)
    
    # Add assistant message
    assistant_message = {
        "role": "assistant",
        "content": response["message"],
        "timestamp": datetime.now(),
        "suggestions": response.get("suggestions", []),
        "aiEnhanced": response.get("aiEnhanced", False),
        "sql": response.get("sql", ""),
        "rows": response.get("rows", 0)
    }
    st.session_state.messages.append(assistant_message)
    
    # Update visualization
    st.session_state.current_visualization = response

if __name__ == "__main__":
    main()
