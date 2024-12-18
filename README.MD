# [DEPRECATED] Inkscape Export Layers

**⚠️ This project is no longer actively maintained ⚠️**

Please use the more modern and actively maintained fork at: https://github.com/dmitry-t/inkscape-export-layers

The new version includes:
- Support for Inkscape version 1.0+
- Additional export formats (PDF, SVG)
- Progressive reveal option for presentations
- Better error handling and diagnostics
- Active maintenance and bug fixes

## Original Description

This was an Inkscape extension to export SVG layers as (JPG, PNG) images. The exported images could be combined from multiple layers.

## Installation

### Automatic Installation
Run the install script:
```bash
chmod +x install.sh
./install.sh
```

### Manual Installation
Copy `export_layers.py` and `export_layers.inx` to your Inkscape extensions directory:
- Linux: `~/.config/inkscape/extensions/`
- Windows: `%APPDATA%\inkscape\extensions\`
- MacOS: `$HOME/.config/inkscape/extensions/`

## How it works
To export your Inkscape file as an image open an inkscape file with multiple layers (otherwise you can simply use the in-built export tool 'Ctrl + E').

There are two options for your layers when exporting:
- **Fixed**: If a layer label starts with "[fixed]"" this layer will always be exported and combined with other layers. It is very useful for backgrounds or fixed elements.
-  **Export**: If a layer label starts with "[export]" this layer will be exported along with any [Fixed] layer and combined in a single image.

Check this example:

![Layer export example](http://i.imgur.com/StUpSd1.png)

The layer **[fixed] background** is a fixed layer and will always be exported combined with the **[export]** layers.

If could make this export, we will get two images: the combination of background + version1 and background + version2

## Using it
To use the extension once your layers are ready:

1. Go to **Extensions > Export > Export layers**
2. Choose the path you want to save your file to (inkscape does not allow to use a file explorer, sorry)
3. Choose the format of your export (JPG, PNG)
