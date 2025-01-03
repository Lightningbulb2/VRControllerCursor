import bpy
import numpy as np

bl_info = {
    "name": "VRControllerCursor",
    "author": "Lightningbulb",
    "version": (0, 0, 2),
    "blender": (3, 3, 3),
    "description": "Adds support for VR controller object manipulation",
    "location": "View 3D N panel",
    "category": "3D View",
}

from bpy.types import Operator
from bpy.types import Panel
from bpy.props import IntProperty, FloatProperty
import mathutils



class ObjectGrabOperator(bpy.types.Operator):
    bl_idname = "track.modal"
    bl_label = "Track object to controller"

    objectGrabbed = False
    controllerActive = False

    def __init__(self):
        super().__init__()
        self.objectGrabbed = False
        self.controllerActive = bpy.types.WindowManager.controller_active

    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        print("modal active")
        return {'RUNNING_MODAL'}
       


    def modal(self, context, event):

        if self.controllerActive == False:
            print("modal cancelled")
            return {'CANCELLED'}

        if event.type == 'XR_ACTION':  # Capture VR controller press
            #self.report({'INFO'},"XRPRESSED")
            print("controller pressed")
            self.objectGrabbed = True

        if self.objectGrabbed == True:
            #try:

            if (context.selected_objects)[0]:
                self.firstx = (context.selected_objects)[0].rotation_euler.x
                self.firsty = (context.selected_objects)[0].rotation_euler.y
                self.firstz = (context.selected_objects)[0].rotation_euler.z
            else:
                self.report({'WARNING'}, "No active object, could not finish")

            controllerquaternion = mathutils.Quaternion(bpy.types.XrSessionState.controller_aim_rotation_get(bpy.context,0))


            startingpos = mathutils.Euler.to_quaternion(mathutils.Euler((self.firstx, self.firsty, self.firstz),"XYZ"))

        


            ## SO If this is ".rotation_euler it pops around every time I grab the object and let go, but cancelling returns it properly"
            ## if it's ".delta_rotation_euler" then it stops cancelling properly, but it stops popping around if I grab and let go constantly, 
            # BUT it doesnt care if I'm holding it, it seems to remember where I was OH BECAUSE I NEED A RELATIVE QUATERNION NOT AN ABSOLUTE FOR THE CHANGE
            (context.selected_objects)[0].rotation_euler = mathutils.Quaternion.to_euler(controllerquaternion.rotation_difference(startingpos))
            #mathutils.Quaternion.to_euler(mathutils.Quaternion(q_final))
                                                            

            #except:
                #self.report({'INFO'},"select an object first")
                #return {'CANCELLED'}


            if event.type == 'XR_ACTION':
                if (context.selected_objects)[0]:
                    self.firstx = (context.selected_objects)[0].rotation_euler.x
                    self.firsty = (context.selected_objects)[0].rotation_euler.y
                    self.firstz = (context.selected_objects)[0].rotation_euler.z
                self.objectGrabbed = False

            elif event.type in {'RIGHTMOUSE', 'ESC'}:
                self.objectGrabbed = False

            return {'RUNNING_MODAL'}
        
        return {'PASS_THROUGH'}
        
    







class SettingsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_label = "VRControllerCursor"
    bl_region_type = "UI"
    bl_category = "VRControllerCursor"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        label = "Controller: ON" if context.window_manager.controller_active else "Controller: OFF"
        self.layout.prop(context.window_manager, 'controller_active', text=label, toggle=True)
        #layout.prop(scene, "controller_toggle", text="Active Controller")


        layout.operator(ObjectGrabOperator.bl_idname, text=ObjectGrabOperator.bl_label)



def update_function(self, context):
    if self.controller_active:
        bpy.ops.track.modal('INVOKE_DEFAULT')
    return



def register():

    bpy.utils.register_class(ObjectGrabOperator)

    bpy.utils.register_class(SettingsPanel)
    

    bpy.types.WindowManager.controller_active = bpy.props.BoolProperty(
        name="Active_Controller", 
        description="toggle if any input from the controller will be monitored", 
        update= update_function,
        default = False)
    

def unregister():
    del bpy.types.WindowManager.controller_active
    bpy.utils.unregister_class(ObjectGrabOperator)
    bpy.utils.unregister_class(SettingsPanel)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()