import threading

# Event threading variables ---------------------------
Button_press = threading.Event()
StateofBumper = threading.Event()
garage_stage = threading.Event()
outgarage_stage = threading.Event()
odometry_stage = threading.Event()
see_garage = threading.Event()
ending_stage = threading.Event()
processing_image = threading.Event()

# Data from camera ------------------------------------
vision_data = {"pos":None, "radius":None, "avg_x":None, "dist":None}
vision_lock = threading.Lock()
