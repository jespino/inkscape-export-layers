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


class PNGExport(inkex.Effect):
    def __init__(self):
        """init the effetc library and get options from gui"""
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--path", action="store", type="string", dest="path", default="~/", help="")
        self.OptionParser.add_option('-f', '--filetype', action='store', type='string', dest='filetype', default='jpeg', help='Exported file type')
        self.OptionParser.add_option("--crop", action="store", type="inkbool", dest="crop", default=False)
        self.OptionParser.add_option("--dpi", action="store", type="float", dest="dpi", default=90.0)

    def effect(self):
        output_path = os.path.expanduser(self.options.path)
        curfile = self.args[-1]
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
                    tmp_dest_png_path = os.path.join(tmp_dir, "export.png")
                    self.exportToPng(layer_dest_svg_path, tmp_dest_png_path)
                    layer_dest_jpg_path = os.path.join(output_path, "%s_%s.jpg" % (str(counter).zfill(3), layer_label))
                    self.convertPngToJpg(tmp_dest_png_path, layer_dest_jpg_path)
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
        command = [
            "inkscape",
            "-D" if self.options.crop else "-C",
            "-d", str(self.options.dpi),
            "-e", output_path.encode("utf-8"),
            svg_path.encode("utf-8")
        ]
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        p.wait()

    def convertPngToJpg(self, png_path, output_path):
        command = "convert \"%s\" \"%s\"" % (png_path, output_path)
        p = subprocess.Popen(command.encode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
    e.affect(output=False)


if __name__ == "__main__":
    _main()
