from FluoriteGraph import FluoriteGraph, NodeType, EdgeType, Folder

def main():
    filenames = ["hello.py", "myclass.py", "exec.py"]
    files = NodeType("файли")
    files.extend(filenames)

    classes = NodeType("класси")
    classes.append("MyClass")

    method_names = ["method1", "method2"]    
    methods = NodeType("методи")
    methods.extend(method_names)

    imports = EdgeType("імпортує", directed=True)
    uses = EdgeType("використовує", directed=True)

    imports.append(files["hello.py"], files["myclass.py"])
    uses.append(files["hello.py"], methods["method1"])

    graph = FluoriteGraph(
        nodes=[files, classes, methods], 
        edges=[imports, uses], 
        folders=[Folder("src", [files["myclass.py"]])]
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
#             nodes={
#                 1: Node(name='hello.py'), 
#                 2: Node(name='myclass.py'), 
#                 3: Node(name='exec.py')
#             }
#         ), 
#         NodeType(
#             name='класси', 
#             nodes={
#                 4: Node(name='MyClass')
#             }
#         ), 
#         NodeType(
#             name='методи', 
#             nodes={
#                 5: Node(name='method1'), 
#                 6: Node(name='method2')
#             }
#         )
#     ], 
#     edges=[
#         EdgeType(
#             name='імпортує', 
#             directed=True, 
#             edges={
#                 7: Edge(
#                     node_in=Node(name='hello.py'), 
#                     node_out=Node(name='myclass.py'), 
#                 )
#             }
#         ), 
#         EdgeType(
#             name='використовує', 
#             directed=True, 
#             edges={
#                 8: Edge(
#                     node_in=Node(name='hello.py'), 
#                     node_out=Node(name='method1'),
#                 )
#             }
#         )
#     ], 
#     folders=[
#         Folder(
#             name='src', 
#             nodes=[Node(name='myclass.py')]
#         )
#     ]
# )
