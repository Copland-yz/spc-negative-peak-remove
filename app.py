from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import numpy as np
import io
import os
import json
from werkzeug.utils import secure_filename
from spc_reader import SPCFile, read_spc_file, write_spc_file

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        files = request.files.getlist('files')
        file_data = []
        
        for file in files:
            if file and file.filename.endswith('.spc'):
                # Read SPC file
                file_content = file.read()
                x_values, y_values, x_unit = read_spc_file(file_content)
                
                file_info = {
                    'filename': secure_filename(file.filename),
                    'x_values': x_values.tolist(),
                    'y_values': y_values.tolist(),
                    'x_unit': x_unit,  # Include detected unit
                    'original_data': file_content.hex()  # Store original binary data
                }
                file_data.append(file_info)
        
        return jsonify({'success': True, 'files': file_data})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/process', methods=['POST'])
def process_spectra():
    try:
        data = request.json
        threshold = float(data['threshold'])
        files = data['files']
        
        processed_files = []
        
        for file_info in files:
            y_values = np.array(file_info['y_values'])
            x_values = np.array(file_info['x_values'])
            
            # Apply threshold - remove negative peaks
            processed_y = np.where(y_values < threshold, threshold, y_values)
            
            processed_file = {
                'filename': file_info['filename'],
                'x_values': x_values.tolist(),
                'original_y': y_values.tolist(),
                'processed_y': processed_y.tolist(),
                'x_unit': file_info.get('x_unit', 'Unknown'),  # Pass through the unit info
                'original_data': file_info['original_data']
            }
            processed_files.append(processed_file)
        
        return jsonify({'success': True, 'processed_files': processed_files})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save', methods=['POST'])
def save_file():
    try:
        data = request.json
        filename = secure_filename(data['filename'])
        processed_y = np.array(data['processed_y'])
        original_data = bytes.fromhex(data['original_data'])
        
        # Create new SPC file with modified y-values preserving original structure and units
        try:
            spc_file = SPCFile(original_data)
            print(f"Original SPC info: X range {spc_file.x_values[0]:.1f} to {spc_file.x_values[-1]:.1f}")
            print(f"Header info: ftflgs={spc_file.header.get('ftflgs', 'N/A')}, fexper={spc_file.header.get('fexper', 'N/A')}")
            
            new_spc_data = spc_file.write_file(processed_y)
            print("Successfully created SPC file preserving all original formatting and units")
        except Exception as write_error:
            print(f"Failed to preserve original SPC structure: {write_error}")
            return jsonify({'success': False, 'error': f'Could not preserve SPC file format: {write_error}'})
        
        # Save the file
        save_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
        with open(save_path, 'wb') as f:
            f.write(new_spc_data)
        
        return jsonify({'success': True, 'saved_path': save_path})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(app.config['PROCESSED_FOLDER'], filename),
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)