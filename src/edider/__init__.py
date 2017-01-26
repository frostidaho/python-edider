"""
edider is a package which gives access to information about 
connected computer monitors.

Usage example:
import edider
mons = edider.get_monitors()
print(dir(mons[0]))
"""
__version__ = "0.1.0"
from edider.x11read import get_monitors

