import bpy
import numpy as np

bl_info = {
    "name": "VRControllerCursor",
    "author": "Lightningbulb",
    "version": (0, 0, 1),
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


    #object2 = bpy.context.selected_objects

    #object2[0].rotation_mode = 'QUATERNION'

    #first_location = None
    #first_rotation = None

    
    #def __init__(self):
        #self.firstx = None
        #self.firsty = None
        #self.firstz = None


    #buttonx = None
    #buttony = None
    #buttonz = None

    
    
    def invoke(self, context, event):
        if (context.selected_objects)[0]:
            self.firstx = (context.selected_objects)[0].rotation_euler.x
            self.firsty = (context.selected_objects)[0].rotation_euler.y
            self.firstz = (context.selected_objects)[0].rotation_euler.z

            #self.buttonx = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_aim_rotation_get(bpy.context,0))).x
            #self.buttony = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_aim_rotation_get(bpy.context,0))).y
            #self.buttonz = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_aim_rotation_get(bpy.context,0))).z

            #bpy.types.XrSessionState.controller_aim_rotation_get(bpy.context,0)

            print(mathutils.Euler((self.firstx, self.firsty, self.firstz),"XYZ"))
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}


    def modal(self, context, event):



        
        #try:

        controllerquaternion = mathutils.Quaternion(bpy.types.XrSessionState.controller_aim_rotation_get(bpy.context,0))

        #relativedifference = controllerquaternion.rotation_difference(mathutils.Euler.to_quaternion(mathutils.Euler((self.buttonx, self.buttony, self.buttonz),"XYZ")))

        startingpos = mathutils.Euler.to_quaternion(mathutils.Euler((self.firstx, self.firsty, self.firstz),"XYZ"))

        
        #(context.selected_objects)[0].rotation_euler = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_aim_rotation_get(bpy.context,0))*delta)
        """
        def quaternion_inverse(q):
            # Returns the inverse (conjugate) of a quaternion
            return np.array([q[0], -q[1], -q[2], -q[3]])

        def quaternion_multiply(q1, q2):
            # Multiplies two quaternions (q1 * q2)
            w1, x1, y1, z1 = q1
            w2, x2, y2, z2 = q2
            return np.array([
                w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
                w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
            ])

        # Calculate relative rotation
        q_start_inv = quaternion_inverse(startingpos)
        q_relative = quaternion_multiply(delta, q_start_inv)

        # Calculate final quaternion
        q_final = quaternion_multiply(startingpos, q_relative)

        """


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

                #self.buttonx = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_aim_rotation_get(bpy.context,0))).x
                #self.buttony = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_aim_rotation_get(bpy.context,0))).y
                #self.buttonz = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_aim_rotation_get(bpy.context,0))).z
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            (context.selected_objects)[0].rotation_euler.x = self.firstx
            (context.selected_objects)[0].rotation_euler.y = self.firsty
            (context.selected_objects)[0].rotation_euler.z = self.firstz            
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}




class ControllerGrabListener(bpy.types.Operator):
    bl_idname = "buttonlistener.modal"
    bl_label = "Function 1"
    
    


    def invoke(self, context, event):
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        # Here you can handle some initialization code
        context.window_manager.modal_handler_add(self)
        #num = 0
        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if not context.window_manager.controller_toggle:
            context.window_manager.event_timer_remove(self._timer)
            return {'FINISHED'}

        if event.type == 'XR_ACTION':  # Capture mouse movement
            self.report({'INFO'},"XRPRESSED")
            bpy.ops.track.modal('INVOKE_DEFAULT')
        elif event.type == 'ESC':  # Capture exit events
            print("Cancelled")
            return {'CANCELLED'}

        return {'PASS_THROUGH'}


class SettingsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_label = "VRControllerCursor"
    bl_region_type = "UI"
    bl_category = "VRControllerCursor"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        label = "Controller: ON" if context.window_manager.controller_toggle else "Controller: OFF"
        self.layout.prop(context.window_manager, 'controller_toggle', text=label, toggle=True)
        #layout.prop(scene, "controller_toggle", text="Active Controller")

        layout.operator(ControllerGrabListener.bl_idname)

        layout.operator(ObjectGrabOperator.bl_idname, text=ObjectGrabOperator.bl_label)



def update_function(self, context):
    if self.controller_toggle:
        bpy.ops.buttonlistener.modal('INVOKE_DEFAULT')
    return



def register():

    bpy.utils.register_class(ObjectGrabOperator)

    bpy.utils.register_class(SettingsPanel)
    
    bpy.utils.register_class(ControllerGrabListener)

    bpy.types.WindowManager.controller_toggle = bpy.props.BoolProperty(
        name="Active_Controller", 
        description="toggle if any input from the controller will be monitored", 
        update= update_function,
        default = False)
    

def unregister():
    del bpy.types.WindowManager.controller_toggle
    bpy.utils.unregister_class(ObjectGrabOperator)
    bpy.utils.unregister_class(ControllerGrabListener)
    bpy.utils.unregister_class(SettingsPanel)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()