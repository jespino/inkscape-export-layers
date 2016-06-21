# Inkscape Export Layers

Inkscape extension to export SVG layers as (JPG, PNG) images. The exported images can be a combination of multiple layers.

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
