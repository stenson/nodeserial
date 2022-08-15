bl_info = {
    "name": "Nodeserial",
    "author": "Rob Stenson",
    "version": (0, 1),
    "blender": (3, 0, 0),
    "location": "NODE_EDITOR > Toolshelf",
    "description": "Node serialization",
    "warning": "",
    "wiki_url": "",
    "category": "Nodes",
}

import importlib
from pathlib import Path

if "bpy" in locals():
    # bpy.ops.scripts.reload() was called
    importlib.reload(io)
else:
    import bpy
    
    from nodeserial import io

import platform
def _os(): return platform.system()
def on_windows(): return _os() == "Windows"
def on_mac(): return _os() == "Darwin"
def on_linux(): return _os() == "Linux"


class NodeserialPropertiesGroup(bpy.types.PropertyGroup):
    json: bpy.props.StringProperty(name="JSON", default="", subtype="FILE_PATH")

class Nodeserial_OT_SerializeGeoNodes(bpy.types.Operator):
    bl_label = "Serialize Geo Nodes"
    bl_idname = "nodeserial.serialize_geo_nodes"
    
    def execute(self, context):
        io.serialize_geonodes(context.active_node)
        return {"FINISHED"}

class Nodeserial_OT_RealizeGeoNodes(bpy.types.Operator):
    bl_label = "Realize Geo Nodes"
    bl_idname = "nodeserial.realize_geo_nodes"
    
    def execute(self, context):
        io.deserialize_geonodes(context.scene.nodeserial.json)
        return {"FINISHED"}

class NodeserialMainPanel(bpy.types.Panel):
    bl_label = "Nodeserial"
    bl_idname = "NODESERIAL_PT_MAINPANEL"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "nodeserial"
    
    def draw(self, context):
        layout = self.layout
        layout.row().operator("nodeserial.serialize_geo_nodes")
        layout.row().separator()

        layout.row().prop(context.scene.nodeserial, "json")
        layout.row().operator("nodeserial.realize_geo_nodes")


classes = [
    NodeserialPropertiesGroup,
    Nodeserial_OT_SerializeGeoNodes,
    Nodeserial_OT_RealizeGeoNodes,
    NodeserialMainPanel,
]

def register():
    print("---nodeserial---", bl_info["version"])
    for cl in classes:
        bpy.utils.register_class(cl)
    
    bpy.types.Scene.nodeserial = bpy.props.PointerProperty(type=NodeserialPropertiesGroup, name="Nodeserial", description="Nodeserial deserialization settings")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)