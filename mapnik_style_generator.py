import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import math

class MapnikStyle:
    def __init__(self,max_level = 18):
        self.main_map = ET.Element('Map', {"background-color": "transparent", "srs": "+proj=longlat +datum=WGS84"})

        self.max_level = max_level


    def level_to_scale(self,zoomlevel):
        osm_factor = (20026376.39 / 180.0)  # due to strange coordinate system
        return osm_factor * float(559082264 / 2 ** zoomlevel)

    def add_layer(self,geojson_content,from_level:int,to_level:int):
        assert from_level >= 0
        assert to_level >= 0
        assert  to_level>from_level

        layername = "layer-{}-to-{}".format(from_level,to_level)
        stylename = "style-{}-to-{}".format(from_level,to_level)
        filename =  "data-{}-to-{}.geojson".format(from_level,to_level)

        ratio = math.sqrt( float(to_level) / float(self.max_level))
        color = "rgb({0:d},{1:d},{2:d})".format(
            int(ratio * 255.0), 0, int(255.0 * (1.0 - ratio)))

        style = ET.Element("Style", {"name": stylename})
        for zoom_level in range(from_level,to_level):
            max_v = self.level_to_scale(zoom_level)
            min_v = self.level_to_scale(zoom_level+1)
            target_level_difference = (to_level - zoom_level) -1 # how many layers we are away from the best fitting layer
            stroke_width = max(1,5-target_level_difference)

            line_sym = ET.Element("LineSymbolizer", {"stroke": color, "stroke-width": str(stroke_width)})
            max_scale = ET.Element("MaxScaleDenominator")
            max_scale.text = str(max_v)
            min_scale = ET.Element("MinScaleDenominator")
            min_scale.text = str(min_v)


            rule = ET.Element("Rule")
            rule.append(line_sym)
            rule.append(max_scale)
            if zoom_level+1 < self.max_level:
                rule.append(min_scale)

            style.append(rule)
        self.main_map.append(style)

        layer = ET.Element("Layer", {"name": layername})

        style_name = ET.Element("StyleName")
        style_name.text = stylename
        ds = ET.Element("Datasource")
        ds_type = ET.Element("Parameter", {"name": "type"})
        ds_type.text = "geojson"
        file = ET.Element("Parameter", {"name": "file"})
        file.text = "./" + filename

        ds.append(ds_type)
        ds.append(file)

        layer.append(style_name)
        layer.append(ds)
        self.main_map.append(layer)

        with open(filename,'w',buffering=10**7) as f:
            print("Writing {}".format(filename))
            json.dump(geojson_content,f,check_circular=False)


    @property
    def xml(self):
        flat_xml = ET.tostring(self.main_map, encoding="unicode")
        return minidom.parseString(flat_xml).toprettyxml("    ")


    def write(self):
        with open('mapnik.xml','w') as f:
            f.write(self.xml)
            f.flush()