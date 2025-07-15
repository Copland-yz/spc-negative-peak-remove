#!/usr/bin/env python3
"""
Investigate and fix SPC unit labeling issues.
The Galactic SPC format has specific header fields that control how GRAMS displays units.
"""

import struct
import numpy as np
from spc_reader import SPCFile

def analyze_spc_unit_fields(filename):
    """Deep dive into SPC header fields that control unit display."""
    try:
        with open(filename, 'rb') as f:
            data = f.read()
        
        print(f"Analyzing unit fields in: {filename}")
        print(f"File size: {len(data)} bytes\n")
        
        # The SPC format has several fields that affect unit interpretation
        print("=== Header Analysis ===")
        
        # Basic header fields
        ftflgs = data[0]
        fversn = data[1]
        fexper = data[2]
        fexp = data[3]
        
        print(f"ftflgs: 0x{ftflgs:02x} ({ftflgs:08b})")
        print(f"fversn: {fversn}")
        print(f"fexper: {fexper} (experiment type)")
        print(f"fexp: {fexp}")
        print()
        
        # Key experiment types for spectroscopy
        if fexper == 4:
            print("Experiment type 4: FT-IR, FT-NIR, FT-Raman (should use wavenumbers)")
        elif fexper == 5:
            print("Experiment type 5: NIR (could use wavelengths)")
        elif fexper == 6:
            print("Experiment type 6: UV-VIS (typically wavelengths)")
        else:
            print(f"Experiment type {fexper}: See SPC specification")
        print()
        
        # Read more header fields - SPC headers can be quite large
        print("=== Extended Header Fields ===")
        
        # Read 32-bit values throughout the header
        for offset in range(0, min(128, len(data)), 4):
            if offset + 4 <= len(data):
                try:
                    val_uint = struct.unpack('<I', data[offset:offset+4])[0]
                    val_int = struct.unpack('<i', data[offset:offset+4])[0]
                    val_float = struct.unpack('<f', data[offset:offset+4])[0]
                    
                    print(f"Offset {offset:3d}: uint={val_uint:10d} int={val_int:10d} float={val_float:10.3f}")
                except:
                    pass
        
        print()
        
        # Check for ASCII strings in header (unit labels might be stored as text)
        print("=== ASCII Strings in Header ===")
        header_portion = data[:512] if len(data) >= 512 else data
        
        # Look for printable ASCII sequences
        current_string = ""
        for i, byte_val in enumerate(header_portion):
            if 32 <= byte_val <= 126:  # Printable ASCII
                current_string += chr(byte_val)
            else:
                if len(current_string) >= 3:  # Only show strings of 3+ chars
                    print(f"Offset {i-len(current_string):3d}: '{current_string}'")
                current_string = ""
        
        if len(current_string) >= 3:
            print(f"Offset {len(header_portion)-len(current_string):3d}: '{current_string}'")
        
        print()
        
        # Parse with our reader to see current interpretation
        spc_file = SPCFile(data)
        print(f"Current interpretation: X={spc_file.x_values[0]:.1f} to {spc_file.x_values[-1]:.1f}")
        
    except Exception as e:
        print(f"Error analyzing file: {e}")

def create_wavenumber_spc_file(input_filename, output_filename):
    """Create a copy of SPC file with corrected unit metadata."""
    try:
        with open(input_filename, 'rb') as f:
            data = f.read()
        
        print(f"Creating wavenumber-corrected version...")
        
        # Make a copy of the data
        new_data = bytearray(data)
        
        # Force experiment type to FT-IR (type 4) which typically uses wavenumbers
        original_fexper = new_data[2]
        new_data[2] = 4  # FT-IR experiment type
        print(f"Changed experiment type: {original_fexper} -> 4 (FT-IR)")
        
        # Some SPC files have additional unit flags or identifiers
        # Let's try a few common patterns:
        
        # Look for specific byte patterns that might indicate wavelength vs wavenumber
        # This is somewhat trial-and-error based on the SPC spec
        
        # Check if there are any obvious wavelength indicators we can change
        changes_made = []
        
        # Sometimes unit info is stored as specific values in the header
        # Let's try changing any suspicious values
        for offset in [20, 24, 28, 32, 36, 40, 44, 48]:
            if offset + 4 <= len(new_data):
                original_val = struct.unpack('<I', new_data[offset:offset+4])[0]
                
                # Look for values that might indicate wavelength units
                # This is speculative but based on common SPC patterns
                if original_val in [1, 2, 3]:  # Common unit codes
                    # Try setting to a wavenumber unit code
                    struct.pack_into('<I', new_data, offset, 0)  # 0 often means wavenumber
                    changes_made.append(f"Offset {offset}: {original_val} -> 0")
        
        if changes_made:
            print("Unit-related changes made:")
            for change in changes_made:
                print(f"  {change}")
        else:
            print("No obvious unit fields found to modify")
        
        # Save the modified file
        with open(output_filename, 'wb') as f:
            f.write(new_data)
        
        print(f"Saved corrected file as: {output_filename}")
        print("Try opening this file in GRAMS to see if the unit label is corrected")
        
    except Exception as e:
        print(f"Error creating corrected file: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fix_units.py <input_spc_file> [output_spc_file]")
        print("This script analyzes and attempts to fix unit labeling in SPC files")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "corrected_" + input_file
    
    print("Step 1: Analyzing unit fields in SPC file")
    analyze_spc_unit_fields(input_file)
    
    print("\nStep 2: Creating unit-corrected version")
    create_wavenumber_spc_file(input_file, output_file)