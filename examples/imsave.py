from __future__ import print_function

import sys
import string
from robolab_turtlebot import Turtlebot

from imageio import imwrite

turtle = Turtlebot(rgb=True)
i = 0
while(True):
    turtle.wait_for_rgb_image()
    print(turtle.get_rgb_K())
    input()
    rgb = turtle.get_rgb_image()
    
    filename = f'image + {i} + .png'
    i += 1
    
    print(f'Image saved as {filename}')
    imwrite(filename, rgb)
