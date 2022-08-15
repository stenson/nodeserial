import bpy
from pathlib import Path
from json import loads, dumps

GEO_NODE_FIELDS = ["data_type", "mode", "operation", "input_type"]

def serialize_geonodes(group):
    #ng = bpy.data.node_groups[group_name]
    ng = group.node_tree
    nodes = []

    #if isinstance(ng, bpy.types.GeometryNodeGroup):
    name = ng.name
    for n in ng.nodes:
        nr = dict(
            type=str(type(n).__name__),
            name=n.name,
            location=(n.location[0], n.location[1]),
            inputs=[],
            outputs=[])
        
        nodes.append(nr)

        for gnf in GEO_NODE_FIELDS:
            if hasattr(n, gnf):
                nr[gnf] = getattr(n, gnf)

        for idx, o in enumerate(n.outputs):
            rec = dict(name=o.name, type=type(o).__name__)
            nr["outputs"].append(rec)
            if hasattr(o, "default_value"):
                v = o.default_value
                if not isinstance(v, bpy.types.Object):                        
                    try:
                        vs = [x for x in v]
                    except:
                        vs = v
                    rec["value"] = vs

        for idx, i in enumerate(n.inputs):
            rec = dict(name=i.name, type=type(i).__name__)
            nr["inputs"].append(rec)
            if i.is_linked:
                rec["links"] = []
                for l in i.links:
                    rec["links"].append(dict(
                        src=[l.from_node.name, l.from_socket.name, l.from_socket.path_from_id()],
                        dst=l.to_socket.name))
            else:
                if hasattr(i, "default_value"):
                    v = i.default_value
                    try:
                        vs = [x for x in v]
                    except:
                        vs = v
                    rec["value"] = vs
        
        #for idx, o in enumerate(n.outputs):
        #    nr["outputs"].append(dict(name=o.name, type=type(o).__name__))

    output = dict(name=name, nodes=nodes)
    #from pprint import pformat
    #Path(f"{name}.py").write_text(pformat(output))

    Path(f"output/{name}.json").write_text(dumps(output, indent=2))

def deserialize_geonodes(json_path):
    data = loads(Path(json_path).read_text())
    nodes = data["nodes"]
    
    nodes_name = data["name"]
    try:
        ng = bpy.data.node_groups[nodes_name]
    except KeyError:
        ng = bpy.data.node_groups.new(type="GeometryNodeTree", name=nodes_name)
    
    ng.inputs.clear()
    ng.outputs.clear()

    for node in ng.nodes:
        ng.nodes.remove(node)
    
    for node in nodes:
        nn = ng.nodes.new(type=node["type"])
        nn.name = node["name"]
        nn.label = nn.name
        nn.location = node["location"]

        if isinstance(nn, bpy.types.NodeGroupInput):
            for o in node["outputs"][:]:
                if o["name"]:
                    ng.inputs.new(o["type"], o["name"])
        elif isinstance(nn, bpy.types.NodeGroupOutput):
            for o in node["inputs"][:]:
                if o["name"]:
                    ng.outputs.new(o["type"], o["name"])
        else:
            for gnf in GEO_NODE_FIELDS:
                if gnf in node:
                    setattr(nn, gnf, node[gnf])
            
            for idx, no in enumerate(node["outputs"]):
                if "value" in no:
                    vs = no["value"]
                    try:
                        for vdx, v in enumerate(vs):
                            nn.outputs[idx][vdx].default_value = v
                    except:
                        nn.outputs[idx].default_value = vs

    for node in nodes:
        nn = ng.nodes[node["name"]]
        for idx, ni in enumerate(node["inputs"]):
            if "value" in ni:
                vs = ni["value"]
                try:
                    for vdx, v in enumerate(vs):
                        nn.inputs[idx][vdx].default_value = v
                except:
                    nn.inputs[idx].default_value = vs

    for nidx, node in enumerate(nodes):
        nn = ng.nodes[node["name"]]
        for idx, ni in enumerate(node["inputs"]):
            if "links" in ni:
                for ldx, nl in enumerate(ni["links"]):
                    src_path = nl["src"][2]
                    #src_node = ng.nodes[nl["src"][0]]
                    #src = src_node.outputs[nl["src"][1]]
                    src = eval(f"ng.{src_path}")
                    dst = nn.inputs[idx]
                    ng.links.new(src, dst)