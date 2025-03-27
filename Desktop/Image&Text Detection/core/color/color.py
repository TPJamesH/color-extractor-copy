import re
import zlib
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, Set, Tuple, List
from pikepdf import Pdf

class ColorSpace(ABC):
    """Abstract base class for color spaces"""
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def as_rgb(self, value: Tuple[float, ...]) -> Tuple[float, float, float]:
        pass

    def __eq__(self, other):
        return isinstance(other, ColorSpace) and self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __repr__(self):
        return f"ColorSpace(name={self.name})"

class RGBColorSpace(ColorSpace):
    def __init__(self):
        super().__init__('rgb')
    
    def as_rgb(self, value: Tuple[float, ...]) -> Tuple[float, float, float]:
        return value

class CMYKColorSpace(ColorSpace):
    def __init__(self):
        super().__init__('cmyk')
    
    def as_rgb(self, value: Tuple[float, ...]) -> Tuple[float, float, float]:
        c, m, y, k = value
        r = 1.0 - min(1.0, c * (1.0 - k) + k)
        g = 1.0 - min(1.0, m * (1.0 - k) + k)
        b = 1.0 - min(1.0, y * (1.0 - k) + k)
        return (r, g, b)

class GrayColorSpace(ColorSpace):
    def __init__(self):
        super().__init__('gray')
    
    def as_rgb(self, value: Tuple[float, ...]) -> Tuple[float, float, float]:
        return (value[0],) * 3

class Color:
    """Represents a color with usage statistics"""
    def __init__(self, space: ColorSpace, value: Tuple[float, ...]):
        self.space = space
        self.value = value
        self.count = 1
        self._rgb = None
        self._hex = None
    
    @property
    def rgb(self) -> Tuple[float, float, float]:
        if self._rgb is None:
            self._rgb = self.space.as_rgb(self.value)
        return self._rgb
    
    @property
    def hex(self) -> str:
        if self._hex is None:
            r, g, b = (int(channel * 255) for channel in self.rgb)
            self._hex = f"#{r:02X}{g:02X}{b:02X}"
        return self._hex
    
    def __eq__(self, other):
        return (
            isinstance(other, Color) and
            self.space == other.space and
            self.value == other.value
        )
    
    def __hash__(self):
        return hash((self.space, self.value))
    
    def __repr__(self):
        return f"Color(space={self.space.name}, value={self.value}, count={self.count})"

class ColorExtractor:
    """Extracts colors from PDF with usage statistics"""
    COLOR_SPACE_MAP = {
        'rgb': (re.compile(rb'([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+rg[^a-zA-Z]'), RGBColorSpace()),
        'cmyk': (re.compile(rb'([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+k[^a-zA-Z]'), CMYKColorSpace()),
        'gray': (re.compile(rb'([\d.]+)\s+g[^a-zA-Z]'), GrayColorSpace())
    }
    
    def __init__(self):
        self.colors: Dict[Color, Color] = {}
        self.total_count = 0
    
    def extract(self, pdf_path: str) -> Set[Color]:
        """Extract unique colors with usage statistics"""
        pdf = Pdf.open(pdf_path)
        
        for page in pdf.pages:
            if '/Contents' not in page:
                continue
                
            streams = page.Contents
            streams = [streams] if not isinstance(streams, list) else streams
            
            for stream in streams:
                if hasattr(stream, 'get_stream_buffer'):
                    stream_data = bytes(stream.get_stream_buffer())
                    self._process_stream(stream_data)
        
        return set(self.colors.values())
    
    def _process_stream(self, stream_data: bytes):
        """Process a PDF content stream"""
        try:
            try:
                decoded = stream_data.decode('latin-1')
                self._parse_content(decoded.encode('latin-1'))
            except UnicodeDecodeError:
                try:
                    decompressed = zlib.decompress(stream_data)
                    self._parse_content(decompressed)
                except zlib.error:
                    self._parse_content(stream_data)
        except Exception as e:
            print(f"Stream processing error: {e}")
    
    def _parse_content(self, data: bytes):
        """Parse raw PDF content"""
        for space, (pattern, converter) in self.COLOR_SPACE_MAP.items():
            for match in pattern.finditer(data):
                try:
                    components = tuple(float(x.decode('ascii')) for x in match.groups())
                    color = Color(converter, components)
                    
                    if color in self.colors:
                        self.colors[color].count += 1
                    else:
                        self.colors[color] = color
                    
                    self.total_count += 1
                except (ValueError, AttributeError) as e:
                    print(f"Error parsing color: {e}")
    
    def get_usage_stats(self) -> List[Color]:
        """Get colors sorted by usage frequency"""
        return sorted(self.colors.values(), 
                     key=lambda c: c.count, 
                     reverse=True)

# Usage Example
if __name__ == "__main__":
    extractor = ColorExtractor()
    colors = extractor.extract("./color/he-academic-calendar-2024-09.pdf")
    
    print(f"Found {len(colors)} unique colors (from {extractor.total_count} total uses)")
    print("Top 10 colors:")
    for color in extractor.get_usage_stats()[:10]:
        print(f"{color.hex}: {color.space.name} {color.value} - {color.count} uses "
              f"({color.count/extractor.total_count:.1%})")