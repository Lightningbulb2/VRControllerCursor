import bpy

bl_info = {
    "name": "VRControllerCursor",
    "author": "Lightningbulb",
    "version": (0, 0, 5),
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

        if context.selected_objects:
            self.grabType = (context.selected_objects)[0]
            print("object type")

        if context.selected_pose_bones:
            self.grabType = context.selected_pose_bones[0]
            print("pose bone type")

        # I am using selected objects at index 0 because because blender still defines the last touched object as "active" and
        #  that might be poor user interaction if I use the simple "context.object"
        if self.grabType:

        #NOTE:2025/1/21 you might notice all the rotations are broken down into their components, the original reasoning was that only primitives would carry between cycles (I gotta test that)    
        
            ##### ROTATION
            
            self.firstRotationx = self.grabType.rotation_euler.x
            self.firstRotationy = self.grabType.rotation_euler.y
            self.firstRotationz = self.grabType.rotation_euler.z
                


            area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
            area.spaces[0].region_3d.view_rotation

            viewportCameraOrientation = mathutils.Quaternion(area.spaces[0].region_3d.view_rotation)

            calibrationOrientation = mathutils.Euler.to_quaternion(mathutils.Euler((bpy.types.calibrationRotationx, bpy.types.calibrationRotationy, bpy.types.calibrationRotationz), "XYZ"))
            
            
            controllerOrientation = mathutils.Quaternion(bpy.types.XrSessionState.controller_grip_rotation_get(bpy.context,0))

            # initialize "last modal orientation". It's used for variable trigger influence
            self.lastModalRotationx = mathutils.Quaternion.to_euler(controllerOrientation).x
            self.lastModalRotationy = mathutils.Quaternion.to_euler(controllerOrientation).y
            self.lastModalRotationz = mathutils.Quaternion.to_euler(controllerOrientation).z

            self.compoundRotationOffsetx = mathutils.Quaternion.to_euler(controllerOrientation).x
            self.compoundRotationOffsety = mathutils.Quaternion.to_euler(controllerOrientation).y
            self.compoundRotationOffsetz = mathutils.Quaternion.to_euler(controllerOrientation).z

            print("calibration on invoke:" + str(calibrationOrientation))

            
            # calibration correct the orientation
            controllerOrientation.rotate(calibrationOrientation.inverted())


            # camera correct the orientation
            controllerOrientation.rotate(viewportCameraOrientation)
            

            self.controllerfirstRotationx = mathutils.Quaternion.to_euler(controllerOrientation).x
            self.controllerfirstRotationy = mathutils.Quaternion.to_euler(controllerOrientation).y
            self.controllerfirstRotationz = mathutils.Quaternion.to_euler(controllerOrientation).z
            #### ROTATION

            #### LOCATION
            controllerLocation = bpy.types.XrSessionState.controller_grip_location_get(bpy.context,0)


            print(controllerLocation)


            ### LOCATION




            #print(mathutils.Euler((self.firstx, self.firsty, self.firstz),"XYZ"))
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "VRControllerCursor: No active object, could not finish")
            return {'CANCELLED'}


    def modal(self, context, event):
        
        
        calibrationOrientation = mathutils.Euler.to_quaternion(mathutils.Euler((bpy.types.calibrationRotationx, bpy.types.calibrationRotationy, bpy.types.calibrationRotationz), "XYZ"))
        
        # current controller rotation
        currentControllerOrientation = mathutils.Quaternion(bpy.types.XrSessionState.controller_grip_rotation_get(bpy.context,0))

        lastUpdateOrientation = mathutils.Euler.to_quaternion(mathutils.Euler((self.lastModalRotationx, self.lastModalRotationy, self.lastModalRotationz), "XYZ"))

        
    


        deltaSinceTriggerEvent = lastUpdateOrientation.inverted()
        deltaSinceTriggerEvent.rotate(currentControllerOrientation)



        triggerPressure = context.window_manager.xr_session_state.action_state_get(context, "blender_default","teleport", "/user/hand/left")[0]

        identityquat = mathutils.Quaternion((1,0,0,0))


        #get this cycle's delta using the trigger as an interpolation facture (0 is no change, 1 is rotate by full delta this cycle)
        triggerAdjustedDelta = identityquat.slerp(deltaSinceTriggerEvent,triggerPressure)




        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        area.spaces[0].region_3d.view_rotation

        viewportCameraOrientation = mathutils.Quaternion(area.spaces[0].region_3d.view_rotation)

   
        #controllerDelta.rotate(
        orient = calibrationOrientation.inverted()



        # correct for differing camera rotation
        orient.rotate(viewportCameraOrientation)

        orientmatrix = orient.to_matrix()



        self.lastModalRotationx = mathutils.Quaternion.to_euler(currentControllerOrientation).x
        self.lastModalRotationy = mathutils.Quaternion.to_euler(currentControllerOrientation).y
        self.lastModalRotationz = mathutils.Quaternion.to_euler(currentControllerOrientation).z


       
        #TODO MAKE THIS EFFICIENT it causes a lot of lag
        bpy.ops.transform.rotate(value=triggerAdjustedDelta.to_euler().x, orient_axis='X', orient_type='VIEW', orient_matrix=(orientmatrix), orient_matrix_type='VIEW', constraint_axis=(True, False, False))
        bpy.ops.transform.rotate(value=triggerAdjustedDelta.to_euler().y, orient_axis='Y', orient_type='VIEW', orient_matrix=(orientmatrix), orient_matrix_type='VIEW', constraint_axis=(False, True, False))
        bpy.ops.transform.rotate(value=triggerAdjustedDelta.to_euler().z, orient_axis='Z', orient_type='VIEW', orient_matrix=(orientmatrix), orient_matrix_type='VIEW', constraint_axis=(False, False, True))
      

        ### LOCATION STUFF




        

        # finishing and cancelling
        if context.window_manager.xr_session_state.action_state_get(context, "blender_default","teleport", "/user/hand/left")[0] < 0.15 and context.window_manager.xr_session_state.action_state_get(context, "blender_default","nav_grab", "/user/hand/left")[0] < 0.15:

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.grabType.rotation_euler.x = self.firstRotationx
            self.grabType.rotation_euler.y = self.firstRotationy
            self.grabType.rotation_euler.z = self.firstRotationz    
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

        """
        
        actionMap = bpy.types.XrActionMaps.new(context.window_manager.xr_session_state, "vrcc_actions", True)

        
        grab_rotate_action = context.window_manager.xr_session_state.actionmaps.find(context.window_manager.xr_session_state, "vrcc_actions").actionmap_items.new("grip_rotate", True)
        context.window_manager.xr_session_state.action_create(context, actionMap, grab_rotate_action)


        #context.window_manager.xr_session_state.actionmaps.find(context.window_manager.xr_session_state, "vrcc_actions").actionmap_items.new()

        #grab_locate_action = bpy.types.XrActionMapItems.new("grip_rotate", True)
        #context.window_manager.xr_session_state.action_create(context, actionMap, grab_locate_action)

        #pose_calibration_action = bpy.types.XrActionMapItems.new("pose_calibrate", True)
        #context.window_manager.xr_session_state.action_create(context, actionMap, pose_calibration_action)


        context.window_manager.xr_session_state.action_set_create(context, actionMap)

        
        trigger_binding = context.window_manager.xr_session_state.actionmaps.find(context.window_manager.xr_session_state, "vrcc_actions").actionmap_items.find("grip_rotate").bindings.new("trigger", True)
        context.window_manager.xr_session_state.actionmaps.find(context.window_manager.xr_session_state, "vrcc_actions").actionmap_items.find("grip_rotate").bindings.find("trigger").profile = "/interaction_profiles/oculus/touch_controller"
        context.window_manager.xr_session_state.actionmaps.find(context.window_manager.xr_session_state, "vrcc_actions").actionmap_items.find("grip_rotate").bindings.find("trigger").component_paths.new("/user/hand/left/input/grip/pose")
        
        #bpy.types.XrActionMapBindings.new(bpy.types.XrComponentPaths.new("/user/hand/left/input/grip/pose"))
        context.window_manager.xr_session_state.action_binding_create(context, actionMap, grab_rotate_action, trigger_binding)
        

        #context.window_manager.xr_session_state.action
        #context.window_manager.xr_session_state.active_action_set_set

        #grip_binding = bpy.types.XrActionMapBindings.new(bpy.types.XrComponentPaths.new("/user/hand/left/input/grip/pose"))
        #bpy.types.XrSessionState.action_binding_create(context, actionMap, grab_locate_action, grip_binding)

        #x_button_binding = bpy.types.XrActionMapBindings.new("xbutton")
        #bpy.types.XrSessionState.action_binding_create(context, actionMap, pose_calibration_action, x_button_binding)
        
        """
  

        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if not context.window_manager.controller_toggle:
            context.window_manager.event_timer_remove(self._timer)
            return {'FINISHED'}
        
        ##TODO figure out if I should use custom binding stuff
        if event.xr and (event.xr.action == "teleport" or event.xr.action == "nav_grab"):
            print("XRPRESSED")
            bpy.ops.object.grab_object('INVOKE_DEFAULT')

        elif event.xr and event.xr.action == "nav_reset":
            bpy.ops.vrcc.setcalibrationpoint("INVOKE_DEFAULT")
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

        layout.operator(OBJECT_OT_GrabObject.bl_idname, text="grab selected object")
        
    


