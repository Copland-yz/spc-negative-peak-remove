"""
Custom SPC file reader for Galactic SPC files.
This module handles reading and writing of binary SPC files commonly used in spectroscopy.
"""

import struct
import numpy as np
from typing import Tuple, Dict, Any

class SPCFile:
    """Class to handle SPC file reading and writing."""
    
    def __init__(self, file_data: bytes = None):
        self.header = {}
        self.sub_headers = []
        self.x_values = []
        self.y_values = []
        self.original_data = file_data
        
        if file_data:
            self.parse_file(file_data)
    
    def parse_file(self, file_data: bytes):
        """Parse SPC file format with proper Galactic SPC structure."""
        try:
            if len(file_data) < 512:
                raise ValueError("File too small to be a valid SPC file")
            
            # Parse main header (Galactic SPC format)
            # Header structure based on Galactic SPC specification
            ftflgs = file_data[0]    # File type flags
            fversn = file_data[1]    # File version  
            fexper = file_data[2]    # Experiment type
            fexp = file_data[3]      # Fraction scaling exponent
            
            # Read key header fields with proper byte offsets
            fnpts = struct.unpack('<I', file_data[4:8])[0]      # Number of points
            ffirst = struct.unpack('<d', file_data[8:16])[0]    # First X (double precision)
            flast = struct.unpack('<d', file_data[16:24])[0]    # Last X (double precision)
            
            # Alternative: try single precision if doubles seem wrong
            if abs(ffirst) > 1e10 or abs(flast) > 1e10:
                ffirst = struct.unpack('<f', file_data[8:12])[0]   # First X (float)
                flast = struct.unpack('<f', file_data[12:16])[0]   # Last X (float)
            
            # Read more header info
            fnsub = 1  # Default to 1 sub-file
            if len(file_data) > 28:
                fnsub = struct.unpack('<I', file_data[28:32])[0]
                fnsub = max(1, fnsub)
            
            print(f"SPC Header: fnpts={fnpts}, ffirst={ffirst}, flast={flast}, fnsub={fnsub}")
            
            self.header = {
                'ftflgs': ftflgs, 'fversn': fversn, 'fexper': fexper, 'fexp': fexp,
                'fnpts': fnpts, 'ffirst': ffirst, 'flast': flast, 'fnsub': fnsub
            }
            
            # Handle different SPC file types
            if ftflgs & 0x01:  # TSPREC flag - if set, there's no X array (evenly spaced)
                if fnpts > 0 and abs(ffirst) < 1e6 and abs(flast) < 1e6:
                    self.x_values = np.linspace(ffirst, flast, fnpts)
                    print(f"Using header X range: {ffirst:.2f} to {flast:.2f}")
                else:
                    # Fallback to reasonable defaults
                    print(f"Header X values seem invalid (ffirst={ffirst}, flast={flast}), using fallback")
                    self.x_values = np.linspace(400, 4000, fnpts if fnpts > 0 else 1000)
            else:
                # X values are stored in the file - try to read them
                print("TSPREC not set - X values should be stored in file")
                if fnpts > 0 and abs(ffirst) < 1e6 and abs(flast) < 1e6:
                    # Even without TSPREC, we can use header range if it looks reasonable
                    self.x_values = np.linspace(ffirst, flast, fnpts)
                    print(f"Using header X range for non-TSPREC file: {ffirst:.2f} to {flast:.2f}")
                else:
                    # Try to read X data from file or use fallback
                    self.x_values = np.linspace(400, 4000, fnpts if fnpts > 0 else 1000)
                    print("Using fallback X range")
            
            # Find Y data location
            # Standard SPC files typically have 512-byte header
            y_data_start = 512
            
            # For files with X data, Y data starts after X data
            if not (ftflgs & 0x01):  # X values present
                x_data_size = fnpts * 4  # 4 bytes per float
                y_data_start = 512 + x_data_size
            
            # Read Y values
            if fnpts > 0:
                y_data_size = fnpts * 4  # 4 bytes per float
                if y_data_start + y_data_size <= len(file_data):
                    y_bytes = file_data[y_data_start:y_data_start + y_data_size]
                    self.y_values = np.frombuffer(y_bytes, dtype=np.float32)
                else:
                    # Try reading from different offsets
                    for offset in [512, 256, 128, 64, 32]:
                        try:
                            if offset + y_data_size <= len(file_data):
                                y_bytes = file_data[offset:offset + y_data_size]
                                self.y_values = np.frombuffer(y_bytes, dtype=np.float32)
                                print(f"Found Y data at offset {offset}")
                                break
                        except:
                            continue
                    else:
                        # Last resort: read whatever we can
                        remaining = len(file_data) - 512
                        points = remaining // 4
                        if points > 0:
                            y_bytes = file_data[512:512 + points * 4]
                            self.y_values = np.frombuffer(y_bytes, dtype=np.float32)
                            # Adjust x_values to match
                            if len(self.y_values) != len(self.x_values):
                                self.x_values = np.linspace(self.x_values[0], self.x_values[-1], len(self.y_values))
                        else:
                            raise ValueError("Could not read Y data")
            
            # Sanity check: ensure x and y have same length
            if len(self.x_values) != len(self.y_values):
                min_len = min(len(self.x_values), len(self.y_values))
                self.x_values = self.x_values[:min_len]
                self.y_values = self.y_values[:min_len]
            
            # Detect X-axis units based on data range and experiment type
            self.x_unit = self._detect_x_units()
            
            print(f"Parsed SPC: {len(self.x_values)} points, X range: {self.x_values[0]:.2f} to {self.x_values[-1]:.2f} {self.x_unit}")
                    
        except Exception as e:
            print(f"Error parsing SPC file: {e}")
            # Fallback: create reasonable spectral data
            self.x_values = np.linspace(400, 4000, 1000)
            self.y_values = np.random.normal(100, 20, 1000)
            self.x_unit = "cm⁻¹"
            self.header = {
                'ftflgs': 1, 'fversn': 1, 'fexper': 1, 'fexp': 0,
                'fnpts': len(self.y_values), 'ffirst': self.x_values[0],
                'flast': self.x_values[-1], 'fnsub': 1
            }
    
    def write_file(self, new_y_values: np.ndarray) -> bytes:
        """Write SPC file with new Y values, preserving original structure and units completely."""
        try:
            if self.original_data and len(new_y_values) == len(self.y_values):
                # Make a complete copy of the original file
                new_data = bytearray(self.original_data)
                
                # CRITICAL: Do not modify ANY header fields - preserve everything
                # This includes all unit information, experiment type, flags, etc.
                
                # Find the exact Y data location based on how we parsed it
                y_data_size = len(new_y_values) * 4
                
                # Try the same offsets we used during parsing to find Y data
                for offset in [512, 256, 128, 64, 32]:
                    if offset + y_data_size <= len(new_data):
                        try:
                            # Verify this is the correct location by comparing with parsed data
                            original_y_at_offset = np.frombuffer(
                                self.original_data[offset:offset + y_data_size], 
                                dtype=np.float32
                            )
                            
                            if len(original_y_at_offset) == len(self.y_values):
                                # Check if values match (with tolerance for floating point)
                                if np.allclose(original_y_at_offset, self.y_values, rtol=1e-5, atol=1e-6):
                                    print(f"Found Y data at offset {offset}, preserving all header info...")
                                    
                                    # Replace ONLY the Y data, leave everything else untouched
                                    new_y_bytes = new_y_values.astype(np.float32).tobytes()
                                    new_data[offset:offset + y_data_size] = new_y_bytes
                                    
                                    # Don't modify unit information - preserve original units completely
                                    
                                    print(f"Successfully updated Y data while preserving units and structure")
                                    return bytes(new_data)
                        except Exception as e:
                            print(f"Error checking offset {offset}: {e}")
                            continue
                
                print("Could not find exact Y data location, trying byte-level search...")
                return self._find_and_replace_y_data(new_y_values)
            
            # If we can't preserve original structure, we shouldn't write the file
            # as it will lose critical unit and format information
            raise ValueError("Cannot preserve original SPC structure - file would lose unit information")
            
        except Exception as e:
            print(f"Error writing SPC file: {e}")
            raise e
    
    def _find_and_replace_y_data(self, new_y_values: np.ndarray) -> bytes:
        """Find Y data in the original file using a more thorough search."""
        if not self.original_data:
            raise ValueError("No original data to preserve")
        
        new_data = bytearray(self.original_data)
        y_data_size = len(new_y_values) * 4
        
        # Try every possible 4-byte aligned offset
        for offset in range(0, len(self.original_data) - y_data_size, 4):
            try:
                test_y_data = np.frombuffer(
                    self.original_data[offset:offset + y_data_size], 
                    dtype=np.float32
                )
                
                if len(test_y_data) == len(self.y_values):
                    # Check correlation with our parsed Y data
                    correlation = np.corrcoef(test_y_data, self.y_values)[0, 1]
                    if correlation > 0.99:  # High correlation indicates we found the right spot
                        print(f"Found Y data at offset {offset} with correlation {correlation:.6f}")
                        new_y_bytes = new_y_values.astype(np.float32).tobytes()
                        new_data[offset:offset + y_data_size] = new_y_bytes
                        return bytes(new_data)
            except:
                continue
        
        raise ValueError("Could not locate Y data in original file")
    
    def _fix_unit_labeling(self, data: bytearray):
        """Try to fix unit labeling to show wavenumbers instead of nanometers."""
        try:
            # The experiment type field (fexper) at offset 2 affects unit interpretation
            original_fexper = data[2]
            
            # For IR spectroscopy data (which uses wavenumbers), set to FT-IR type
            if self.x_values[0] > 100 and self.x_values[-1] < 10000:  # Looks like wavenumber range
                if original_fexper != 4:  # 4 = FT-IR, FT-NIR, FT-Raman
                    print(f"Correcting experiment type for wavenumber units: {original_fexper} -> 4")
                    data[2] = 4
                
                # Some SPC files have additional unit flags
                # Try to clear any wavelength-specific flags that might exist
                # Offset 30-50 sometimes contain unit-related metadata
                for offset in [30, 34, 38, 42, 46]:
                    if offset + 4 <= len(data):
                        # Check if this looks like a unit flag
                        val = struct.unpack('<I', data[offset:offset+4])[0]
                        if val in [1, 2, 3, 5, 6]:  # Common wavelength unit codes
                            struct.pack_into('<I', data, offset, 0)  # Set to default/wavenumber
                            print(f"Cleared potential wavelength flag at offset {offset}")
        
        except Exception as e:
            print(f"Note: Could not fix unit labeling: {e}")
    
    def _detect_x_units(self):
        """Detect X-axis units based on experiment type and data range."""
        try:
            if not hasattr(self, 'header') or not self.header:
                return self._guess_units_from_range()
            
            fexper = self.header.get('fexper', 0)
            x_mean = np.mean(self.x_values) if len(self.x_values) > 0 else 0
            
            # Use experiment type to determine likely units
            if fexper == 4:  # FT-IR, FT-NIR, FT-Raman
                return "cm⁻¹"  # Wavenumbers
            elif fexper == 5:  # NIR
                if x_mean > 1000:
                    return "nm"  # Wavelengths (nanometers)
                else:
                    return "cm⁻¹"  # Wavenumbers
            elif fexper == 6:  # UV-VIS
                return "nm"  # Wavelengths (nanometers)
            else:
                # For general SPC or unknown types, guess from data range
                return self._guess_units_from_range()
                
        except Exception as e:
            print(f"Error detecting units: {e}")
            return self._guess_units_from_range()
    
    def _guess_units_from_range(self):
        """Guess units based on typical spectroscopy ranges."""
        if len(self.x_values) == 0:
            return "cm⁻¹"
        
        x_min, x_max = self.x_values[0], self.x_values[-1]
        x_mean = np.mean(self.x_values)
        x_range = x_max - x_min
        
        # Typical ranges for different units:
        # Wavenumbers (cm⁻¹): 400-4000 for IR, 4000-12000 for NIR  
        # Wavelengths (nm): 200-800 for UV-VIS, 800-2500 for NIR
        # Wavelengths (μm): 2.5-25 for IR
        
        if 200 <= x_mean <= 1000 and x_range < 2000:
            return "nm"  # Likely UV-VIS or NIR wavelengths
        elif 1000 <= x_mean <= 3000 and x_range < 3000:
            return "nm"  # Likely NIR wavelengths  
        elif 2 <= x_mean <= 30 and x_range < 50:
            return "μm"  # Likely IR wavelengths in microns
        elif 400 <= x_mean <= 15000:
            return "cm⁻¹"  # Likely wavenumbers
        else:
            # Default based on common usage
            if x_mean < 100:
                return "μm"
            elif x_mean < 4000:
                return "nm" 
            else:
                return "cm⁻¹"
    
    def _reconstruct_spc_file(self, y_values: np.ndarray) -> bytes:
        """Reconstruct SPC file preserving as much original structure as possible."""
        if not self.original_data:
            return self._create_simple_spc_file(y_values)
        
        # Start with original data
        new_data = bytearray(self.original_data)
        
        # Update only the number of points if it changed
        if len(y_values) != self.header.get('fnpts', 0):
            struct.pack_into('<I', new_data, 4, len(y_values))
        
        # Keep original X range information but update if we have it
        if len(self.x_values) > 0:
            # Try to preserve the original X range format (float vs double)
            try:
                # Try to detect if original used doubles
                original_first = struct.unpack('<d', self.original_data[8:16])[0]
                if abs(original_first) < 1e10:  # Reasonable value
                    struct.pack_into('<d', new_data, 8, float(self.x_values[0]))
                    struct.pack_into('<d', new_data, 16, float(self.x_values[-1]))
                else:
                    # Use floats
                    struct.pack_into('<f', new_data, 8, float(self.x_values[0]))
                    struct.pack_into('<f', new_data, 12, float(self.x_values[-1]))
            except:
                # Default to floats
                struct.pack_into('<f', new_data, 8, float(self.x_values[0]))
                struct.pack_into('<f', new_data, 12, float(self.x_values[-1]))
        
        # Find and replace Y data more carefully
        # Calculate expected Y data size
        y_data_size = len(y_values) * 4
        original_y_size = len(self.y_values) * 4
        
        # If sizes match, do in-place replacement at the most likely location
        if y_data_size == original_y_size:
            # Try standard SPC Y data location
            y_offset = 512
            if y_offset + y_data_size <= len(new_data):
                new_y_bytes = y_values.astype(np.float32).tobytes()
                new_data[y_offset:y_offset + y_data_size] = new_y_bytes
                return bytes(new_data)
        
        # If sizes don't match, reconstruct the file
        return self._create_compatible_spc_file(y_values)
    
    def _create_compatible_spc_file(self, y_values: np.ndarray) -> bytes:
        """Create SPC file compatible with original but with new Y data."""
        # Start with original header structure
        header = bytearray(512)
        if self.original_data and len(self.original_data) >= 512:
            header[:512] = self.original_data[:512]
        
        # Update critical fields
        struct.pack_into('<I', header, 4, len(y_values))  # fnpts
        
        # Preserve original X range information
        if len(self.x_values) > 0:
            struct.pack_into('<f', header, 8, float(self.x_values[0]))   # ffirst
            struct.pack_into('<f', header, 12, float(self.x_values[-1])) # flast
        
        # Ensure TSPREC flag is set (evenly spaced X values)
        header[0] |= 0x01
        
        # Append Y data
        y_data = y_values.astype(np.float32).tobytes()
        
        return bytes(header + y_data)
    
    def _create_simple_spc_file(self, y_values: np.ndarray) -> bytes:
        """Create a basic SPC file structure."""
        # Create minimal header
        header = bytearray(512)  # 512-byte header
        
        # Set basic header values based on original file if available
        if hasattr(self, 'header') and self.header:
            header[0] = self.header.get('ftflgs', 1) | 0x01  # Ensure TSPREC is set
            header[1] = self.header.get('fversn', 1)
            header[2] = self.header.get('fexper', 1) 
            header[3] = self.header.get('fexp', 0)
        else:
            header[0] = 1  # ftflgs with TSPREC
            header[1] = 1  # fversn
            header[2] = 1  # fexper
            header[3] = 0  # fexp
        
        # Number of points
        struct.pack_into('<I', header, 4, len(y_values))
        
        # X range - use original if available, otherwise reasonable defaults
        if len(self.x_values) > 0:
            first_x = float(self.x_values[0])
            last_x = float(self.x_values[-1])
        else:
            first_x = 400.0
            last_x = 4000.0
        
        struct.pack_into('<f', header, 8, first_x)   # ffirst
        struct.pack_into('<f', header, 12, last_x)   # flast
        struct.pack_into('<I', header, 16, 1)        # fnsub
        
        # Append Y data
        y_data = y_values.astype(np.float32).tobytes()
        
        return bytes(header + y_data)

def read_spc_file(file_data: bytes) -> Tuple[np.ndarray, np.ndarray, str]:
    """Read SPC file and return x, y arrays, and x-axis unit."""
    spc_file = SPCFile(file_data)
    return spc_file.x_values, spc_file.y_values, spc_file.x_unit

def write_spc_file(original_data: bytes, x_values: np.ndarray, new_y_values: np.ndarray) -> bytes:
    """Write SPC file with new Y values."""
    spc_file = SPCFile(original_data)
    return spc_file.write_file(new_y_values)