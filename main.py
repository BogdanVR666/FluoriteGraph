from FluoriteGraph import Edge, EdgeType, FluoriteGraph, Folder, Node, NodeType

def main():
    files = NodeType(
        "файли", 
        [
            Node("hello.py"),
            Node("myclass.py"),
            Node("exec.py"),
        ]
    )
    
    classes = NodeType("класси", [Node("MyClass"),])
    
    methods = NodeType(
        "методи", 
        [
            Node("method1"),
            Node("method2"),
        ]
    )

    imports = EdgeType("імпортує", directed=True)
    uses = EdgeType("використовує", directed=True)

    imports.edges.append(Edge(files["hello.py"], files["myclass.py"]))
    uses.edges.append(Edge(files["hello.py"], methods["method1"]))

    graph = FluoriteGraph(
        nodes=[
            files, 
            classes, 
            methods,
        ], 
        edges=[
            imports, 
            uses,
        ], 
        folders=[
            Folder("src", [files["myclass.py"],])
        ]
    )
    print(graph)

if __name__ == "__main__":
    main()

# RESULT:
#
# FluoriteGraph(
#     nodes=[
#         NodeType(
#             name='файли', 
#             nodes=[
#                 Node(
#                     name='hello.py', 
#                     id=1, 
#                     description=None
#                 ), 
#                 Node(
#                     name='myclass.py', 
#                     id=2, 
#                     description=None
#                 ), 
#                 Node(
#                     name='exec.py', 
#                     id=3, 
#                     description=None
#                 )
#             ]
#         ), 
#         NodeType(
#             name='класси', 
#             nodes=[
#                 Node(
#                     name='MyClass', 
#                     id=4, 
#                     description=None
#                 )
#             ]
#         ), 
#         NodeType(
#             name='методи', 
#             nodes=[
#                 Node(
#                     name='method1', 
#                     id=5, 
#                     description=None
#                 ), 
#                 Node(
#                     name='method2', 
#                     id=6, 
#                     description=None
#                 )
#             ]
#         )
#     ], 
#     edges=[
#         EdgeType(
#             name='імпортує', 
#             directed=True, 
#             edges=[
#                 Edge(
#                     node_in=Node(name='hello.py', id=1, description=None), 
#                     node_out=Node(name='myclass.py', id=2, description=None), 
#                     description=None
#                 )
#             ]
#         ), 
#         EdgeType(
#             name='використовує', 
#             directed=True, 
#             edges=[
#                 Edge(
#                     node_in=Node(name='hello.py', id=1, description=None), 
#                     node_out=Node(name='method1', id=5, description=None), 
#                     description=None
#                 )
#             ]
#         )
#     ], 
#     folders=[
#         Folder(
#             name='src', 
#             nodes=[
#                 Node(name='myclass.py', id=2, description=None)
#             ]
#         )
#     ]
# )
