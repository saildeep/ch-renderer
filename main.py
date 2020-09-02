import json

from chparser import parse_file
from mapnik_style_generator import MapnikStyle


mss = MapnikStyle()
ch = parse_file('./ch.ftxt')
print("Finished parsing CH")

data ={}
level_to_zoomlevel = lambda x:mss.max_level-x
for e in ch.edges:
    replaced_by = ch.get_edge(e.replaced_by)
    this_level = e.level
    next_level = 1000000000
    # workaround for root node
    if replaced_by is not None:
        next_level = replaced_by.level
    from_zoomlevel = level_to_zoomlevel(next_level)
    to_zoomlevel = level_to_zoomlevel(this_level)

    if from_zoomlevel < 0 or to_zoomlevel<0:
        continue

    assert to_zoomlevel>from_zoomlevel

    key = (from_zoomlevel,to_zoomlevel)
    edge_collection = data.get(key,[])
    edge_collection.append(e)
    data[key] = edge_collection



print("Finished categorizing vertices")

used_zoom_levels = []
for (from_zoomlevel,to_zoomlevel),edge_collection in data.items():


    out_data = {
            "type":"FeatureCollection",
            "features":list(map(lambda edge:
                {
                    "type":"Feature",

                    "geometry":{
                        "type":"LineString",
                        "coordinates":[
                            ch.get_vertex(edge.src_id).mapnik_coordinate,
                            ch.get_vertex(edge.target_id).mapnik_coordinate]
                    }


                 }
            ,edge_collection))
        }
    mss.add_layer(out_data,from_zoomlevel,to_zoomlevel)


mss.write()
