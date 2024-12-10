#!/bin/bash

# Create Inkscape extensions directory if it doesn't exist
INKSCAPE_EXT_DIR="$HOME/.config/inkscape/extensions"
mkdir -p "$INKSCAPE_EXT_DIR"

# Copy extension files
cp export_layers.py "$INKSCAPE_EXT_DIR/"
cp export_layers.inx "$INKSCAPE_EXT_DIR/"

# Make Python script executable
chmod +x "$INKSCAPE_EXT_DIR/export_layers.py"

echo "Installation complete! The Export Layers extension should now appear in Inkscape under Extensions > Export > Export layers"
