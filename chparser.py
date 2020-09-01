from typing import List


class Vertex:
    def __init__(self, id, label, lat, lng):
        self.id = id
        self.label = label
        self.lat = lat
        self.lng = lng


class Edge(object):
    def __init__(self, id, src_id, target_id, cost, skip1, skip2):
        self.id = id
        self.src_id = src_id
        self.target_id = target_id
        self.cost = cost
        self.skip1 = skip1
        self.skip2 = skip2


class CH:
    def __init__(self, vertices: List[Vertex], edges: List[Edge]):
        self.vertices = vertices
        self.edges = edges


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
