# Argo AI Ocean Assistant - Streamlit Version

A comprehensive oceanographic data visualization and analysis application built with Streamlit, featuring AI-powered natural language querying and advanced data processing capabilities.

## 🌊 Features

### Core Functionality
- **Interactive Chat Interface**: Natural language queries about oceanographic data
- **Real-time Visualizations**: Temperature/salinity profiles, interactive maps, T-S diagrams
- **ARGO Float Data**: Integration with ARGO float network data
- **Anomaly Detection**: Automated detection of temperature anomalies
- **NetCDF File Upload**: Support for uploading and analyzing NetCDF files

### AI-Powered Features
- **RAG Pipeline Integration**: Advanced retrieval-augmented generation for intelligent responses
- **Natural Language Processing**: Convert plain English queries to data analysis
- **Semantic Search**: Find relevant oceanographic data using AI embeddings
- **Social Impact Analysis**: Educational summaries and ecosystem health metrics

### Visualizations
- **Profile Charts**: Temperature and salinity depth profiles
- **Interactive Maps**: ARGO float locations with trajectories
- **T-S Diagrams**: Temperature-salinity relationships
- **Anomaly Charts**: Time series with anomaly detection
- **Comparison Views**: Multi-float comparisons and regional analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip or conda package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd streamlit-backup
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements_streamlit.txt
   ```

3. **Run the basic version**:
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Run the enhanced version** (with RAG pipeline):
   ```bash
   streamlit run streamlit_enhanced.py
   ```

### Environment Variables (Optional)

For enhanced AI capabilities, set these environment variables:

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export ARGOVIS_API_KEY="your-argovis-api-key"
export HUGGINGFACEHUB_API_TOKEN="your-hf-token"
```

## 📁 Project Structure

```
streamlit-backup/
├── streamlit_app.py              # Basic Streamlit application
├── streamlit_enhanced.py         # Enhanced version with RAG pipeline
├── requirements_streamlit.txt    # Python dependencies
├── README_STREAMLIT.md          # This file
├── backend/                      # Backend modules
│   ├── rag_pipeline.py          # RAG pipeline implementation
│   ├── config.py                # Configuration management
│   ├── data_processing.py       # NetCDF data processing
│   └── social_impact.py         # Social impact analysis
├── data/                        # Sample data
│   └── mock-argo-data.json     # Mock ARGO float data
└── components/                  # Original React components (reference)
```

## 🎯 Usage

### Basic Queries
- "Show me all float locations"
- "Compare temperature profiles"
- "Show salinity data"
- "Arabian Sea analysis"

### Advanced Queries
- "Show comprehensive oceanographic analysis"
- "Display thermocline depths and water masses"
- "Analyze water mass properties"
- "Show temperature-salinity diagrams"
- "Compare mixed layer depths by region"

### File Upload
1. Click "Upload NetCDF File" in the sidebar
2. Select a .nc file
3. The application will process and analyze the data
4. Use the processed data in your queries

## 🔧 Configuration

### Backend Configuration
The enhanced version uses the existing backend modules. Configure them in `backend/config.py`:

```python
class Config:
    duckdb_path = "data/argo.duckdb"
    data_dir = "data"
    faiss_index_path = "data/faiss_index.bin"
    faiss_meta_path = "data/faiss_meta.jsonl"
    mistral_model_id = "mistralai/Mistral-7B-Instruct-v0.2"
```

### Customization
- Modify `SAMPLE_QUERIES` in the Python files to add custom sample queries
- Update `load_mock_data()` to use your own data sources
- Customize the CSS styling in the `st.markdown()` sections

## 📊 Data Sources

### ARGO Float Data
- Real-time data from ARGO float network
- Temperature, salinity, and pressure profiles
- Float trajectories and status information

### Mock Data
- Sample data for demonstration purposes
- Located in `data/mock-argo-data.json`
- Includes multiple floats with realistic profiles

### NetCDF Files
- Support for standard NetCDF oceanographic files
- Automatic processing and visualization
- Integration with existing data analysis workflows

## 🤖 AI Integration

### RAG Pipeline
The enhanced version includes a full RAG (Retrieval-Augmented Generation) pipeline:

1. **Data Ingestion**: NetCDF files → DuckDB database
2. **Embeddings**: Sentence transformers for semantic search
3. **Vector Search**: FAISS index for fast similarity search
4. **NL2SQL**: Natural language to SQL conversion
5. **Summarization**: AI-powered result summarization

### Supported AI Models
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **LLM**: Mistral-7B-Instruct-v0.2 (via HuggingFace)
- **Fallback**: Heuristic-based processing when AI models unavailable

## 🌍 Social Impact Features

### Educational Summaries
- Kid-friendly explanations of oceanographic phenomena
- Scientific insights in accessible language
- Regional context and environmental significance

### Ecosystem Health Monitoring
- Health index calculation (0-100 scale)
- Anomaly detection and alerting
- Environmental impact assessment

### Anomaly Detection
- Temperature anomaly identification
- Statistical analysis of oceanographic trends
- Visual indicators for significant changes

## 🛠️ Development

### Adding New Visualizations
1. Create a new function following the pattern of `create_profile_chart()`
2. Add the visualization to the appropriate visualization type handler
3. Update the UI to include the new visualization option

### Extending Query Processing
1. Add new patterns to `process_natural_language_query()`
2. Create corresponding response structures
3. Update the visualization rendering logic

### Custom Data Sources
1. Modify `load_mock_data()` to connect to your data source
2. Update the data transformation logic
3. Ensure compatibility with existing visualization functions

## 🐛 Troubleshooting

### Common Issues

1. **Backend modules not found**:
   - Ensure the `backend/` directory is in the same location as the Streamlit files
   - Check that all backend dependencies are installed

2. **NetCDF file processing fails**:
   - Verify the file is a valid NetCDF file
   - Check that xarray and netCDF4 are properly installed

3. **RAG pipeline initialization fails**:
   - Check that all required dependencies are installed
   - Verify database and index file permissions
   - Check the logs for specific error messages

4. **Visualization not displaying**:
   - Ensure Plotly and Folium are properly installed
   - Check that data is in the expected format
   - Verify that the visualization functions are receiving valid data

### Performance Optimization

1. **Large datasets**:
   - Use data sampling for initial visualization
   - Implement pagination for large result sets
   - Cache frequently accessed data

2. **RAG pipeline**:
   - Pre-build FAISS index for faster queries
   - Use smaller embedding models for faster processing
   - Implement query caching

## 📈 Future Enhancements

### Planned Features
- Real-time data streaming from ARGO network
- Advanced machine learning models for prediction
- Multi-language support
- Mobile-responsive design improvements
- Export functionality for visualizations and data

### Integration Opportunities
- Jupyter notebook integration
- API endpoints for external access
- Database integration for persistent storage
- Cloud deployment options

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- ARGO float network for oceanographic data
- Streamlit team for the excellent framework
- Plotly and Folium for visualization capabilities
- The oceanographic research community

## 📞 Support

For questions, issues, or contributions:
- Create an issue in the repository
- Contact the development team
- Check the documentation and examples

---

**Note**: This Streamlit application is a conversion of the original Next.js application, maintaining all core functionality while providing a Python-based interface for oceanographic data analysis.
