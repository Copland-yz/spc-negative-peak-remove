# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a web application for removing negative peaks from emission line spectra stored in Galactic SPC files. The application provides an interactive interface for setting thresholds, visualizing spectra, and saving processed files.

## Development Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the Flask application
python app.py
```

The application will be available at http://localhost:5000

## Commands

### Start Development Server
```bash
python app.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Test SPC File Processing
Access the web interface and upload .spc files through the drag-and-drop interface.

## Architecture

### Backend (Flask)
- `app.py`: Main Flask application with API endpoints
  - `/upload`: Handles SPC file uploads and parsing
  - `/process`: Applies negative peak removal threshold
  - `/save`: Saves processed SPC files with preserved headers
  - `/download/<filename>`: Downloads processed files

### Frontend
- `templates/index.html`: Interactive web interface with:
  - Drag-and-drop file upload for multiple SPC files
  - Threshold controls for negative peak removal
  - Interactive Plotly.js visualization comparing original vs processed spectra
  - File saving functionality

### Key Features
- **SPC File Handling**: Uses the `spc` Python library to read/write Galactic SPC files
- **Peak Removal**: Applies user-defined thresholds (e.g., set values < 0 to 0)
- **Visualization**: Real-time interactive plots showing before/after comparison
- **Header Preservation**: Attempts to preserve original SPC file headers when saving

### File Structure
```
/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── uploads/              # Temporary uploaded files
└── processed/            # Saved processed files
```

### SPC File Processing
The application handles binary Galactic SPC files by:
1. Reading with the `spc` library to extract x,y data
2. Applying threshold-based negative peak removal
3. Attempting to preserve the original binary header structure
4. Saving modified files maintaining SPC format compatibility