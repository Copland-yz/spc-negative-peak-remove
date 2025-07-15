#!/usr/bin/env python3
"""
Test script to verify SPC file writing preserves structure correctly.
"""

import numpy as np
from spc_reader import SPCFile

def test_spc_roundtrip():
    """Test that we can read an SPC file, modify it, and write it back correctly."""
    
    # Create test data
    print("Creating test SPC file...")
    x_values = np.linspace(400, 4000, 1000)
    y_values = np.sin(x_values / 500) * 100 + np.random.normal(0, 5, 1000)
    
    # Add some negative values to test threshold removal
    y_values[200:300] -= 150  # Make some values negative
    
    # Create original SPC file
    spc_file = SPCFile()
    spc_file.x_values = x_values
    spc_file.y_values = y_values
    spc_file.header = {
        'ftflgs': 1, 'fversn': 1, 'fexper': 1, 'fexp': 0,
        'fnpts': len(y_values), 'ffirst': x_values[0],
        'flast': x_values[-1], 'fnsub': 1
    }
    
    original_data = spc_file._create_simple_spc_file(y_values)
    with open('test_original.spc', 'wb') as f:
        f.write(original_data)
    
    print(f"Original: {len(y_values)} points, X: {x_values[0]:.1f}-{x_values[-1]:.1f}, Y: {y_values.min():.1f} to {y_values.max():.1f}")
    
    # Read it back
    print("\nReading SPC file...")
    spc_read = SPCFile(original_data)
    print(f"Read back: {len(spc_read.y_values)} points, X: {spc_read.x_values[0]:.1f}-{spc_read.x_values[-1]:.1f}")
    
    # Apply threshold (remove negative values)
    threshold = 0
    processed_y = np.where(spc_read.y_values < threshold, threshold, spc_read.y_values)
    print(f"After threshold: Y range {processed_y.min():.1f} to {processed_y.max():.1f}")
    
    # Write back
    print("\nWriting processed SPC file...")
    new_data = spc_read.write_file(processed_y)
    with open('test_processed.spc', 'wb') as f:
        f.write(new_data)
    
    # Verify the processed file
    print("\nVerifying processed file...")
    spc_verify = SPCFile(new_data)
    print(f"Verified: {len(spc_verify.y_values)} points, X: {spc_verify.x_values[0]:.1f}-{spc_verify.x_values[-1]:.1f}")
    print(f"Y range: {spc_verify.y_values.min():.1f} to {spc_verify.y_values.max():.1f}")
    
    # Check if X-axis is preserved
    x_diff = np.abs(spc_read.x_values - spc_verify.x_values).max()
    print(f"X-axis preservation error: {x_diff:.6f}")
    
    # Check if Y processing worked
    negative_count_original = np.sum(spc_read.y_values < 0)
    negative_count_processed = np.sum(spc_verify.y_values < 0)
    print(f"Negative values: original={negative_count_original}, processed={negative_count_processed}")
    
    print("\nTest files created:")
    print("  test_original.spc - Original file with negative peaks")
    print("  test_processed.spc - Processed file with negative peaks removed")
    print("\nTry opening both files in GRAMS to verify they display correctly!")

if __name__ == "__main__":
    test_spc_roundtrip()