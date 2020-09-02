
import pickle
import os

from chparser import parse_file
from mapnik_style_generator import MapnikStyle

print("Started main.py")
mss = MapnikStyle()
cache_file = "./cached_graph.pckl"
if os.path.exists(cache_file):
    with open(cache_file,'rb') as f:
        ch = pickle.load(f)
else:
    ch = parse_file('./ch.ftxt')
    with open(cache_file,'wb') as f:
        pickle.dump(ch,f)
print("Finished parsing CH")

data ={}
level_to_zoomlevel = lambda x:(mss.max_level-x)-1
for e in ch.edges:
    replaced_by = ch.get_edge(e.replaced_by)
    this_level = e.level
    next_level = 1000000000
    # workaround for root node
    if replaced_by is not None:
        next_level = replaced_by.level
    from_zoomlevel = level_to_zoomlevel(next_level)
    to_zoomlevel = level_to_zoomlevel(this_level)

    if to_zoomlevel <1:
        continue

    if from_zoomlevel < 0:
        from_zoomlevel = 0

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
