# VRControllerCursor
VRControllerCursor (VRCC) is an addon designed to speedup 3d manipulation in blender by adding transform capability to VR controllers


Project started 2024/12/30

# Finished

2025/1/4
calibration corrected rotation implemented

2025/1/20
variable influence for rotation with trigger implemented

2025/1/26
rebuilt rotation system to use bpy.ops.transform.rotate() instead of manually setting rotation myself. (This adds full rotation compatibility to all different interaction types)


### TODO

• fix horrendous lag caused by the transform.rotate() in a modal()

• make the controller listener run more reliably

• add user bindable keybinds

• add location transformations

• add proper Euler mode that preserves rotation changes, not just orientation

• figure out how to run controllers completely without HMD

• consider re-working how rotation is input because of how the OpenXR standard handles pivot points on controllers of different shapes

openXR rotation issues from 2 years ago
https://youtu.be/g-zupOaJ6dI
(they aren't offset to always be at everyone's hand, just the center of the controller)

possible solution:
https://x.com/SadlyItsBradley/status/1821996412982452313
