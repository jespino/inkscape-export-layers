#! /usr/bin/env python

import sys
sys.path.append('/usr/share/inkscape/extensions')
import inkex
import os
import subprocess
import tempfile
import shutil
import copy


class PNGExport(inkex.Effect):
    def __init__(self):
        """init the effect library and get options from gui"""
        inkex.Effect.__init__(self)
        self.arg_parser.add_argument("--path", action="store", type=str, dest="path", default="~/", help="")
        self.arg_parser.add_argument('-f', '--filetype', action='store', type=str, dest='filetype', default='jpeg', help='Exported file type')
        self.arg_parser.add_argument("--crop", action="store", type=inkex.Boolean, dest="crop", default=False)
        self.arg_parser.add_argument("--dpi", action="store", type=float, dest="dpi", default=90.0)
        self.arg_parser.add_argument("--only_visible", action="store", type=inkex.Boolean, dest="only_visible", default=False)

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

            with tempfile.NamedTemporaryFile() as fp_svg:
                layer_dest_svg_path = fp_svg.name
                self.export_layers(layer_dest_svg_path, show_layer_ids)

                if self.options.filetype == "jpeg":
                    with tempfile.NamedTemporaryFile() as fp_png:
                        self.exportToPng(layer_dest_svg_path, fp_png.name)
                        layer_dest_jpg_path = os.path.join(output_path, "%s_%s.jpg" % (str(counter).zfill(3), layer_label))
                        self.convertPngToJpg(fp_png.name, layer_dest_jpg_path)
                else:
                    layer_dest_png_path = os.path.join(output_path, "%s_%s.png" % (str(counter).zfill(3), layer_label))
                    self.exportToPng(layer_dest_svg_path, layer_dest_png_path)

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

            # Check if layer is visible
            style = layer.get('style', '')
            is_visible = True
            if style is not None:
                is_visible = 'display:none' not in style

            if self.options.only_visible and not is_visible:
                continue

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

    def exportToPng(self, svg_path, output_path):
        area_param = '-D' if self.options.crop else 'C'
        command = "inkscape %s -d %s -e \"%s\" \"%s\"" % (area_param, self.options.dpi, output_path, svg_path)

        p = subprocess.Popen(command.encode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()

    def convertPngToJpg(self, png_path, output_path):
        command = "convert \"%s\" \"%s\"" % (png_path, output_path)
        p = subprocess.Popen(command.encode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()


def _main():
    e = PNGExport()
    e.run()
    exit()

if __name__ == "__main__":
    _main()
