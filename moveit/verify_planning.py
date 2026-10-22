"""Compatibility entry point for the driver-free UR planning check."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).with_name('verify_runtime.py')), run_name='__main__')
