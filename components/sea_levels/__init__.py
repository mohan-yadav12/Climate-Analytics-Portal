"""Sea Levels component package.

Importing this package will automatically register the Dash layout function and callbacks so that the main application only needs to import `components.sea_levels` and call `get_layout()` to include this section in the app.
"""

from .layout import create_sea_levels_layout as get_layout  # re-export for convenience

# Import callbacks to ensure they are registered with Dash on package import
from . import callbacks  # noqa: F401  # Side-effect import to register callbacks
