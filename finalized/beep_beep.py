import time
import numpy as np
from robolab_turtlebot import Rate
from threading_variables import vision_lock, vision_data


# Distance calculator ---------------------------------
def get_bottom_half_distance(pc):
    if pc is None:
        return None

    h = pc.shape[0]
    bottom = pc[h // 2:, :, :]
    z = bottom[:, :, 2]

    mask = np.isfinite(z) & (z >= 0)
    if np.count_nonzero(mask) == 0:
        return None
    with vision_lock:
        vision_data["g_dist"] = float(np.mean(z[mask]))


# Parking state ---------------------------------------
class ParkController:
    def __init__(self, stop_dist=0.51, sound=True):
        self.stop_dist = stop_dist
        self.sound = sound

    # Beeping parametres ------------------------------
        self.START_BEEP = 0.7
        self.END_BEEP = stop_dist
        self.MIN_INTERVAL = 0.1
        self.MAX_INTERVAL = 1.0

        self.last_beep = 0.0

    def step(self, turtle):

        # Handles one step of parking -----------------
        # True = parked, False = continue -------------

        dist = None
        with vision_lock:
            dist = vision_data["g_dist"]

        if dist is None:
            return False

        # Control of parking --------------------------
        if dist < self.stop_dist:
            turtle.cmd_velocity(linear=0.0)
            return True

        # Beeping -------------------------------------
        if self.sound and self.END_BEEP <= dist <= self.START_BEEP:

            delta_beep = self.START_BEEP - self.END_BEEP
            scale = (self.START_BEEP - dist) / delta_beep
            scale = np.clip(scale, 0.0, 1.0)

            interval_range = self.MAX_INTERVAL - self.MIN_INTERVAL
            interval = self.MIN_INTERVAL + (1 - scale) * interval_range

            now = time.time()
            if now - self.last_beep >= interval:
                turtle.play_sound(2)
                self.last_beep = now

        # Forward movement ----------------------------
        turtle.cmd_velocity(linear=0.1, angular=0)
        return False

    def park(self, turtle):
        rate = Rate(20)
        while True:
            done = self.step(turtle)
            if done:
                print("Zaparkováno!")
                break
            rate.sleep()
