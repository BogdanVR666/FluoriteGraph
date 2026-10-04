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

    _name: str
    nodes: dict[int, Node] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self._name

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
        node_in: int
        node_out: int
        description: str | None = None
        edge_id: int = field(default_factory=lambda: next(_counter))

        def __repr__(self):
            node_in = self.node_in
            node_out = self.node_out
            description = f", '{self.description}'" if self.description else ""
            return f"Edge({node_in=}, {node_out=}{description})"

    _name: str
    directed: bool = False
    edges: dict[int, Edge] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self._name
    
    def append(self, node_in: int, node_out: int) -> None:
        edge = self.Edge(node_in, node_out)
        self.edges[edge.edge_id] = edge

    def extend(self, edges: Iterable[tuple[int, int]]) -> None:
        for edge in edges:
            if isinstance(edge, EdgeType.Edge):
                self.edges[edge.edge_id] = edge
            elif isinstance(edge, Iterable) and len(edge) == 2:
                self.append(edge[0], edge[1])
            else:
                raise ValueError("data must be 'Iterable[Edge]' or 'pair[int, int]'")


@dataclass(slots=True)
class Hyperedge:
    name: str
    description: str | None = None
    children: set[int] = field(default_factory=set)
    hyperedge_id: int = field(default_factory=lambda: next(_counter))
    owner: "FluoriteGraph | None" = field(default=None, compare=False, repr=False)

    def append(self, child_id: int) -> None:
        if child_id == self.hyperedge_id or (
            self.owner is not None and self.owner._reaches(child_id, self.hyperedge_id)
        ):
            raise ValueError(f"Adding {child_id} to {self.hyperedge_id} creates a cycle")
        self.children.add(child_id)

    def extend(self, children: Iterable[int]) -> None:
        for child_id in children:
            self.append(child_id)


@dataclass(slots=True)
class FluoriteGraph:
    nodes: dict[str, NodeType] = field(default_factory=dict)
    edges: dict[str, EdgeType] = field(default_factory=dict)
    hyperedges: dict[int, Hyperedge] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.nodes, dict):
            self.nodes = {node_type.name: node_type for node_type in self.nodes}
        if not isinstance(self.edges, dict):
            self.edges = {edge_type.name: edge_type for edge_type in self.edges}
        hyperedges = self.hyperedges.values() if isinstance(self.hyperedges, dict) else self.hyperedges
        self.hyperedges = {}
        self.hyperextend(hyperedges)

    def hyperadd(self, hyperedge: Hyperedge) -> None:
        for child_id in hyperedge.children:
            if child_id == hyperedge.hyperedge_id or self._reaches(child_id, hyperedge.hyperedge_id):
                raise ValueError(f"Adding {hyperedge.hyperedge_id} creates a cycle through {child_id}")
        hyperedge.owner = self
        self.hyperedges[hyperedge.hyperedge_id] = hyperedge

    def hyperextend(self, hyperedges: Iterable[Hyperedge]) -> None:
        for hyperedge in hyperedges:
            self.hyperadd(hyperedge)

    def _reaches(self, start: int, target: int) -> bool:
        stack, seen = [start], set()
        while stack:
            current = stack.pop()
            if current == target:
                return True
            if current in seen or current not in self.hyperedges:
                continue
            seen.add(current)
            stack.extend(self.hyperedges[current].children)
        return False
