import bpy
from ... base_types.node import AnimationNode
from ... events import propertyChanged

class ViewportColorNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ViewportColorNode"
    bl_label = "Viewport Color"

    inputNames = { "Color" : "color" }
    outputNames = {}

    materialName = bpy.props.StringProperty(update = propertyChanged)

    def create(self):
        self.inputs.new("mn_ColorSocket", "Color")

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'materialName', bpy.data, 'materials', text='', icon='MATERIAL_DATA')

    def execute(self, color):
        material = bpy.data.materials.get(self.materialName)
        if material is None: return

        try: material.diffuse_color = color[:3]
        except: pass