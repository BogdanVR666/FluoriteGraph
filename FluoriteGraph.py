from dataclasses import dataclass, field
from collections.abc import Iterable
from itertools import count

_counter = count(1)


@dataclass(slots=True)
class NodeType:
    @dataclass(frozen=True, slots=True)
    class Node:
        name: str
        description: str | None
        node_id: int = field(default_factory=lambda: next(_counter))

        def __repr__(self):
            name = self.name
            description = f", {self.description}," if self.description else ""
            return f"Node({name=}{description})"

    name: str
    nodes: dict[int, Node] = field(default_factory=dict)

    def append(self, name, description=None):
        node = self.Node(name, description)
        self.nodes[node.node_id] = node

    def extend(self, nodes: Iterable[Iterable[str]]):
        for node in nodes:
            if isinstance(node, str):
                self.append(node)
            elif isinstance(node, Iterable) and len(node) == 2:
                self.append(node[0], node[1])
            else:
                raise ValueError("data must be 'str' or 'pair[str, str]'")

    def __getitem__(self, name):
        result = list()
        for node in self.nodes.values():
            if node.name == name:
                result.append(node)
        if len(result) == 1:
            return result[0]
        elif len(result):
            return result
        else:
            raise KeyError(f"Node with name {name} not found")


@dataclass(slots=True)
class EdgeType:
    @dataclass(frozen=True, slots=True)
    class Edge:
        node_in: NodeType.Node
        node_out: NodeType.Node
        description: str | None = None
        edge_id: int = field(default_factory=lambda: next(_counter))

        def __repr__(self):
            node_in = self.node_in
            node_out = self.node_out
            description = f", {self.description}," if self.description else ""
            return f"Edge({node_in=}, {node_out=}{description})"

    name: str
    directed: bool = False
    edges: dict[int, Edge] = field(default_factory=dict)
    
    def append(self, node_in: NodeType.Node, node_out: NodeType.Node) -> None:
        edge = self.Edge(node_in, node_out)
        self.edges[edge.edge_id] = edge

    def extend(self, nedges: Iterable[tuple[NodeType.Node, NodeType.Node]]) -> None:
        for edge in edges:
            if isinstance(edge, Edge):
                self.edges[edge.edge_id] = edge
            elif isinstance(edge, Iterable) and len(edge) == 2:
                self.append(edge[0], edge[1])
            else:
                raise ValueError("data must be 'Iterable[Edge]' or 'pair[Node, Node]'")


@dataclass(frozen=True, slots=True)
class Folder:
    name: str
    nodes: tuple["NodeType.Node | Folder"]


@dataclass(slots=True)
class FluoriteGraph:
    nodes: list[NodeType] = field(default_factory=list)
    edges: list[EdgeType] = field(default_factory=list)
    folders: list[Folder] = field(default_factory=list)

