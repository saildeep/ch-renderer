
import pickle
import os
import hashlib


from chparser import parse_file
from mapnik_style_generator import MapnikStyle, Colormapper

print("Started main.py")
mss = MapnikStyle()
file = os.environ.get('FILENAME','./ch.ftxt')

ch = parse_file(file)

data ={}
level_to_zoomlevel = lambda x:(mss.max_level-x)
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


num_levels = 12

hierarchy_small = ch.get_edge_hierarchy(num_levels,extend_childs=True)
hierarchy_compact = ch.bin_edges_from_hierarchy(hierarchy_small)

max_zoom = 18
cm = Colormapper(0,num_levels)
for levels_string,edges in hierarchy_compact.items():
    levels = list(map(int,levels_string.split("-")))
    lines = ch.make_edge_list(edges)
    ranges = list(map(lambda level:
                      (
                          (max_zoom-1)-level if level< num_levels-1 else 0 ,
                          max_zoom-level if level > 0 else mss.max_level
                      ),levels))
    colors = list(map(lambda x:cm(x),levels))
    mss.add_layers_with_ranges(lines,ranges,colors)


for i in range(num_levels):
    lines = ch.make_edge_list(hierarchy_small[i])
    from_zoomlevel = 17-i
    to_zoomlevel = 18-i
    if i == 0:
        to_zoomlevel = mss.max_level
    if i == num_levels -1:
        from_zoomlevel = 0


    #mss.add_layers(lines,from_zoomlevel,to_zoomlevel)

print("Finished categorizing vertices")


for (from_zoomlevel,to_zoomlevel),edge_collection in data.items():
    lines = ch.make_edge_list(edge_collection)
    #mss.add_layers(lines,from_zoomlevel,to_zoomlevel)
#mss.add_unbound_layer(ch.make_edge_list(filter(lambda x:x.level==0,ch.edges)))



mss.write()
