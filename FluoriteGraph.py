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
            description = f", '{self.description}'" if self.description else ""
            return f"Edge({node_in=}, {node_out=}{description})"

    name: str
    directed: bool = False
    edges: dict[int, Edge] = field(default_factory=dict)
    
    def append(self, node_in: NodeType.Node, node_out: NodeType.Node) -> None:
        edge = self.Edge(node_in, node_out)
        self.edges[edge.edge_id] = edge

    def extend(self, edges: Iterable[tuple[NodeType.Node, NodeType.Node]]) -> None:
        for edge in edges:
            if isinstance(edge, EdgeType.Edge):
                self.edges[edge.edge_id] = edge
            elif isinstance(edge, Iterable) and len(edge) == 2:
                self.append(edge[0], edge[1])
            else:
                raise ValueError("data must be 'Iterable[Edge]' or 'pair[Node, Node]'")


@dataclass(slots=True)
class HyperedgeType:
    @dataclass(frozen=True, slots=True)
    class Hyperedge:
        name: str
        description: str | None = None
        hyperedge_id: int = field(default_factory=lambda: next(_counter))

    hyperedges: dict[int, Hyperedge] = field(default_factory=dict)
    children: dict[int, set[int]] = field(default_factory=dict)

    def append(self, hyperedge: Hyperedge) -> None:
        self.hyperedges[hyperedge.hyperedge_id] = hyperedge
        self.children[hyperedge.hyperedge_id] = set()

    def add(self, hyperedge_id: int, child_id: int) -> None:
        if child_id == hyperedge_id or self._reaches(child_id, hyperedge_id):
            raise ValueError(f"Adding {child_id} to {hyperedge_id} creates a cycle")
        self.children[hyperedge_id].add(child_id)

    def _reaches(self, start: int, target: int) -> bool:
        # вершини - листки, тому обходимо лише гіперребра
        stack, seen = [start], set()
        while stack:
            current = stack.pop()
            if current == target:
                return True
            if current in seen:
                continue
            seen.add(current)
            stack.extend(self.children.get(current, ()))
        return False


@dataclass(slots=True)
class FluoriteGraph:
    nodes: dict[str, NodeType] = field(default_factory=dict)
    edges: dict[str, EdgeType] = field(default_factory=dict)
    hyperedges: HyperedgeType = field(default_factory=HyperedgeType)

    def __post_init__(self):
        # дозволяє передавати списки: FluoriteGraph(nodes=[files, classes])
        if not isinstance(self.nodes, dict):
            self.nodes = {node_type.name: node_type for node_type in self.nodes}
        if not isinstance(self.edges, dict):
            self.edges = {edge_type.name: edge_type for edge_type in self.edges}

    def hyperadd(self, hyperedge: HyperedgeType.Hyperedge) -> None:
        self.hyperedges.append(hyperedge)
