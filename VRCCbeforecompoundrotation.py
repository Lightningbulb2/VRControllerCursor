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
            
           

            self.firstRotationx = (context.selected_objects)[0].rotation_euler.x
            self.firstRotationy = (context.selected_objects)[0].rotation_euler.y
            self.firstRotationz = (context.selected_objects)[0].rotation_euler.z

            self.compoundRotationOffsetx = 0
            self.compoundRotationOffsety = 0
            self.compoundRotationOffsetz = 0

            area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
            area.spaces[0].region_3d.view_rotation

            viewportCameraOrientation = mathutils.Quaternion(area.spaces[0].region_3d.view_rotation)

            calibrationOrientation = mathutils.Euler.to_quaternion(mathutils.Euler((bpy.types.calibrationx, bpy.types.calibrationy, bpy.types.calibrationz), "XYZ"))
            

            controllerOrientation = mathutils.Quaternion(bpy.types.XrSessionState.controller_grip_rotation_get(bpy.context,0))

            # initialize "last modal orientation". It's used for variable trigger influence
            self.lastModalRotationx = mathutils.Quaternion.to_euler(controllerOrientation).x
            self.lastModalRotationy = mathutils.Quaternion.to_euler(controllerOrientation).y
            self.lastModalRotationz = mathutils.Quaternion.to_euler(controllerOrientation).z

   

            print("calibration on invoke:" + str(calibrationOrientation))

            
            # calibration correct the orientation
            controllerOrientation.rotate(calibrationOrientation.inverted())


            # camera correct the orientation
            controllerOrientation.rotate(viewportCameraOrientation)

            

            self.controllerfirstRotationx = mathutils.Quaternion.to_euler(controllerOrientation).x
            self.controllerfirstRotationy = mathutils.Quaternion.to_euler(controllerOrientation).y
            self.controllerfirstRotationz = mathutils.Quaternion.to_euler(controllerOrientation).z


            self.lastTriggerPressure = context.window_manager.xr_session_state.action_state_get(context, "blender_default","teleport", "/user/hand/left")[0]

            #print(mathutils.Euler((self.firstx, self.firsty, self.firstz),"XYZ"))
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "VRControllerCursor: No active object, could not finish")
            return {'CANCELLED'}


    def modal(self, context, event):
        
        
        calibrationOrientation = mathutils.Euler.to_quaternion(mathutils.Euler((bpy.types.calibrationx, bpy.types.calibrationy, bpy.types.calibrationz), "XYZ"))
        
        # rotation the object started at
        objectstartingpos = mathutils.Euler.to_quaternion(mathutils.Euler((self.firstRotationx, self.firstRotationy, self.firstRotationz),"XYZ"))



        # START controller's original rotation on button press
        controllerStartOrientation = mathutils.Euler.to_quaternion(mathutils.Euler((self.controllerfirstRotationx, self.controllerfirstRotationy, self.controllerfirstRotationz),"XYZ"))
        # current controller rotation
        currentControllerOrientation = mathutils.Quaternion(bpy.types.XrSessionState.controller_grip_rotation_get(bpy.context,0))

        lastUpdateOrientation = mathutils.Euler.to_quaternion(mathutils.Euler((self.lastModalRotationx, self.lastModalRotationy, self.lastModalRotationz), "XYZ"))

        
    



        
        # start at controller starting location
        controllerDelta = controllerStartOrientation.inverted()





        # rotate vector to current controller position
        controllerDelta.rotate(currentControllerOrientation)

        deltaSinceTriggerEvent = lastUpdateOrientation.inverted()
        deltaSinceTriggerEvent.rotate(currentControllerOrientation)



        triggerPressure = context.window_manager.xr_session_state.action_state_get(context, "blender_default","teleport", "/user/hand/left")[0]

        #triggerPressure = 0.2


        triggerOffset = mathutils.Euler.to_quaternion(mathutils.Euler((self.compoundRotationOffsetx, self.compoundRotationOffsety, self.compoundRotationOffsetz), "XYZ"))
      #  print("cumulative Delta: " + str(triggerOffset))

        # TODO change update method to change ONLY instead of reverse offsetting it in this weird way
        triggerAdjustedDelta = deltaSinceTriggerEvent.inverted().slerp(deltaSinceTriggerEvent,triggerPressure/2)

       # print("slerped: " + str(triggerAdjustedDelta))

        triggerOffset.rotate(triggerAdjustedDelta)
        
        controllerDelta.rotate(triggerOffset)
      #  print("update delta: " + str(deltaSinceTriggerEvent))
     
        #TODO FIX messed up perspective correction when trigger is < 1 for longer periods of time (causing the offset to do funky stuff)
        
        



        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        area.spaces[0].region_3d.view_rotation

        viewportCameraOrientation = mathutils.Quaternion(area.spaces[0].region_3d.view_rotation)


   
        controllerDelta.rotate(calibrationOrientation.inverted())

        # correct for differing camera rotation
        controllerDelta.rotate(viewportCameraOrientation)

        

        newObjectRotation = objectstartingpos
        newObjectRotation.rotate(controllerDelta)


        self.lastModalRotationx = mathutils.Quaternion.to_euler(currentControllerOrientation).x
        self.lastModalRotationy = mathutils.Quaternion.to_euler(currentControllerOrientation).y
        self.lastModalRotationz = mathutils.Quaternion.to_euler(currentControllerOrientation).z
        self.lastTriggerPressure = triggerPressure

        self.compoundRotationOffsetx = mathutils.Quaternion.to_euler(triggerOffset).x
        self.compoundRotationOffsety = mathutils.Quaternion.to_euler(triggerOffset).y
        self.compoundRotationOffsetz = mathutils.Quaternion.to_euler(triggerOffset).z


        (context.selected_objects)[0].rotation_euler = mathutils.Quaternion.to_euler(newObjectRotation)

        
        if context.window_manager.xr_session_state.action_state_get(context, "blender_default","teleport", "/user/hand/left")[0] < 0.15 and context.window_manager.xr_session_state.action_state_get(context, "blender_default","nav_grab", "/user/hand/left")[0] < 0.15:
            if (context.selected_objects)[0]:
                self.firstRotationx = (context.selected_objects)[0].rotation_euler.x
                self.firstRotationy = (context.selected_objects)[0].rotation_euler.y
                self.firstRotationz = (context.selected_objects)[0].rotation_euler.z

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            (context.selected_objects)[0].rotation_euler.x = self.firstRotationx
            (context.selected_objects)[0].rotation_euler.y = self.firstRotationy
            (context.selected_objects)[0].rotation_euler.z = self.firstRotationz    
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
        
        #TODO figure out why this action isn't being detected
        if event.xr and (event.xr.action == "teleport" or event.xr.action == "nav_grab"):
            #print(event.xr.float_threshold)
        #if event.xr and event.xr.action == 'grip_rotate':
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
        update_CalibrationPointX(self, context)
        update_CalibrationPointY(self, context)
        update_CalibrationPointZ(self, context)

        print(bpy.types.calibrationx, bpy.types.calibrationy, bpy.types.calibrationz)

        return {'FINISHED'}


def update_function(self, context):
    if self.controller_toggle and bpy.types.XrSessionState.is_running(context):
        bpy.ops.object.controller_grab_listener('INVOKE_DEFAULT')
    elif self.controller_toggle:
        self.controller_toggle = False
    return

def update_CalibrationPointX(self, context):
    bpy.types.calibrationx = mathutils.Quaternion.to_euler(mathutils.Quaternion(bpy.types.XrSessionState.controller_grip_rotation_get(context,0))).x - (math.pi/2)
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