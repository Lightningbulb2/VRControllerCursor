import bpy
from bpy.types import Operator, Panel

class TEST_OT_modal_operator(Operator):
    bl_idname = "test.modal"
    bl_label = "Demo modal operator"

    def modal(self, context, event):
        if not context.window_manager.test_toggle:
            context.window_manager.event_timer_remove(self._timer)
            print("done")
            return {'FINISHED'}
        print("pass through")
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        context.window_manager.modal_handler_add(self)
        print("modal")
        return {'RUNNING_MODAL'} 

class TEST_PT_side_panel(Panel):
    """This is the parent of the whole mess"""
    bl_label = "TEST panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "TEST"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        label = "Operator ON" if context.window_manager.test_toggle else "Operator OFF"
        self.layout.prop(context.window_manager, 'test_toggle', text=label, toggle=True)  

def update_function(self, context):
    print("invoke modal")
    if self.test_toggle:
        bpy.ops.test.modal('INVOKE_DEFAULT')
    return

classes = [
    TEST_PT_side_panel,
    TEST_OT_modal_operator,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.test_toggle = bpy.props.BoolProperty(
         default = False,
         update = update_function
    )

def unregister():
    del bpy.types.WindowManager.test_toggle
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == '__main__':
    register()