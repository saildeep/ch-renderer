import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

from chparser import parse_file


num_zoom_levels = 20

def generate_stylexml(zoomlevel_list):
    main_map = ET.Element('Map', {"background-color": "transparent", "srs": "+proj=longlat+datum=WGS84"})
    for zoom_level in zoomlevel_list:
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
        main_map.append(style)


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
        main_map.append(layer)

    return minidom.parseString(ET.tostring(main_map)).toprettyxml(indent="    ")





ch = parse_file('./ch-bremen.ftxt')

data =list( map(lambda x:[], list(range(num_zoom_levels))))
for e in ch.edges:
    if e.skip1 == -1 and e.skip2 == -1:
        from_coord = ch.get_vertex(e.src_id).mapnik_coordinate
        to_coord = ch.get_vertex(e.target_id).mapnik_coordinate
        data[0].append([from_coord,to_coord])

used_zoom_levels = []
for i in range(num_zoom_levels):
    if len(data[i]) > 0:
        used_zoom_levels.append(i)
        out_data = {
                "type":"FeatureCollection",
                "features":[
                    {
                        "type":"Feature",

                        "geometry":{
                            "type":"MultiLineString",
                            "coordinates":data[i]
                        }


                     }
                ]
            }
        with open("{0}.geojson".format(i),'w') as f:
            json.dump(out_data,f,check_circular=False)
            f.flush()

with open('mapnik.xml','w') as f:
    s = generate_stylexml(used_zoom_levels)
    f.write(s)
pass


