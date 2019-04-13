from vehicle.skills.skills.base import Skill
from .api_patches import Axis
from .api_patches import get_input_axis_value


class Pano(Skill):
    """
    Simply spin in place, with yaw and pitch controled by vertical sliders


    This example shows how to re-purpose the existing UI controls to serve a different purpose.
    """

    def __init__(self):
        super(Pano, self).__init__()

    def get_onscreen_controls(self, api):
        """
        Determine what messaging to show and controls to enable based on state.
        """
        controls = {}
        controls['drag_enabled'] = False
        controls['tap_targets_enabled'] = False
        controls['double_tap_enabled'] = False
        controls['steering_enabled'] = False

        # Enable the two sliders
        controls['height_slider_enabled'] = True  # left slider
        controls['zoom_slider_enabled'] = True  # right slider
        # NOTE: Unfortunately the "height" and "zoom" labels in the UI cannot be changed from here
        return controls

    def update(self, api):
        """
        Periodically update the state machine based on api changes.
        """
        # Turn off the automatic phone controls; we will do it ourselves.
        api.phone.disable_movement_commands()

        # Get the current values for the vertical sliders.
        left_slider = get_input_axis_value(api.phone, Axis.UP, default=0.0)
        right_slider = get_input_axis_value(api.phone, Axis.FORWARD, default=0.0)

        # Update movement controls
        api.movement.set_heading_rate(left_slider)
        api.movement.set_gimbal_pitch(right_slider)

        # Force the screen to redraw.
        self.set_needs_layout()
