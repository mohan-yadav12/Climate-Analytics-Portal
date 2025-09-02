"""Greenhouse Gas component package"""
from .layout import create_layout as get_layout  # noqa: F401
# Register callbacks on import
from . import callbacks  # noqa: F401 