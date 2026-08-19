from dataclasses import dataclass, field
from itertools import count

_counter = count(1)

@dataclass(frozen=True, slots=True)
class Node:
    name: str
    id: int = field(default_factory=lambda: next(_counter))
    description: str | None = None


@dataclass(slots=True)
class NodeType:
    name: str
    nodes: list[Node] = field(default_factory=list)

    def __getitem__(self, name: str) -> Node:
        for node in self.nodes:
            if node.name == name:
                return node
        raise KeyError(f"Node {name!r} not found in {self.name!r}")


@dataclass(frozen=True, slots=True)
class Edge:
    node_in: Node
    node_out: Node
    description: str | int | None = None


@dataclass(slots=True)
class EdgeType:
    name: str
    directed: bool = False
    edges: list[Edge] = field(default_factory=list)


@dataclass(slots=True)
class Folder:
    name: str
    nodes: list["Node | Folder"]


@dataclass(slots=True)
class FluoriteGraph:
    nodes: list[NodeType] = field(default_factory=list)
    edges: list[EdgeType] = field(default_factory=list)
    folders: list[Folder] = field(default_factory=list)

