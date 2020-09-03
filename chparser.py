
from typing import List

 #do this as mapnik expects to coordinates in epsg 3857 form some weird reason
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




    def get_vertex(self,id):
        if id < 0 :
            return None
        return self.vertices[id]

    def get_edge(self,id):
        if id < 0 :
            return None
        return self.edges[id]

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
