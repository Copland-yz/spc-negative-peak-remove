#!/usr/bin/env python3
"""
Create a test SPC file with some negative peaks for testing the application.
"""

import numpy as np
from spc_reader import SPCFile

def create_test_spc_file():
    """Create a test SPC file with negative peaks."""
    # Generate test spectral data
    x_values = np.linspace(400, 4000, 1000)  # Wavenumber range typical for IR spectroscopy
    
    # Create a spectrum with several peaks and some negative values
    y_values = np.zeros_like(x_values)
    
    # Add some positive peaks
    y_values += 100 * np.exp(-((x_values - 1600) / 50)**2)  # Peak at 1600 cm-1
    y_values += 80 * np.exp(-((x_values - 2900) / 40)**2)   # Peak at 2900 cm-1
    y_values += 60 * np.exp(-((x_values - 3400) / 60)**2)   # Peak at 3400 cm-1
    
    # Add some negative peaks (artifacts that we want to remove)
    y_values += -30 * np.exp(-((x_values - 1000) / 30)**2)  # Negative peak at 1000 cm-1
    y_values += -20 * np.exp(-((x_values - 2000) / 25)**2)  # Negative peak at 2000 cm-1
    y_values += -40 * np.exp(-((x_values - 3000) / 35)**2)  # Negative peak at 3000 cm-1
    
    # Add some noise
    y_values += np.random.normal(0, 5, len(x_values))
    
    # Create SPC file
    spc_file = SPCFile()
    spc_file.x_values = x_values
    spc_file.y_values = y_values
    spc_file.header = {
        'ftflgs': 0, 'fversn': 1, 'fexper': 1, 'fexp': 0,
        'fnpts': len(y_values), 'ffirst': x_values[0],
        'flast': x_values[-1], 'fnsub': 1
    }
    
    # Write test file
    test_data = spc_file._create_simple_spc_file(y_values)
    with open('test_spectrum.spc', 'wb') as f:
        f.write(test_data)
    
    print(f"Created test SPC file: test_spectrum.spc")
    print(f"Spectrum range: {x_values[0]:.1f} - {x_values[-1]:.1f} cm⁻¹")
    print(f"Number of points: {len(y_values)}")
    print(f"Y-value range: {y_values.min():.1f} to {y_values.max():.1f}")
    print(f"Negative values present: {np.sum(y_values < 0)} points")

if __name__ == "__main__":
    create_test_spc_file()