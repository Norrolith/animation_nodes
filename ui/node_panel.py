import bpy
from bpy.props import *
from .. preferences import debuggingIsEnabled
from .. base_types.socket import AnimationNodeSocket

def draw(self, context):
    node = getattr(bpy.context, "active_node", None)
    if not getattr(node, "isAnimationNode", False): return
    layout = self.layout
    layout.separator()

    drawGenericNodeProperties(layout, node)
    drawSocketLists(layout, node)
    drawSocketVisibilityOperators(layout, node)

    if debuggingIsEnabled():
        layout.separator()
        layout.label("Identifier: " + node.identifier)

def drawGenericNodeProperties(layout, node):
    layout.prop(node, "width", text = "Width")

    col = layout.column(align = True)
    col.prop(node, "location", text = "X", index = 0)
    col.prop(node, "location", text = "Y", index = 1)

def drawSocketLists(layout, node):
    row = layout.row(align = True)

    size = max(len(node.inputs), len(node.outputs), 1)

    if len(node.inputs) > 0:
        col = row.column()
        subrow = col.row(align = True)
        subrow.label("Inputs")
        subrow.operator("an.move_input", text = "", icon = "TRIA_UP").moveUp = True
        subrow.operator("an.move_input", text = "", icon = "TRIA_DOWN").moveUp = False
        col.template_list("an_SocketUiList", "", node, "inputs", node, "activeInputIndex", rows = size, maxrows = size)

    if len(node.outputs) > 0:
        col = row.column()
        subrow = col.row(align = True)
        subrow.label("Outputs")
        subrow.operator("an.move_output", text = "", icon = "TRIA_UP").moveUp = True
        subrow.operator("an.move_output", text = "", icon = "TRIA_DOWN").moveUp = False
        col.template_list("an_SocketUiList", "", node, "outputs", node, "activeOutputIndex", rows = size, maxrows = size)

def drawSocketVisibilityOperators(layout, node):
    col = layout.column(align = True)
    col.label("Toogle Operation Visibility:")
    row = col.row(align = True)
    node.invokeFunction(row, "toogleTextInputVisibility", text = "Name")
    node.invokeFunction(row, "toogleMoveOperatorsVisibility", text = "Move")
    node.invokeFunction(row, "toogleRemoveOperatorVisibility", text = "Remove")
    node.invokeFunction(row, "disableSocketEditingInNode", icon = "FULLSCREEN")


class SocketUiList(bpy.types.UIList):
    bl_idname = "an_SocketUiList"

    def draw_item(self, context, layout, node, socket, icon, activeData, activePropname):
        if not isinstance(socket, AnimationNodeSocket):
            layout.label("No Animation Node Socket")
            return
        if socket.textProps.editable:
            layout.prop(socket, "text", emboss = False, text = "")
        else: layout.label(socket.getDisplayedName())

        if socket.removeable:
            socket.invokeFunction(layout, "remove", icon = "X", emboss = False)

        icon = "RESTRICT_VIEW_ON" if socket.hide else "RESTRICT_VIEW_OFF"
        layout.prop(socket, "hide", text = "", icon_only = True, icon = icon, emboss = False)


class MoveInputSocket(bpy.types.Operator):
    bl_idname = "an.move_input"
    bl_label = "Move Input"

    moveUp = BoolProperty()

    @classmethod
    def poll(cls, context):
        socket = getActiveSocket(isOutput = False)
        return getattr(socket, "moveable", False)

    def execute(self, context):
        return moveSocket(isOutput = False, moveUp = self.moveUp)

class MoveOutputSocket(bpy.types.Operator):
    bl_idname = "an.move_output"
    bl_label = "Move Output"

    moveUp = BoolProperty()

    @classmethod
    def poll(cls, context):
        socket = getActiveSocket(isOutput = True)
        return getattr(socket, "moveable", False)

    def execute(self, context):
        return moveSocket(isOutput = True, moveUp = self.moveUp)


def moveSocket(isOutput, moveUp):
    socket = getActiveSocket(isOutput)
    socket.moveInGroup(moveUp)

    node = socket.node
    if isOutput: node.activeOutputIndex = list(node.outputs).index(socket)
    else: node.activeInputIndex = list(node.inputs).index(socket)
    return {"FINISHED"}

def getActiveSocket(isOutput):
    node = bpy.context.active_node
    if node is None: return
    if isOutput: return node.activeOutputSocket
    else: return node.activeInputSocket



# Register
##################################

def register():
    bpy.types.NODE_PT_active_node_generic.append(draw)

def unregister():
    bpy.types.NODE_PT_active_node_generic.remove(draw)
