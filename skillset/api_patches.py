"""
Helper functions that will eventually be added to the official api in some form.

Or alternate implementations that address bugs in the originals.
"""
import numpy as np

from lcmtypes.skills import ui_input_axis_t as Axis


# TODO(matt): fix the phone API
def safe_get_key(phone_api, key):
    # This queries the variables without mutating it if the key is not set
    # This appears to be a problem because movement_t complains about None values.
    return phone_api.variables.vars.get(key)


def get_input_axis_value(phone_api, axis, default=None):
    """
    Get the value for an active input axis, if active.

    Returns:
        (float | None): the current value
    """
    inputs = phone_api.ui_inputs
    if inputs is None:
        return default

    for joystick_axis in inputs.joysticks:
        if joystick_axis.axis == axis:
            return joystick_axis.value

    return default


# TODO(matt): add this to the phone API
def get_tap_ray(api):
    start = api.phone.ray_tracer._ray_start
    end = api.phone.ray_tracer._ray_end
    if start is None or end is None:
        return None
    ray = end - start
    length = np.linalg.norm(ray)
    return ray / length


# NOTE(matt): this just returns the result of a typical double tap and is limited to 7 meters.
def get_focus_position(api):
    return api.phone.ray_tracer._focus_position

