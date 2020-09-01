import xml.etree.ElementTree as ET
from xml.dom import minidom

from pyproj import transform,Proj, Transformer


map = ET.Element('Map',{"background-color":"transparent","srs":"+proj=longlat+datum=WGS84"})

def generate_stylexml():
    for zoom_level in range(21):
        scale = int(559082264 / 2**zoom_level)
        min_v = 0
        max_v = scale

        line_sym = ET.Element("LineSymbolizer",{"stroke":"green","stroke-width":"4"})
        min_scale = ET.Element("MinScaleDenominator")
        max_scale = ET.Element("MaxScaleDenominator")
        min_scale.text = str(min_v)
        max_scale.text = str(max_v)

        style = ET.Element("Style",{"name":"style-{}".format(zoom_level)})
        style.append(line_sym)
        style.append(min_scale)
        style.append(max_scale)
        map.append(style)


        layer = ET.Element("Layer",{"name":"layer-{}".format(zoom_level)})

        style_name = ET.Element("StyleName")
        style_name.text = "style-{}".format(zoom_level)
        ds = ET.Element("Datasource")
        type = ET.Element("Parameter",{"name":"type"})
        type.text="geojson"
        file = ET.Element("Parameter",{"name":"file"})
        file.text="./{}.geojson".format(zoom_level)

        ds.append(type)
        ds.append(file)

        layer.append(style_name)
        layer.append(ds)
        map.append(layer)

    return minidom.parseString(ET.tostring(map)).toprettyxml(indent="    ")


with open('mapnik.xml','w') as f:
    s = generate_stylexml()
    f.write(s)


 #do this as mapnik expects to coordinates in epsg 3857 form some weird reason
wgs84 = Proj('epsg:4326')
mapnik_proj = Proj("epsg:3857")
Transformer.from_proj(wgs84,mapnik_proj)