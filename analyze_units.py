#!/usr/bin/env python3
"""
Analyze SPC file units and structure to debug unit preservation issues.
"""

import struct
import numpy as np
from spc_reader import SPCFile

def analyze_spc_units(filename):
    """Analyze SPC file to understand unit encoding."""
    try:
        with open(filename, 'rb') as f:
            data = f.read()
        
        print(f"Analyzing SPC file: {filename}")
        print(f"File size: {len(data)} bytes")
        print()
        
        # Parse header fields that affect units
        ftflgs = data[0]
        fversn = data[1]
        fexper = data[2]
        fexp = data[3]
        
        print("Header analysis for unit information:")
        print(f"ftflgs: 0x{ftflgs:02x} ({ftflgs:08b})")
        print("  Bit 0 (TSPREC): ", "Set" if ftflgs & 0x01 else "Clear", "(evenly spaced X)")
        print("  Bit 1 (TCGRAM): ", "Set" if ftflgs & 0x02 else "Clear")
        print("  Bit 2 (TMULTI): ", "Set" if ftflgs & 0x04 else "Clear", "(multiple Y values per X)")
        print("  Bit 3 (TRANDM): ", "Set" if ftflgs & 0x08 else "Clear", "(randomly spaced X)")
        print("  Bit 4 (TORDRD): ", "Set" if ftflgs & 0x10 else "Clear", "(ordered X data)")
        print("  Bit 5 (TALABS): ", "Set" if ftflgs & 0x20 else "Clear", "(X axis label)")
        print("  Bit 6 (TXYXYS): ", "Set" if ftflgs & 0x40 else "Clear", "(X,Y,X,Y data)")
        print("  Bit 7 (TXVALS): ", "Set" if ftflgs & 0x80 else "Clear", "(X values present)")
        print()
        
        print(f"fversn: {fversn} (file version)")
        print(f"fexper: {fexper} (experiment type)")
        
        # Experiment type meanings (from SPC specification)
        exp_types = {
            0: "General SPC",
            1: "Gas Chromatography",
            2: "General Chromatography", 
            3: "HPLC Chromatography",
            4: "FT-IR, FT-NIR, FT-Raman",
            5: "NIR",
            6: "UV-VIS",
            7: "X-ray",
            8: "Mass Spectroscopy",
            9: "NMR Spectroscopy or FT-NMR",
            10: "ESR Spectroscopy",
            11: "Fluorescence Spectroscopy",
            12: "Atomic Spectroscopy",
            13: "Chromatography Diode Array"
        }
        exp_type_name = exp_types.get(fexper, f"Unknown ({fexper})")
        print(f"  Experiment type: {exp_type_name}")
        print()
        
        print(f"fexp: {fexp} (fraction scaling exponent)")
        print()
        
        # Read X range values
        fnpts = struct.unpack('<I', data[4:8])[0]
        
        # Try both float and double for X range
        try:
            ffirst_f = struct.unpack('<f', data[8:12])[0]
            flast_f = struct.unpack('<f', data[12:16])[0]
            print(f"X range (as floats): {ffirst_f:.6f} to {flast_f:.6f}")
        except:
            print("Could not read X range as floats")
        
        try:
            ffirst_d = struct.unpack('<d', data[8:16])[0]
            flast_d = struct.unpack('<d', data[16:24])[0]
            print(f"X range (as doubles): {ffirst_d:.6f} to {flast_d:.6f}")
        except:
            print("Could not read X range as doubles")
        
        print()
        print(f"Number of points: {fnpts}")
        print()
        
        # Additional header fields that might affect units
        print("Additional header fields:")
        for offset in range(24, min(64, len(data)), 4):
            try:
                val = struct.unpack('<I', data[offset:offset+4])[0]
                print(f"  Offset {offset}: {val} (0x{val:08x})")
            except:
                pass
        
        print()
        
        # Parse using our reader
        print("Using our SPC reader:")
        spc_file = SPCFile(data)
        print(f"Parsed X range: {spc_file.x_values[0]:.6f} to {spc_file.x_values[-1]:.6f}")
        print(f"Number of points: {len(spc_file.x_values)}")
        print(f"Y range: {spc_file.y_values.min():.6f} to {spc_file.y_values.max():.6f}")
        
        # Check if X values look like wavenumbers or wavelengths
        x_range = spc_file.x_values[-1] - spc_file.x_values[0]
        x_mean = spc_file.x_values.mean()
        
        print()
        print("Unit analysis:")
        if 100 <= x_mean <= 10000:
            print("  X values appear to be WAVENUMBERS (cm⁻¹)")
        elif 200 <= x_mean <= 2000:
            print("  X values appear to be WAVELENGTHS (nanometers)")
        else:
            print(f"  X values have unusual range for spectroscopy: mean = {x_mean:.1f}")
        
        print(f"  X range span: {x_range:.1f}")
        print(f"  X mean: {x_mean:.1f}")
        
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_spc_units(sys.argv[1])
    else:
        print("Usage: python analyze_units.py <spc_file>")
        print("This script analyzes SPC file headers to understand unit encoding")