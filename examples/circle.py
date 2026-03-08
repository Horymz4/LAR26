from robolab_turtlebot import Turtlebot, Rate, get_time

turtle = Turtlebot()
rate = Rate(10)

t = get_time()
pi = 3.1415926


while( get_time() - t < 24):
    if get_time() -t <4:
        lspeed = 0
        angspeed = -pi/4
    else:
        lspeed = 0.1
        angspeed = pi/10

    turtle.cmd_velocity(linear = lspeed, angular = angspeed)
    rate.sleep()
    
