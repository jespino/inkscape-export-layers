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

class write_file ():
    def __init__(self,path):
        self.datei = open(path + "export.txt", "w+")
    def write(self,text):
        #''.join(xs)
        if type(text) == "str":
            pass
        elif type(text) == "int":
            text = str(text)
        elif type(text) == "list":
            text = "".join(text)
        self.datei.write (str(text))
        self.datei.write ("\n")

    def close (self):
        self.datei.close()


class PNGExport(inkex.Effect):
    def __init__(self):
        """init the effetc library and get options from gui"""
        inkex.Effect.__init__(self)
        self.arg_parser.add_argument("--path", action="store", type=str, dest="path", default="~/", help="")
        self.arg_parser.add_argument("--crop", action="store", type=inkex.Boolean, dest="crop", default=False)
        self.arg_parser.add_argument("--overwrite", action="store", type=inkex.Boolean, dest="overwrite", default=True)
        self.arg_parser.add_argument("--dpi", action="store", type=float, dest="dpi", default=90.0)

    def effect(self):

        output_path = os.path.expanduser(self.options.path)
        self.file = write_file(output_path)
        self.file.write("#")
        curfile = self.options.input_file
        layers = self.get_layers(curfile)

        if not os.path.exists(os.path.join(output_path)):
            os.makedirs(os.path.join(output_path))
        layers_to_export = []
        for i in range(len(layers)):
            for ii in range(len(layers)-i-1,-1,-1): # find background
                if layers[ii][2] == "background":
                    background = layers[ii]
                    for ii in range(len(layers)-i-1,-1,-1): # find fixed
                        if layers[ii][2] == "fixed":
                            fixed = layers[ii]
                            for ii in range(len(layers)-i-1,-1,-1): # find export
                                if layers[ii][2] == "export":
                                    export = layers[ii]
                                    if [ background , fixed , export] in layers_to_export:
                                        pass
                                    else:
                                        layers_to_export.append([ background , fixed , export])
        self.file.write("overwrite")
        self.file.write(self.options.overwrite)
        for layer in layers_to_export:
            layer_label = layer[2][1] + "_" + layer[1][1]
            show_layer_ids = layer[0] + layer[1] + layer[2]
            layer_dest_png_path = os.path.join(output_path,  layer_label + ".png")
            self.file.write (layer_dest_png_path)
            self.file.write (os.path.isfile(layer_dest_png_path))

            if os.path.isfile(layer_dest_png_path) == True:
                if self.options.overwrite == True:
                    self.file.write ("make")
                    with _make_temp_directory() as tmp_dir:
                        layer_dest_svg_path = os.path.join(tmp_dir, "export.svg")
                        self.export_layers(layer_dest_svg_path, show_layer_ids)

                        layer_dest_png_path = os.path.join(output_path,  layer_label + ".png")
                        self.exportToPng(layer_dest_svg_path, layer_dest_png_path)
            else:
                self.file.write ("make")
                with _make_temp_directory() as tmp_dir:
                    layer_dest_svg_path = os.path.join(tmp_dir, "export.svg")
                    self.export_layers(layer_dest_svg_path, show_layer_ids)

                    layer_dest_png_path = os.path.join(output_path,  layer_label + ".png")
                    self.exportToPng(layer_dest_svg_path, layer_dest_png_path)

    def export_layers(self, dest, show):
        """
        Export selected layers of SVG to the file `dest`.
        :arg  str   dest:  path to export SVG file.
        :arg  list  hide:  layers to hide. each element is a string.
        :arg  list  show:  layers to show. each element is a string.
        """
        doc = copy.deepcopy(self.document)
        #self.file.write(type(doc))
        for layer in doc.xpath('//svg:g[@inkscape:groupmode="layer"]', namespaces=inkex.NSS):
            layer.attrib['style'] = 'display:none'
            label_attrib_name = "{%s}label" % layer.nsmap['inkscape']
            id = layer.attrib["id"]
            if id in show or "[show]" in layer.attrib[label_attrib_name]:
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
            elif layer_label.lower().startswith("[background] "):
                layer_type = "background"
                layer_label = layer_label[13:]
            else:
                continue

            layers.append([layer_id, layer_label, layer_type])

        return layers

    def exportToPng(self, svg_path, output_path):
        area_param = '-D' if self.options.crop else '-C'
        command = "inkscape %s -d %s --export-filename \"%s\" \"%s\"" % (area_param, self.options.dpi, output_path, svg_path)
        self.file.write (command)
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        p.wait()

@contextlib.contextmanager
def _make_temp_directory():
    temp_dir = tempfile.mkdtemp(prefix="tmp-inkscape")
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


def _main():
    e = PNGExport()
    e.run()
    exit()

if __name__ == "__main__":
    _main()
