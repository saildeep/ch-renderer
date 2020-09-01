
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

    @property
    def mapnik_coordinate(self):
        return tranformer.transform(self.lat,self.lng)



class Edge(object):
    def __init__(self, id, src_id, target_id, cost, skip1, skip2):
        self.id = id
        self.src_id = src_id
        self.target_id = target_id
        self.cost = cost
        self.skip1 = skip1
        self.skip2 = skip2

    def __str__(self):
        return "Edge {0}:{1}->{2}@{3}$, skipping {4},{5} ".format(self.id,self.src_id,self.target_id,self.cost,self.skip1,self.skip2)


class CH:
    def __init__(self, vertices: List[Vertex], edges: List[Edge]):
        self.vertices = vertices
        self.edges = edges

    def get_vertex(self,id):
        return self.vertices[id]


def parse_file(filepath):
    with open(filepath) as file:
        num_vertices = int(file.readline(1000000))
        num_edges = int(file.readline(100000))

        vertices = []
        for i in range(num_vertices):
            vvertex = file.readline(10000)
            parsed_vertex = vvertex.split(" ")
            vertex = Vertex(i, int(parsed_vertex[0]), float(parsed_vertex[1]), float(parsed_vertex[2]))

            vertices.append(vertex)
        edges = []
        for i in range(num_edges):
            vedge = file.readline(100000)
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

        return CH(vertices, edges)
