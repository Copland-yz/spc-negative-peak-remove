#!/usr/bin/env python3
"""
Test unit detection with different spectral ranges.
"""

import numpy as np
from spc_reader import SPCFile

def test_unit_detection():
    """Test unit detection for different spectral types."""
    
    test_cases = [
        {
            'name': 'IR Wavenumbers',
            'x_range': (400, 4000),
            'points': 1000,
            'expected_unit': 'cm⁻¹',
            'experiment_type': 4  # FT-IR
        },
        {
            'name': 'NIR Wavelengths', 
            'x_range': (800, 2500),
            'points': 500,
            'expected_unit': 'nm',
            'experiment_type': 5  # NIR
        },
        {
            'name': 'UV-VIS Wavelengths',
            'x_range': (200, 800),
            'points': 600,
            'expected_unit': 'nm', 
            'experiment_type': 6  # UV-VIS
        },
        {
            'name': 'IR Wavelengths (microns)',
            'x_range': (2.5, 25),
            'points': 400,
            'expected_unit': 'μm',
            'experiment_type': 1  # General
        }
    ]
    
    print("Testing unit detection:")
    print("=" * 50)
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"X range: {test['x_range'][0]} - {test['x_range'][1]}")
        print(f"Expected unit: {test['expected_unit']}")
        
        # Create test data
        x_values = np.linspace(test['x_range'][0], test['x_range'][1], test['points'])
        y_values = np.random.normal(100, 20, test['points'])
        
        # Create SPC file
        spc_file = SPCFile()
        spc_file.x_values = x_values
        spc_file.y_values = y_values
        spc_file.header = {
            'ftflgs': 1, 'fversn': 1, 'fexper': test['experiment_type'], 'fexp': 0,
            'fnpts': len(y_values), 'ffirst': x_values[0],
            'flast': x_values[-1], 'fnsub': 1
        }
        
        # Test unit detection
        detected_unit = spc_file._detect_x_units()
        
        print(f"Detected unit: {detected_unit}")
        print(f"✓ PASS" if detected_unit == test['expected_unit'] else f"✗ FAIL")
        
        # Test full workflow
        test_data = spc_file._create_simple_spc_file(y_values)
        roundtrip_spc = SPCFile(test_data)
        
        print(f"Roundtrip unit: {roundtrip_spc.x_unit}")
        print(f"Roundtrip ✓ PASS" if roundtrip_spc.x_unit == test['expected_unit'] else f"Roundtrip ✗ FAIL")

if __name__ == "__main__":
    test_unit_detection()