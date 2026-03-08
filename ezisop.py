def go_to_origin(turtle):
    print("Returning to origin...")
    
    while not StateofBumper.is_set():
        # Get current odometry
        odom = turtle.get_odometry() # returns [x, y, yaw]
        x, y, yaw = odom[0], odom[1], odom[2]
        
        # Calculate distance to origin
        distance = np.sqrt(x**2 + y**2)
        # Calculate angle to origin
        angle_to_target = np.arctan2(-y, -x)
        # Error in heading
        angle_error = angle_to_target - yaw
        
        # Normalize angle error to [-pi, pi]
        angle_error = (angle_error + np.pi) % (2 * np.pi) - np.pi

        # Stopping condition
        if distance < 0.05: # 5cm tolerance
            print("Reached origin!")
            turtle.cmd_velocity(0, 0)
            break
            
        # P-controller constants (tune these if robot wobbles)
        lin_k = 0.2 
        ang_k = 0.8
        
        # If angle error is large, rotate in place first
        if abs(angle_error) > 0.2:
            turtle.cmd_velocity(linear=0, angular=ang_k * angle_error)
        else:
            # Move forward and adjust heading simultaneously
            turtle.cmd_velocity(linear=lin_k * distance, angular=ang_k * angle_error) 
