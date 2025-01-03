import bpy

bl_info = {
    "name": "VRControllerCursor",
    "author": "Lightningbulb",
    "version": (0, 0, 3),
    "blender": (3, 3, 3),
    "description": "Adds support for VR controller object manipulation",
    "location": "View 3D N panel",
    "category": "3D View",
}

from bpy.types import Operator
from bpy.types import Panel
from bpy.props import IntProperty, FloatProperty
import mathutils
import math


### NOTE:
### object always refers to a blender object, and is a common category along with Mesh, and Materials
### classe names will reference what they interact with whether it is Objects, Meshes, or Materials. If they interact with a the addon itself it will start with the addonname



class OBJECT_OT_GrabObject(Operator):
    bl_idname = "object.grab_object"
    bl_label = "GrabObject"
    bl_options = {"REGISTER","UNDO"}


    #firstx = bpy.props.FloatProperty()
    #firsty = bpy.props.FloatProperty()
    #firstz = bpy.props.FloatProperty()

    #controllerfirstx = bpy.props.FloatProperty()
    #controllerfirsty = bpy.props.FloatProperty()
    #controllerfirstz = bpy.props.FloatProperty()
      
    
    def invoke(self, context, event):


        # I am using selected objects at index 0 because because blender still defines the last touched object as "active" and
        #  that might be poor user interaction if I use the simple "context.object"
        if context.selected_objects and (context.selected_objects)[0]:
            

            print(mathutils.Euler.to_quaternion(mathutils.Euler((bpy.types.calibrationx, bpy.types.calibrationy, bpy.types.calibrationz), "XYZ")))

            self.firstx = (context.selected_objects)[0].rotation_euler.x
            self.firsty = (context.selected_objects)[0].rotation_euler.y
            self.firstz = (context.selected_objects)[0].rotation_euler.z

            area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
            area.spaces[0].region_3d.view_rotation

            cameraPerspectiveDelta = mathutils.Quaternion(area.spaces[0].region_3d.view_rotation)

            calibrationQuaternion = mathutils.Euler.to_quaternion(mathutils.Euler((bpy.types.calibrationx, bpy.types.calibrationy, bpy.types.calibrationz), "XYZ"))

            


            controllerOrientation = mathutils.Quaternion(bpy.types.XrSessionState.controller_grip_rotation_get(bpy.context,0))

            #controllerOrientation.rotate(calibrationQuaternion.inverted())
            print("camera:" + str(cameraPerspectiveDelta))



            controllerOrientation.rotate(cameraPerspectiveDelta)


            self.controllerfirstx = mathutils.Quaternion.to_euler(controllerOrientation).x
            self.controllerfirsty = mathutils.Quaternion.to_euler(controllerOrientation).y
            self.controllerfirstz = mathutils.Quaternion.to_euler(controllerOrientation).z



            #print(mathutils.Euler((self.firstx, self.firsty, self.firstz),"XYZ"))
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "VRControllerCursor: No active object, could not finish")
            return {'CANCELLED'}


    def modal(self, context, event):
        
        
        # rotation the object started at
        objectstartingpos = mathutils.Euler.to_quaternion(mathutils.Euler((self.firstx, self.firsty, self.firstz),"XYZ"))



        # START controller's original rotation on button press
        controllerStart = mathutils.Euler.to_quaternion(mathutils.Euler((self.controllerfirstx, self.controllerfirsty, self.controllerfirstz),"XYZ"))
        # current controller rotation
        controllerquaternion = mathutils.Quaternion(bpy.types.XrSessionState.controller_grip_rotation_get(bpy.context,0))



        
        calibrationQuaternion = mathutils.Euler.to_quaternion(mathutils.Euler((bpy.types.calibrationx, bpy.types.calibrationy, bpy.types.calibrationz), "XYZ"))
 
        

        #controllerStart.rotate(calibrationQuaternion)



        
        # start at controller starting location
        controllerDelta = controllerStart.inverted()

        #controllerDelta.rotate(calibrationQuaternion.inverted())

        #controllerquaternion.rotate(calibrationQuaternion)

        # rotate vector to current controller position
        controllerDelta.rotate(controllerquaternion)

        

        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        area.spaces[0].region_3d.view_rotation

        viewportCameraOrientation = mathutils.Quaternion(area.spaces[0].region_3d.view_rotation)


        # correct for differing camera rotation
        controllerDelta.rotate(viewportCameraOrientation)

        print("controller delta:" + str(controllerDelta) + "(should be 1,0,0,0 on grab)")

        newObjectRotation = objectstartingpos
        newObjectRotation.rotate(controllerDelta)


        (context.selected_objects)[0].rotation_euler = mathutils.Quaternion.to_euler(newObjectRotation)


        if event.type == 'XR_ACTION':
            if (context.selected_objects)[0]:
                self.firstx = (context.selected_objects)[0].rotation_euler.x
                self.firsty = (context.selected_objects)[0].rotation_euler.y
                self.firstz = (context.selected_objects)[0].rotation_euler.z

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            (context.selected_objects)[0].rotation_euler.x = self.firstx
            (context.selected_objects)[0].rotation_euler.y = self.firsty
            (context.selected_objects)[0].rotation_euler.z = self.firstz    
            print("finished")        
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}




