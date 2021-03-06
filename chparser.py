
from typing import List

 #do this as mapnik expects to coordinates in epsg 3857 form some weird reason
import math
from pyproj import Proj, Transformer

wgs84 = Proj('epsg:4326')
mapnik_proj = Proj("epsg:3857")
tranformer = Transformer.from_proj(wgs84,mapnik_proj)

class Vertex:
    def __init__(self, id, label, lat, lng):
        self.id = id
        self.label = label
        self.lat = lat
        self.lng = lng
        self.mapnik_coordinate = tranformer.transform(self.lat,self.lng)



class Edge(object):
    def __init__(self, id, src_id, target_id, cost, skip1, skip2):
        self.id = id
        self.src_id = src_id
        self.target_id = target_id
        self.cost = cost
        self.skip1 = skip1
        self.skip2 = skip2
        self.replaced_by = -1
        self.level = -1
        self.normalized_level = -1


    def __str__(self):
        return "Edge {0}:{1}->{2}@{3}$, skipping {4},{5} ".format(self.id,self.src_id,self.target_id,self.cost,self.skip1,self.skip2)


class CH:
    def __init__(self, vertices: List[Vertex], edges: List[Edge]):
        self.vertices = vertices
        self.edges = edges
        self.max_level = 0
        self.__compute_edge_levels()
        self.__compute_vertex_labels()
        print("Max level at ch {}".format(self.max_level))


    def __compute_edge_levels(self):
        print("Computing edge levels")
        open_list = list(range(len(self.edges)))
        new_open_list = []
        while len(open_list) > 0:
            for ie in open_list:
                e = self.edges[ie]
                if e.skip1 == -1 and e.skip2 == -1:
                    e.level = 0
                    continue
                s1 = self.edges[e.skip1]
                s2 = self.edges[e.skip2]
                if s1.level >= 0 and s2.level >=0:
                    s1.replaced_by = ie
                    s2.replaced_by = ie
                    e.level = max(s1.level,s2.level)+1
                    self.max_level = max(e.level,self.max_level)
                    continue
                new_open_list.append(ie)
            open_list = new_open_list

        f_max_level = float(self.max_level)
        for edge in self.edges:
            edge.normalized_level = float(edge.level )/ f_max_level


    def __compute_vertex_labels(self):
        self.__min_label = 10000000
        self.__max_label = -10000000
        labels = []
        for v in self.vertices:
            self.__min_label = min(v.label,self.__min_label)
            self.__max_label= max(v.label,self.__max_label)
            labels.append(v.label)





    def get_vertex(self,id):
        if id < 0 :
            return None
        return self.vertices[id]

    def get_edge(self,id):
        if id < 0 :
            return None
        return self.edges[id]


    def get_vertex_hierarchy(self,num_levels):
        # level 0 is all visible

        hier = list(map(lambda x: [], range(num_levels)))
        leafes = list(filter(lambda x:x.skip1==-1 and x.skip2==-1, self.edges))

        for l in range(num_levels):

            scale_fn = lambda x:math.log(x+.00001,2)
            normed_level = (float(l) / float(num_levels))
            normed_scaled_level = (scale_fn(normed_level) - scale_fn(0))/(scale_fn(1)- scale_fn(0))

            th = normed_scaled_level * self.__max_label
            print("NSL:", normed_scaled_level, "TH:",th)
            edges = hier[l]
            for e in leafes:


                v1 = self.get_vertex(e.src_id)
                v2 = self.get_vertex(e.target_id)
                if v1.label >= th or v2.label >= th:
                    edges.append(e)


        return hier

    def get_leaf_edges(self,edge:Edge):
        if edge.skip1 == -1:
            assert edge.skip2 == -1
            yield edge
            return
        for e in self.get_leaf_edges(self.get_edge(edge.skip1)):
            yield e
        for e in self.get_leaf_edges(self.get_edge(edge.skip2)):
            yield e


    def get_edge_hierarchy(self,num_levels,extend_childs=False):
        norm_to_level = lambda x:math.floor(x*(num_levels-1))
        get_level = lambda x:norm_to_level(x.normalized_level)
        hier = list(map(lambda x:[],range(num_levels)))


        for e in self.edges:
            # in case of most bottom part
            if e.skip1 == -1:
                assert e.skip2 == -1
                hier[0].append(e)
                continue

            edge_level = get_level(e)
            child1 = self.edges[e.skip1]
            child2 = self.edges[e.skip2]

            child1_level = get_level(child1)
            child2_level = get_level(child2)
            if child1_level< edge_level and child2_level < edge_level:
                hier[edge_level].append(e)

            # somewhat experimental skip prevention
            for child,child_level in [(child1,child1_level),(child2,child2_level)]:
                for add_to_level in range(child_level +1, edge_level):
                    hier[add_to_level].append(child)



        if extend_childs:
            new_hier = list(map(lambda x:[],range(num_levels)))
            for hier_level_index,hier_level in enumerate(hier):
                use_edges = {}
                for e in hier_level:
                    for leave in self.get_leaf_edges(e):
                        use_edges[leave.id] = leave
                new_hier[hier_level_index] = use_edges.values()

            hier = new_hier




        return hier


    def bin_edges_from_hierarchy(self,hier:List[List['Edge']]):


        edgeid_to_contained_levels = {}

        for hier_level_index,level_elements in enumerate(hier):
            for element in level_elements:
                eid = element.id
                levels =  edgeid_to_contained_levels.get(eid,[])
                if hier_level_index not in levels:
                    levels.append(hier_level_index)
                edgeid_to_contained_levels[eid] = levels


        layers = {}
        for edge_id,levels in edgeid_to_contained_levels.items():
            edge = self.get_edge(edge_id)
            levels_sorted = map(str,sorted(levels))
            levels_index = '-'.join(levels_sorted)
            x = layers.get(levels_index,[])
            x.append(edge)
            layers[levels_index] = x
        return layers








    def make_edge_list(self,edge_collection):
        return list(map(lambda edge: [
            self.get_vertex(edge.src_id).mapnik_coordinate,
            self.get_vertex(edge.target_id).mapnik_coordinate], edge_collection))

def parse_file(filepath):
    print("Starting parsing " + filepath)
    with open(filepath,'r',buffering=1000000) as file:
        print("Loading "+ filepath)
        num_vertices = int(file.readline(1000))
        num_edges = int(file.readline(1000))

        vertices = []
        print("Starting parsing {0} vertices and {1} edges".format(num_vertices,num_edges))
        for i in range(num_vertices):
            vvertex = file.readline(400)
            parsed_vertex = vvertex.split(" ")
            vertex = Vertex(i, int(parsed_vertex[0]), float(parsed_vertex[1]), float(parsed_vertex[2]))

            vertices.append(vertex)
        edges = []

        print("Parsed vertices")
        for i in range(num_edges):
            vedge = file.readline(400)
            parsed_edge = vedge.split(" ")
            assert i == int(parsed_edge[0])
            edge = Edge(
                i,
                int(parsed_edge[1]),
                int(parsed_edge[2]),
                int(parsed_edge[3]),
                int(parsed_edge[4]),
                int(parsed_edge[5])
            )
            edges.append(edge)
        print("Parsed edges")
        return CH(vertices, edges)
