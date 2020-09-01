import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

from chparser import parse_file


num_zoom_levels = 20

def generate_stylexml(zoomlevel_list):
    main_map = ET.Element('Map', {"background-color": "transparent", "srs": "+proj=longlat +datum=WGS84"})



    for zoom_level in zoomlevel_list:
        osm_factor = ( 20026376.39 / 180.0) # due to strange coordinate system

        scale = osm_factor * float(559082264 / 2**zoom_level)
        max_v = scale
        min_v = scale / 4

        ratio = float(zoom_level) / float(num_zoom_levels)
        color = "rgb({0:d},{1:d},{2:d})".format(
            int(ratio * 255.0),int(127+120.0*ratio),int(255.0*(1.0-ratio)))

        line_sym = ET.Element("LineSymbolizer",{"stroke":color,"stroke-width":"4"})

        max_scale = ET.Element("MaxScaleDenominator")
        max_scale.text = str(max_v)

        min_scale = ET.Element("MinScaleDenominator")
        min_scale.text = str(min_v)


        style = ET.Element("Style",{"name":"style-{}".format(zoom_level)})
        rule = ET.Element("Rule")
        rule.append(line_sym)

        rule.append(max_scale)
        rule.append(min_scale)

        style.append(rule)
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

    flat_xml = ET.tostring(main_map,encoding="unicode")
    return minidom.parseString(flat_xml).toprettyxml("    ")





ch = parse_file('./ch-bremen.ftxt')

data =list( map(lambda x:[], list(range(num_zoom_levels))))
for e in ch.edges:
    zoomlevel = 15-e.level
    if zoomlevel < 0:
        continue

    from_coord = ch.get_vertex(e.src_id).mapnik_coordinate
    to_coord = ch.get_vertex(e.target_id).mapnik_coordinate
    data[zoomlevel].append([from_coord,to_coord])

used_zoom_levels = []
for i in range(num_zoom_levels):
    if len(data[i]) > 0:
        used_zoom_levels.append(i)
        out_data = {
                "type":"FeatureCollection",
                "features":list(map(lambda x:
                    {
                        "type":"Feature",

                        "geometry":{
                            "type":"LineString",
                            "coordinates":x
                        }


                     }
                ,data[i]))
            }
        with open("{0}.geojson".format(i),'w') as f:
            json.dump(out_data,f,check_circular=False)
            f.flush()

with open('mapnik.xml','w') as f:
    s = generate_stylexml(used_zoom_levels)
    f.write(s)
pass