# Operator to set calibration rotation
class VRCC_OT_SetCalibrationPoint(bpy.types.Operator):
    bl_idname = "vrcc.setcalibrationpoint"
    bl_label = "calibrate"

    def execute(self, context):
     
        self.report({'INFO'}, "VRControllerCursor: Calibration orientation has been set")
        
        # If you need to trigger specific update functions manually, call them like this:
        update_CalibrationRotationPointX(self, context)
        update_CalibrationRotationPointY(self, context)
        update_CalibrationRotationPointZ(self, context)

        return {'FINISHED'}


def update_function(self, context):
    if self.controller_toggle and bpy.types.XrSessionState.is_running(context):
        bpy.ops.object.controller_grab_listener('INVOKE_DEFAULT')
    elif self.controller_toggle:
        self.controller_toggle = False
    return

def update_CalibrationRotationPointX(self, context):
    bpy.types.calibrationRotationx = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_grip_rotation_get(context,0))).x - (math.pi/2)
    return 

def update_CalibrationRotationPointY(self, context):
    bpy.types.calibrationRotationy = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_grip_rotation_get(context,0))).y
    return

def update_CalibrationRotationPointZ(self, context):
    bpy.types.calibrationRotationz = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_grip_rotation_get(context,0))).z
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

    bpy.types.Scene.calibrationRotationx = bpy.props.FloatProperty(
        name="calibrationRotationx", 
        default=0,
        update=update_CalibrationRotationPointX
    )

    bpy.types.Scene.calibrationRotationy = bpy.props.FloatProperty(
        name="calibrationRotationy",
        default=0,
        update=update_CalibrationRotationPointY
    )
    bpy.types.Scene.calibrationRotationz = bpy.props.FloatProperty(
        name="calibrationRotationz", 
        default=0,
        update=update_CalibrationRotationPointZ
    )
    

def unregister():

    classes = (VRCC_PT_SettingsPanel, 
               OBJECT_OT_ControllerGrabListener, 
               OBJECT_OT_GrabObject,
               VRCC_OT_SetCalibrationPoint)
    for c in classes:
        bpy.utils.unregister_class(c)

    del bpy.types.WindowManager.controller_toggle

    del bpy.types.Scene.calibrationRotationx
    del bpy.types.Scene.calibrationRotationy
    del bpy.types.Scene.calibrationRotationz


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()