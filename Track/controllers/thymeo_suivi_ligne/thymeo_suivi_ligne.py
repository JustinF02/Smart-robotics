from controller import Robot

robot = Robot()
timestep = int(robot.getBasicTimeStep())

left_sensor = robot.getDevice('prox.ground.0')
right_sensor = robot.getDevice('prox.ground.1')
left_sensor.enable(timestep)
right_sensor.enable(timestep)

left_motor = robot.getDevice('motor.left')
right_motor = robot.getDevice('motor.right')
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

max_speed = 4.0
turn_speed = 3.0

threshold = 800

while robot.step(timestep) != -1:
    left_val = left_sensor.getValue()
    right_val = right_sensor.getValue()

    print(f"[DEBUG] Left sensor: {left_val:.2f}, Right sensor: {right_val:.2f}")

    if left_val < threshold and right_val < threshold:
        print("Status: On line, move forward")
        left_motor.setVelocity(max_speed)
        right_motor.setVelocity(max_speed)
    elif left_val < threshold:
        print("Status: Line detected on left, turn left")
        left_motor.setVelocity(turn_speed)
        right_motor.setVelocity(max_speed)
    elif right_val < threshold:
        print("Status: Line detected on right, turn right")
        left_motor.setVelocity(max_speed)
        right_motor.setVelocity(turn_speed)
    else:
        print("Status: Line lost, searching")
        left_motor.setVelocity(turn_speed)
        right_motor.setVelocity(-turn_speed)
