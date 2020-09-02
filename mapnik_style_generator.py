import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

class MapnikStyle:
    def __init__(self,max_level = 20):
        self.main_map = ET.Element('Map', {"background-color": "transparent", "srs": "+proj=longlat +datum=WGS84"})

        self.max_level = max_level


    def add_layer(self,geojson_content,from_level:int,to_level:int):
        assert from_level >= 0
        assert to_level >= 0
        assert  to_level>from_level
        osm_factor = (20026376.39 / 180.0)  # due to strange coordinate system
        max_v = osm_factor * float(559082264 / 2 ** from_level)
        min_v = osm_factor * float(559082264 / 2 ** to_level)
        layername = "layer-{}-to-{}".format(from_level,to_level)
        stylename = "style-{}-to-{}".format(from_level,to_level)
        filename =  "data-{}-to-{}.geojson".format(from_level,to_level)

        ratio = float(from_level) / float(self.max_level)
        color = "rgb({0:d},{1:d},{2:d})".format(
            int(ratio * 255.0), int(127 + 120.0 * ratio), int(255.0 * (1.0 - ratio)))

        line_sym = ET.Element("LineSymbolizer", {"stroke": color, "stroke-width": "4"})
        max_scale = ET.Element("MaxScaleDenominator")
        max_scale.text = str(max_v)
        min_scale = ET.Element("MinScaleDenominator")
        min_scale.text = str(min_v)

        style = ET.Element("Style", {"name":stylename})
        rule = ET.Element("Rule")
        rule.append(line_sym)
        rule.append(max_scale)
        if to_level < self.max_level:
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

        with open(filename,'w') as f:
            print("Writing {}".format(filename))
            json.dump(geojson_content,f,check_circular=False)
            f.flush()

    @property
    def xml(self):
        flat_xml = ET.tostring(self.main_map, encoding="unicode")
        return minidom.parseString(flat_xml).toprettyxml("    ")


    def write(self):
        with open('mapnik.xml','w') as f:
            f.write(self.xml)
            f.flush()