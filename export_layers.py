#! /usr/bin/env python

import sys
sys.path.append('/usr/share/inkscape/extensions')
import contextlib
import inkex
import os
import subprocess
import tempfile
import shutil
import copy 

def log(string):
    return
    f = open("D:\\test\\log.txt", "a")
    f.write(string + "\n")
    f.close()        

def isTrueString(string):
    if 'FALSE'.startswith(str(string).upper()):
        return False
    else:
        return True    

class PNGExport(inkex.Effect):
    def __init__(self):
        """init the effect library and get options from gui"""
        inkex.Effect.__init__(self)
        self.arg_parser.add_argument("--path", action="store", type=str, dest="path", default="~/", help="")
        self.arg_parser.add_argument('--f', '--filetype', action='store', type=str, dest='filetype', default='jpeg', help='Exported file type')
        self.arg_parser.add_argument("--crop", action="store", type=str, dest="crop", default="false")
        self.arg_parser.add_argument("--dpi", action="store", type=float, dest="dpi", default=90.0)

    def effect(self):        
        output_path = os.path.expanduser(self.options.path)
        curfile = self.options.input_file
        layers = self.get_layers(curfile)
        counter = 1

        for (layer_id, layer_label, layer_type) in layers:
            if layer_type == "fixed":
                continue

            show_layer_ids = [layer[0] for layer in layers if layer[2] == "fixed" or layer[0] == layer_id]

            if not os.path.exists(os.path.join(output_path)):
                os.makedirs(os.path.join(output_path))

            with _make_temp_directory() as tmp_dir:
                layer_dest_svg_path = os.path.join(tmp_dir, "export.svg")
                self.export_layers(layer_dest_svg_path, show_layer_ids)

                if self.options.filetype == "jpeg":
                    layer_dest_png_path = os.path.join(output_path, "%s_%s.%s" % (str(counter).zfill(3), layer_label, "png"))
                    self.exportToPNG(layer_dest_svg_path, layer_dest_png_path)   
                    self.convertPngToJpg(layer_dest_png_path, layer_dest_png_path.replace(".png", ".jpg"))
                else:
                    layer_dest_png_path = os.path.join(output_path, "%s_%s.%s" % (str(counter).zfill(3), layer_label, "png"))
                    self.exportToPNG(layer_dest_svg_path, layer_dest_png_path)



            counter += 1

    def export_layers(self, dest, show):
        """
        Export selected layers of SVG to the file `dest`.
        :arg  str   dest:  path to export SVG file.
        :arg  list  hide:  layers to hide. each element is a string.
        :arg  list  show:  layers to show. each element is a string.
        """
        doc = copy.deepcopy(self.document)
        for layer in doc.xpath('//svg:g[@inkscape:groupmode="layer"]', namespaces=inkex.NSS):
            layer.attrib['style'] = 'display:none'
            id = layer.attrib["id"]
            if id in show:
                layer.attrib['style'] = 'display:inline'

        doc.write(dest)

    def get_layers(self, src):
        svg_layers = self.document.xpath('//svg:g[@inkscape:groupmode="layer"]', namespaces=inkex.NSS)
        layers = []

        for layer in svg_layers:
            label_attrib_name = "{%s}label" % layer.nsmap['inkscape']
            if label_attrib_name not in layer.attrib:
                continue

            layer_id = layer.attrib["id"]
            layer_label = layer.attrib[label_attrib_name]

            if layer_label.lower().startswith("[fixed] "):
                layer_type = "fixed"
                layer_label = layer_label[8:]
            elif layer_label.lower().startswith("[export] "):
                layer_type = "export"
                layer_label = layer_label[9:]
            else:
                continue
            layers.append([layer_id, layer_label, layer_type])

        return layers

    def exportToPNG(self, svg_path, output_path):
        if isTrueString(self.options.crop):
            cropStyle = "--export-area-page"
        else:
            cropStyle =  "--export-area-drawing"
        command = [
            "inkscape",
            svg_path.encode("utf-8"),
            cropStyle,
            "--export-dpi", str(self.options.dpi),
            "--export-filename", output_path.encode("utf-8"),
            "--export-type=png"
        ]
        log(str(command))
        p = subprocess.Popen(command)
        p.wait()

    def convertPngToJpg(self, png_path, output_path):
        command = ("convert \"%s\" \"%s\"" % (png_path, output_path)).encode("utf-8")
        log(str(command))
        try:
            p = subprocess.Popen(command)            
            p.wait()
        except FileNotFoundError as e:
            import ctypes            
            ctypes.windll.user32.MessageBoxW(0, "ImageMagick is required to convert PNG to JPG.", "ImageMagick not found", 16)


@contextlib.contextmanager
def _make_temp_directory():
    temp_dir = tempfile.mkdtemp(prefix="tmp-inkscape")
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)

def _main():
    e = PNGExport()
    e.run(output = False)
    exit()

if __name__ == "__main__":
    _main()