class OBJECT_OT_ControllerGrabListener(Operator):
    bl_idname = "object.controller_grab_listener"
    bl_label = "ControllerGrabListener"


    def invoke(self, context, event):
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        # Here you can handle some initialization code
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if not context.window_manager.controller_toggle:
            context.window_manager.event_timer_remove(self._timer)
            return {'FINISHED'}

        if event.type == 'XR_ACTION':  # Capture mouse movement
            print("XRPRESSED")
            bpy.ops.object.grab_object('INVOKE_DEFAULT')
        elif event.type == 'ESC':  # Capture exit events
            print("Cancelled")
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

class VRCC_PT_SettingsPanel(Panel):
    bl_idname = "VRCC_PT_Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "VRControllerCursor Settings"
    # ↓ this controls the name when the addon is selectable in the N-Panel menu
    bl_category = "VRControllerCursor"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        layout.label(text= "VR Session: ON" if bpy.types.XrSessionState.is_running(context) else " VR Session: OFF")

        controllerToggleButtonLabel = "Controller: ON" if context.window_manager.controller_toggle and bpy.types.XrSessionState.is_running(context) else "Controller: OFF"
        layout.prop(context.window_manager, 'controller_toggle', text= controllerToggleButtonLabel, toggle=True)

        # Draw a property for the persistent variable
        layout.operator(VRCC_OT_SetCalibrationPoint.bl_idname, text = VRCC_OT_SetCalibrationPoint.bl_label)
        

    


# Operator to set calibration rotation
class VRCC_OT_SetCalibrationPoint(bpy.types.Operator):
    bl_idname = "vrcc.setcalibrationpoint"
    bl_label = "calibrate"

    def execute(self, context):
     
        self.report({'INFO'}, "VRControllerCursor: Calibration orientation has been set")
        
        # If you need to trigger specific update functions manually, call them like this:
        update_CalibrationPointX(self, context)
        update_CalibrationPointY(self, context)
        update_CalibrationPointZ(self, context)

        print(bpy.types.calibrationx, bpy.types.calibrationy, bpy.types.calibrationz)

        return {'FINISHED'}


def update_function(self, context):
    if self.controller_toggle and bpy.types.XrSessionState.is_running(context):
        bpy.ops.object.controller_grab_listener('INVOKE_DEFAULT')
    else:
        self.controller_toggle = False
    return

def update_CalibrationPointX(self, context):
    bpy.types.calibrationx = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_grip_rotation_get(context,0))).x
    return 

def update_CalibrationPointY(self, context):
    bpy.types.calibrationy = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_grip_rotation_get(context,0))).y
    return

def update_CalibrationPointZ(self, context):
    bpy.types.calibrationz = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_grip_rotation_get(context,0))).z
    return
    


def register():
    classes = (VRCC_PT_SettingsPanel, 
               OBJECT_OT_ControllerGrabListener, 
               OBJECT_OT_GrabObject,
               VRCC_OT_SetCalibrationPoint)
    
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.WindowManager.controller_toggle = bpy.props.BoolProperty(
        name="Active_Controller", 
        description="toggle if any input from the controller will be monitored", 
        update= update_function,
        default = False)

    bpy.types.Scene.calibrationx = bpy.props.FloatProperty(
        name="calibrationx", 
        default=0,
        update=update_CalibrationPointX
    )

    bpy.types.Scene.calibrationy = bpy.props.FloatProperty(
        name="calibrationy",
        default=0,
        update=update_CalibrationPointY
    )
    bpy.types.Scene.calibrationz = bpy.props.FloatProperty(
        name="calibrationz", 
        default=0,
        update=update_CalibrationPointZ
    )
    

def unregister():

    classes = (VRCC_PT_SettingsPanel, 
               OBJECT_OT_ControllerGrabListener, 
               OBJECT_OT_GrabObject,
               VRCC_OT_SetCalibrationPoint)
    for c in classes:
        bpy.utils.unregister_class(c)

    del bpy.types.WindowManager.controller_toggle

    del bpy.types.Scene.calibrationx
    del bpy.types.Scene.calibrationy
    del bpy.types.Scene.calibrationz


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()