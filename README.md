# SPC Negative Peak Removal Tool

A web-based application for removing negative peaks from emission line spectra stored in Galactic SPC files. This tool provides an interactive interface for setting thresholds, visualizing spectra, and saving processed files with automatic unit detection.

![SPC Tool Demo](https://img.shields.io/badge/Status-Working-brightgreen) ![Python](https://img.shields.io/badge/Python-3.7+-blue) ![Flask](https://img.shields.io/badge/Flask-2.3+-green)

## ✨ Features

- **🎯 Drag & Drop Upload**: Upload multiple SPC files simultaneously
- **📊 Interactive Visualization**: Real-time comparison of original vs processed spectra using Plotly.js
- **🎛️ Threshold Control**: Set custom thresholds for negative peak removal (e.g., set values < 0 to 0)
- **🔧 Smart Unit Detection**: Automatically detects X-axis units (nm, cm⁻¹, μm) from SPC headers
- **💾 File Processing**: Preserves original SPC file headers while modifying spectral data
- **📁 Download Results**: Save processed SPC files compatible with GRAMS and other spectroscopy software

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Application**:
   ```bash
   python app.py
   ```
   Or use the startup script:
   ```bash
   ./start_server.sh
   ```

3. **Access the Web Interface**:
   Open your browser and go to: `http://localhost:5001`

4. **Test with Sample Data**:
   ```bash
   python create_test_spc.py
   ```
   This creates `test_spectrum.spc` with negative peaks for testing.

## 📖 How to Use

1. **Upload Files**: Drag and drop your .spc files into the upload area
2. **Set Threshold**: Enter the threshold value (e.g., 0 to remove all negative values)
3. **Process**: Click "Process Spectra" to apply the threshold
4. **Visualize**: View the interactive comparison plot with correct unit labels
5. **Save**: Enter a filename and click "Save SPC File" to download the processed file

## 🔬 Technical Details

### Backend (Python/Flask)
- Custom SPC file reader/writer for handling Galactic SPC format
- Binary file processing with complete header preservation
- Intelligent unit detection from SPC headers and data ranges
- RESTful API endpoints for file operations

### Frontend (HTML/CSS/JavaScript)
- Modern responsive design with intuitive interface
- Plotly.js for interactive spectral visualization
- Dynamic axis labeling based on detected units
- Drag-and-drop file upload with progress feedback

### File Format Support
- **Galactic SPC files (.spc)**: Full support for binary SPC format
- **Unit Detection**: Automatically detects nm, cm⁻¹, μm based on experiment type and data range
- **Header Preservation**: Maintains all original metadata and file structure
- **Software Compatibility**: Files open correctly in GRAMS and other spectroscopy software

## 🛠️ API Endpoints

- `POST /upload` - Upload and parse SPC files with unit detection
- `POST /process` - Apply threshold-based peak removal
- `POST /save` - Save processed files with preserved headers
- `GET /download/<filename>` - Download processed files

## 📁 Project Structure

```
/
├── app.py                 # Flask backend application
├── spc_reader.py         # Custom SPC file reader/writer with unit detection
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html       # Web interface with dynamic unit labeling
├── uploads/             # Temporary uploaded files
├── processed/           # Saved processed files
├── start_server.sh      # Startup script
├── create_test_spc.py   # Test file generator
├── debug_real_file.py   # Unit detection debugging tool
└── CLAUDE.md           # Development documentation
```

## 📋 Requirements

- Python 3.7+
- Flask
- NumPy
- SciPy
- Werkzeug
- Flask-CORS

## 🔧 Troubleshooting

- **Port 5001 in use**: The app runs on port 5001 by default (configurable in `app.py`)
- **File upload issues**: Ensure files have .spc extension and are valid Galactic SPC format
- **Unit detection issues**: Use `python debug_real_file.py yourfile.spc` to debug unit detection
- **Processing errors**: Check that uploaded files contain valid spectral data
- **Save failures**: Verify write permissions in the processed/ directory

## 🔬 Unit Detection Logic

The tool automatically detects X-axis units using:

1. **SPC Header Analysis**: Reads experiment type (`fexper`) from file headers
2. **Data Range Analysis**: Analyzes X-axis ranges to determine likely units
3. **Smart Fallbacks**: Uses intelligent defaults when headers are unclear

| Range | Experiment Type | Detected Unit | Typical Use |
|-------|----------------|---------------|-------------|
| 200-1000 | Any | nm | UV-VIS, NIR wavelengths |
| 400-4000 | FT-IR (type 4) | cm⁻¹ | IR wavenumbers |
| 800-2500 | NIR (type 5) | nm | NIR wavelengths |
| 2-30 | General | μm | IR wavelengths |

## 🚀 Development

To modify or extend the application:

1. **Backend changes**: Edit `app.py` for API modifications
2. **SPC handling**: Modify `spc_reader.py` for file format changes  
3. **Frontend updates**: Edit `templates/index.html` for UI changes
4. **Testing**: Use `create_test_spc.py` to generate test files
5. **Debugging**: Use `debug_real_file.py` to troubleshoot unit detection

## 📝 License

This project is developed for spectroscopy research and educational purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📞 Support

For issues or questions, please open an issue on GitHub.