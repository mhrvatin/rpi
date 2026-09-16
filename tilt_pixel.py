# How hard a full 1g tilt accelerates the ball, in pixels/sec^2. Tuned by
# feel on the 8x8 display; adjust if the ball feels too sluggish or too
# skittish on the real hardware.
ACCEL_GAIN = 60.0

# Velocity is multiplied by this every step, so the ball settles down again
# once the Pi is level instead of coasting forever. Also tuned by feel.
FRICTION = 0.9

def initial_state(size=8):
    center = (size - 1) / 2

    return {"x": center, "y": center, "vx": 0.0, "vy": 0.0}

def clamp_to_edge(position, velocity, size=8):
    """Stop the ball dead at an edge instead of letting it run past it."""
    low, high = 0.0, size - 1

    if position < low:
        return low, 0.0

    if position > high:
        return high, 0.0

    return position, velocity

def step(state, accel, dt, size=8):
    """Advance the ball by `dt` seconds under the given tilt.

    `accel` is the dict get_accelerometer_raw() returns, in g. x positive
    is a tilt to the right, y positive is a tilt forward, both of which
    accelerate the ball downhill along that axis. Flip either sign below if
    the ball rolls the wrong way for how the HAT is mounted.
    """
    vx = (state["vx"] + accel["x"] * ACCEL_GAIN * dt) * FRICTION
    vy = (state["vy"] + -accel["y"] * ACCEL_GAIN * dt) * FRICTION

    x = state["x"] + vx * dt
    y = state["y"] + vy * dt

    x, vx = clamp_to_edge(x, vx, size)
    y, vy = clamp_to_edge(y, vy, size)

    return {"x": x, "y": y, "vx": vx, "vy": vy}

def pixel_position(state):
    return int(round(state["x"])), int(round(state["y"]))
