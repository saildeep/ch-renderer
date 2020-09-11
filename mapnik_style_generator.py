import json
import xml.etree.ElementTree as ET
from typing import List, Tuple
from xml.dom import minidom
import math

from chparser import Edge, CH


def divide_chunks(l:List, n:int):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

class MapnikStyle:
    def __init__(self,max_level = 18):
        self.main_map = ET.Element('Map', {"background-color": "transparent", "srs": "+proj=longlat +datum=WGS84"})

        self.max_level = max_level

        self.__open_file_handlers = []

        self._file_index = 0

    def level_to_scale(self,zoomlevel):
        osm_factor = (20026376.39 / 180.0)  # due to strange coordinate system
        return osm_factor * float(559082264 / 2 ** zoomlevel)


    def declareGEOJsonSource(self,filename,stylename,layername,cache_features=True,encoding='utf-8'):
        layer = ET.Element("Layer", {"name": layername})

        style_name = ET.Element("StyleName")
        style_name.text = stylename
        ds = ET.Element("Datasource")
        ds_type = ET.Element("Parameter", {"name": "type"})
        ds_type.text = "geojson"
        file = ET.Element("Parameter", {"name": "file"})
        file.text = "./" + filename

        cache_features_element = ET.Element("Parameter",{"name":"cache_features"})
        cache_features_element.text = "true" if cache_features else "false"

        encoding_element = ET.Element("Parameter",{"name":"encoding"})
        encoding_element.text = encoding


        ds.append(ds_type)
        ds.append(file)
        ds.append(cache_features_element)
        ds.append(encoding_element)

        layer.append(style_name)
        layer.append(ds)

        self.main_map.append(layer)



    def write_json(self,lines,filename):
        out_data = {
            "type": "FeatureCollection",
            "features": list(map(lambda line:
                {
                    "type": "Feature",

                    "geometry": {
                        "type": "LineString",
                        "coordinates": line
                    },


                },lines))

        }

        handler =  open(filename, 'w', buffering=10 ** 8, encoding='utf-8')
        print("Writing {} edges to {}".format(len(lines),filename))
        json.dump(out_data, handler, check_circular=False, indent="\t")
        self.__open_file_handlers.append(handler)


    def add_unbound_layer(self,edges):
        layername = "layer-unbound"
        stylename ="style-unbound"
        filename ="data.geojson"

        self.declareGEOJsonSource(filename,stylename,layername)
        self.write_json(edges,filename)
        style = ET.Element("Style",{"name":stylename})
        rule =ET.Element("Rule")
        line_sym = ET.Element("LineSymbolizer", {"stroke": "black", "stroke-width": str(3)})
        rule.append(line_sym)
        style.append(rule)
        self.main_map.append(style)


    def add_layers(self,lines,from_level:int,to_level:int,max_elements=10000):
        ratio = float(to_level) / float(self.max_level)

        color = "rgb({0:d},{1:d},{2:d})".format(int(ratio * 255.0), 0, int(255.0 * (1.0 - ratio)))

        self.add_layers_with_ranges(lines,[(from_level,to_level)],color,max_elements=max_elements)


    def add_layers_with_ranges(self,lines,ranges:List[Tuple[int,int]],color,max_elements = 100000):
        rules = []
        for from_level,to_level in ranges:
            rules.append(self._get_rule(from_level,to_level,color))


        for i,d in enumerate(divide_chunks(lines,max_elements)):
            self._add_layers(d,rules)


    def _get_rule(self,from_level,to_level,color):
        rule = ET.Element("Rule")
        max_scale = ET.Element("MaxScaleDenominator")
        max_scale.text = str(math.floor(self.level_to_scale(from_level)))
        min_scale = ET.Element("MinScaleDenominator")
        min_scale.text = str(math.ceil(self.level_to_scale(to_level)))
        line_sym = ET.Element("LineSymbolizer", {"stroke": color, "stroke-width": str(3)})

        if to_level < self.max_level:
            rule.append(min_scale)

        if from_level > 0:
            rule.append(max_scale)
        rule.append(line_sym)
        return rule

    def _add_layers(self,lines,rules):



        index = self._file_index
        layername = "layer-{}".format(index)
        stylename = "style-{}".format(index)
        filename =  "data-{}.geojson".format(index)
        self._file_index +=1


        style = ET.Element("Style", {"name": stylename})

        for rule in rules:
            style.append(rule)

        self.main_map.append(style)


        self.declareGEOJsonSource(filename,stylename,layername)



        self.write_json(lines,filename)



    @property
    def xml(self):
        flat_xml = ET.tostring(self.main_map, encoding="unicode")
        return minidom.parseString(flat_xml).toprettyxml("    ")


    def write(self):
        with open('mapnik.xml','w') as f:
            f.write(self.xml)
            f.flush()
        for h in self.__open_file_handlers:
            h.close()
        self.__open_file_handlers = []